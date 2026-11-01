#!/usr/bin/env python3
"""Prepare documented M-SpectraCast CSV exports without altering source data.

Python 3.11+; standard library only. Verifies the release manifest, removes only
empty unnamed columns, normalizes timestamp text, and preserves observation
order and measurement strings. Local-clock regressions are reported, not sorted.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import statistics
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from zipfile import BadZipFile, ZipFile


ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@contextmanager
def csv_source(path: Path, member: str | None):
    if member is None:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            yield stream
    else:
        with ZipFile(path) as archive:
            # Read only the manifest's exact member; never extract archive paths.
            with archive.open(member) as binary:
                with io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as stream:
                    yield stream


def prepare(entry: dict, input_dir: Path, output_dir: Path) -> dict:
    source = input_dir / entry["file"]
    output = output_dir / (entry["id"].replace("-", "") + ".csv")
    if source.resolve() == output.resolve():
        raise ValueError("Choose a separate output directory; source files must not be overwritten.")
    if sha256(source) != entry["sha256"]:
        raise ValueError(f"{entry['file']}: SHA-256 differs from the release manifest.")

    output_dir.mkdir(parents=True, exist_ok=True)
    rows = 0
    first = last = minimum = maximum = None
    gaps = []
    regressions = []
    seen = set()
    fd, temporary_name = tempfile.mkstemp(prefix=output.name + ".", suffix=".tmp", dir=output_dir)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as destination:
            writer = csv.writer(destination, lineterminator="\n")
            with csv_source(source, entry["archive_member"]) as stream:
                reader = csv.reader(stream)
                header = [value.strip() for value in next(reader)]
                if header[0] != entry["timestamp_column"]:
                    raise ValueError(f"{entry['file']}: unexpected timestamp column.")
                indices = [i for i in range(1, len(header)) if header[i]]
                unnamed = [i for i in range(1, len(header)) if not header[i]]
                if [header[i] for i in indices] != entry["channel_labels"]:
                    raise ValueError(f"{entry['file']}: channel labels/order differ from the manifest.")
                writer.writerow(["timestamp"] + entry["channel_labels"])
                for row in reader:
                    line = reader.line_num
                    if len(row) != len(header):
                        raise ValueError(f"{entry['file']}:{line}: unexpected number of fields.")
                    if any(row[i].strip() for i in unnamed):
                        raise ValueError(f"{entry['file']}:{line}: an unnamed column contains data.")
                    current = datetime.strptime(row[0], entry["timestamp_format"])
                    if current in seen:
                        raise ValueError(f"{entry['file']}:{line}: duplicate local timestamp.")
                    seen.add(current)
                    values = [row[i] for i in indices]
                    for raw in values:
                        value = float(raw)
                        if not math.isfinite(value) or value < 0:
                            raise ValueError(f"{entry['file']}:{line}: invalid field magnitude.")
                    if last is not None:
                        seconds = (current - last).total_seconds()
                        if seconds < 0:
                            regressions.append({"source_csv_line": line, "previous": last.isoformat(), "current": current.isoformat()})
                        elif seconds > 0:
                            gaps.append(seconds)
                    first = current if first is None else first
                    minimum = current if minimum is None else min(minimum, current)
                    maximum = current if maximum is None else max(maximum, current)
                    last = current
                    rows += 1
                    writer.writerow([current.isoformat()] + values)
        if rows != entry["rows"]:
            raise ValueError(f"{entry['file']}: {rows} rows differ from the release manifest.")
        if minimum.isoformat() != entry["timestamp_min"] or maximum.isoformat() != entry["timestamp_max"]:
            raise ValueError(f"{entry['file']}: date coverage differs from the release manifest.")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    median = statistics.median(gaps) if gaps else None
    paper = entry["paper_reported"]
    return {
        "dataset": entry["id"],
        "source_file": source.name,
        "source_sha256": entry["sha256"],
        "output_file": output.name,
        "output_sha256": sha256(output),
        "rows": rows,
        "channels": len(indices),
        "units": entry["units"],
        "timestamp_min": minimum.isoformat(),
        "timestamp_max": maximum.isoformat(),
        "timestamp_timezone": None,
        "source_row_order_preserved": True,
        "removed_empty_unnamed_columns": len(unnamed),
        "local_clock_regressions": regressions,
        "positive_interval_min_seconds": min(gaps) if gaps else None,
        "positive_interval_median_seconds": median,
        "positive_interval_max_seconds": max(gaps) if gaps else None,
        "gaps_over_one_hour": sum(gap > 3600 for gap in gaps),
        "paper_rows": paper["readings_per_channel"],
        "paper_row_count_matches": rows == paper["readings_per_channel"],
        "note": "No timezone was inferred, no rows were sorted, and no values were interpolated, resampled, or normalized.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["all", "ED-2022", "UH-2022", "ED-2024", "UH-2024"], default="all")
    parser.add_argument("--input-dir", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data" / "processed")
    args = parser.parse_args(argv)
    manifest = json.loads((ROOT / "data" / "dataset_manifest.json").read_text(encoding="utf-8"))
    entries = [item for item in manifest["datasets"] if args.dataset == "all" or item["id"] == args.dataset]
    reports = []
    try:
        for entry in entries:
            report = prepare(entry, args.input_dir, args.output_dir)
            reports.append(report)
            print(f"{report['dataset']}: {report['rows']:,} rows x {report['channels']} channels; "
                  f"{len(report['local_clock_regressions'])} local-clock regression(s).")
    except (ValueError, OSError, KeyError, StopIteration, csv.Error, UnicodeError, BadZipFile) as exc:
        print(f"Preparation failed: {exc}", file=sys.stderr)
        return 2
    report_file = args.output_dir / ("preparation_report.json" if args.dataset == "all" else args.dataset + "_preparation_report.json")
    report_file.write_text(json.dumps({"manifest_source_commit": manifest["source_commit"], "datasets": reports}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {report_file.name}. Originals were preserved. See docs/DATA_QUALITY.md before time-based analysis.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

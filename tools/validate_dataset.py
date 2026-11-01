#!/usr/bin/env python3
"""Validate the optional M-SpectraCast wide/long CSV exchange schemas.

No measurements are changed, interpolated, resampled, or normalized. This tool
validates interchange files, not model execution or numerical reproduction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import sys
from datetime import datetime
from pathlib import Path


class ValidationError(ValueError):
    """An invalid CSV schema, timestamp, or measurement was found."""


def numeric(raw: str, label: str, line: int) -> float:
    try:
        value = float(raw)
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"Line {line}: {label} is not numeric: {raw!r}") from exc
    if not math.isfinite(value):
        raise ValidationError(f"Line {line}: {label} must be finite, got {raw!r}")
    return value


def timestamp(raw: str, time_format: str | None, line: int) -> datetime:
    try:
        if time_format:
            return datetime.strptime(raw.strip(), time_format)
        return datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(
            f"Line {line}: invalid timestamp {raw!r}; use ISO 8601 or --time-format."
        ) from exc


def check_time(previous: datetime | None, current: datetime, line: int, allow_local_clock_regressions: bool = False) -> bool:
    if previous is None:
        return False
    if (previous.utcoffset() is None) != (current.utcoffset() is None):
        raise ValidationError(f"Line {line}: mixed timezone-aware and naive timestamps.")
    if current < previous:
        if allow_local_clock_regressions and current.utcoffset() is None:
            return True
        raise ValidationError(f"Line {line}: timestamps are not chronological.")
    return False


def check_value(raw: str, unit: str, line: int) -> float:
    value = numeric(raw, "measurement", line)
    if unit == "V/m" and value < 0:
        raise ValidationError(f"Line {line}: electric-field magnitude in V/m is negative.")
    return value


def validate(
    path: str | Path,
    *,
    unit: str,
    file_format: str = "wide",
    timestamp_column: str = "timestamp",
    frequency_column: str = "frequency_mhz",
    value_column: str = "value",
    time_format: str | None = None,
    allow_local_clock_regressions: bool = False,
) -> dict:
    path = Path(path)
    if unit not in {"V/m", "dBm", "standardized"}:
        raise ValidationError("Unit must be V/m, dBm, or standardized.")
    if file_format not in {"wide", "long"}:
        raise ValidationError("Format must be wide or long.")

    first = last = None
    gaps: list[float] = []
    expected_channels: set[float] | None = None
    channel_order: list[float] = []
    current_channels: set[float] = set()
    observations = 0
    csv_rows = 0
    clock_regressions: list[dict] = []

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        try:
            header = [column.strip() for column in next(reader)]
        except StopIteration as exc:
            raise ValidationError("The CSV file is empty.") from exc
        if not header or any(not column for column in header):
            raise ValidationError("Column names must be nonempty.")
        if len(header) != len(set(header)):
            raise ValidationError("Duplicate column names are not allowed.")
        if timestamp_column not in header:
            raise ValidationError(f"Missing timestamp column: {timestamp_column!r}.")
        time_index = header.index(timestamp_column)

        if file_format == "wide":
            value_indices = [i for i in range(len(header)) if i != time_index]
            if not value_indices:
                raise ValidationError("A wide CSV must have at least one frequency channel.")
            channel_order = [numeric(header[i], "frequency header in MHz", 1) for i in value_indices]
            if any(f <= 0 for f in channel_order) or len(set(channel_order)) != len(channel_order):
                raise ValidationError("Frequency headers must be positive and numerically unique.")
            expected_channels = set(channel_order)
        else:
            required = {timestamp_column, frequency_column, value_column}
            if len(required) != 3 or set(header) != required:
                raise ValidationError(
                    "A long CSV must have exactly three distinct columns: "
                    f"{timestamp_column}, {frequency_column}, {value_column}."
                )
            frequency_index = header.index(frequency_column)
            value_index = header.index(value_column)

        for row in reader:
            line = reader.line_num
            if len(row) != len(header):
                raise ValidationError(f"Line {line}: expected {len(header)} fields, got {len(row)}.")
            csv_rows += 1
            current = timestamp(row[time_index], time_format, line)
            if check_time(last, current, line, allow_local_clock_regressions):
                clock_regressions.append({"csv_line": line, "previous": last.isoformat(), "current": current.isoformat()})

            if file_format == "wide":
                if last is not None and current == last:
                    raise ValidationError(f"Line {line}: duplicate observation timestamp.")
                for i in value_indices:
                    check_value(row[i], unit, line)
                observations += 1
            else:
                frequency = numeric(row[frequency_index], "frequency in MHz", line)
                if frequency <= 0:
                    raise ValidationError(f"Line {line}: frequency must be positive.")
                check_value(row[value_index], unit, line)
                if last is not None and current != last:
                    if expected_channels is None:
                        expected_channels = set(current_channels)
                        channel_order = sorted(expected_channels)
                    elif current_channels != expected_channels:
                        raise ValidationError(
                            f"Line {line}: the preceding timestamp has an incomplete or changed channel set."
                        )
                    current_channels.clear()
                if frequency in current_channels:
                    raise ValidationError(f"Line {line}: duplicate timestamp-frequency pair.")
                current_channels.add(frequency)
                if last is None or current != last:
                    observations += 1

            if first is None:
                first = current
            if last is not None and current > last:
                gaps.append((current - last).total_seconds())
            last = current

    if observations == 0:
        raise ValidationError("The CSV contains a header but no observations.")
    if file_format == "long":
        if expected_channels is None:
            expected_channels = set(current_channels)
            channel_order = sorted(expected_channels)
        elif current_channels != expected_channels:
            raise ValidationError("The final timestamp has an incomplete or changed channel set.")

    warnings: list[str] = []
    if clock_regressions:
        warnings.append(f"{len(clock_regressions)} local-clock regression(s) allowed explicitly; row order is preserved and timezone interpretation remains unresolved.")
    if first.utcoffset() is None:
        warnings.append("Timezone is unspecified; preserve and document the source convention.")
    if len(gaps) == 0:
        warnings.append("Only one observation; sampling intervals cannot be assessed.")
        interval = None
    else:
        median = statistics.median(gaps)
        interval = {
            "min_seconds": min(gaps),
            "median_seconds": median,
            "max_seconds": max(gaps),
            "gaps_above_twice_median": sum(gap > 2 * median for gap in gaps),
        }
        if max(gaps) - min(gaps) > 1:
            warnings.append("Intervals vary by more than one second; this is not a verified regular grid.")

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)

    return {
        "status": "valid_with_warnings" if warnings else "valid",
        "filename": path.name,
        "sha256": digest.hexdigest(),
        "bytes": path.stat().st_size,
        "format": file_format,
        "unit_as_declared": unit,
        "csv_data_rows": csv_rows,
        "observations": observations,
        "channels": len(expected_channels),
        "frequencies_mhz": channel_order,
        "first_timestamp": first.isoformat(),
        "last_timestamp": last.isoformat(),
        "sampling_intervals": interval,
        "local_clock_regressions": clock_regressions,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="CSV file; never modified")
    parser.add_argument("--unit", choices=["V/m", "dBm", "standardized"], required=True)
    parser.add_argument("--format", dest="file_format", choices=["wide", "long"], default="wide")
    parser.add_argument("--allow-local-clock-regressions", action="store_true", help="Report and permit regressions only for timezone-naive local clocks; does not resolve timezone or reorder rows")
    parser.add_argument("--timestamp-column", default="timestamp")
    parser.add_argument("--frequency-column", default="frequency_mhz")
    parser.add_argument("--value-column", default="value")
    parser.add_argument("--time-format", help="datetime.strptime format; default is ISO 8601")
    args = vars(parser.parse_args(argv))
    try:
        result = validate(**args)
    except (ValidationError, OSError, UnicodeError, csv.Error, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

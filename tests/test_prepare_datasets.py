"""Ensure preparation preserves data and handles the actual export quirks."""

import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "prepare_datasets.py"
spec = importlib.util.spec_from_file_location("dataset_preparer", MODULE_PATH)
preparer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preparer)


class DatasetPreparationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.root = Path(self.folder.name)
        self.source = self.root / "ED2024.csv"
        self.source.write_text("date,763,773,,\n29/10/2023 02:56:15,0.1000,0.2000,,\n29/10/2023 02:03:47,0.3000,0.4000,,\n", encoding="utf-8")
        self.entry = {
            "id": "ED-2024", "file": self.source.name, "archive_member": None,
            "sha256": preparer.sha256(self.source), "timestamp_column": "date",
            "timestamp_format": "%d/%m/%Y %H:%M:%S", "channel_labels": ["763", "773"],
            "rows": 2, "units": "V/m", "timestamp_min": "2023-10-29T02:03:47",
            "timestamp_max": "2023-10-29T02:56:15", "paper_reported": {"readings_per_channel": 3},
        }

    def test_empty_columns_removed_and_measurements_and_row_order_preserved(self):
        before = self.source.read_bytes()
        report = preparer.prepare(self.entry, self.root, self.root / "processed")
        with (self.root / "processed/ED2024.csv").open() as stream:
            rows = list(csv.reader(stream))
        self.assertEqual(rows[0], ["timestamp", "763", "773"])
        self.assertEqual(rows[1], ["2023-10-29T02:56:15", "0.1000", "0.2000"])
        self.assertEqual(rows[2], ["2023-10-29T02:03:47", "0.3000", "0.4000"])
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(report["removed_empty_unnamed_columns"], 2)
        self.assertEqual(len(report["local_clock_regressions"]), 1)
        self.assertFalse(report["paper_row_count_matches"])

    def test_hash_mismatch_rejected(self):
        self.source.write_text(self.source.read_text() + "\n")
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            preparer.prepare(self.entry, self.root, self.root / "processed")

    def test_nonempty_unnamed_column_rejected_without_partial_output(self):
        self.source.write_text(self.source.read_text().replace("0.2000,,", "0.2000,x,"))
        self.entry["sha256"] = preparer.sha256(self.source)
        with self.assertRaisesRegex(ValueError, "unnamed column"):
            preparer.prepare(self.entry, self.root, self.root / "processed")
        self.assertFalse((self.root / "processed/ED2024.csv").exists())
        self.assertFalse(list((self.root / "processed").glob("*.tmp")))

    def test_original_cannot_be_overwritten(self):
        with self.assertRaisesRegex(ValueError, "must not be overwritten"):
            preparer.prepare(self.entry, self.root, self.root)

    def test_zip_reads_only_manifest_member_without_path_extraction(self):
        archive = self.root / "UH2024.zip"
        with ZipFile(archive, "w") as z:
            z.writestr("UH2024.csv", self.source.read_bytes())
            z.writestr("../unwanted.txt", "must not be extracted")
        self.entry.update(file=archive.name, archive_member="UH2024.csv", sha256=preparer.sha256(archive))
        report = preparer.prepare(self.entry, self.root, self.root / "processed")
        self.assertEqual(report["rows"], 2)
        self.assertFalse((self.root / "unwanted.txt").exists())

    def test_unexpected_channel_order_rejected(self):
        self.entry["channel_labels"] = ["773", "763"]
        with self.assertRaisesRegex(ValueError, "channel labels/order"):
            preparer.prepare(self.entry, self.root, self.root / "processed")

    def test_invalid_measurement_rejected(self):
        self.source.write_text(self.source.read_text().replace("0.1000", "NaN"))
        self.entry["sha256"] = preparer.sha256(self.source)
        with self.assertRaisesRegex(ValueError, "field magnitude"):
            preparer.prepare(self.entry, self.root, self.root / "processed")


if __name__ == "__main__":
    unittest.main()

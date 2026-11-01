"""Behavioral checks for interchange schemas and leakage-relevant data ordering."""

import hashlib
import importlib.util
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "validate_dataset.py"
spec = importlib.util.spec_from_file_location("dataset_validator", MODULE_PATH)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class DatasetValidationTests(unittest.TestCase):
    def check_csv(self, text, **options):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "example.csv"
            path.write_text(text, encoding="utf-8")
            before = path.read_bytes()
            result = validator.validate(path, unit=options.pop("unit", "V/m"), **options)
            self.assertEqual(path.read_bytes(), before, "Validation changed the input")
            self.assertEqual(result["sha256"], hashlib.sha256(before).hexdigest())
            return result

    def test_valid_wide_and_input_integrity(self):
        result = self.check_csv(
            "timestamp,763,773\n2024-01-01T00:00:00Z,0,0.2\n2024-01-01T00:07:30Z,0.1,0.3\n"
        )
        self.assertEqual((result["observations"], result["channels"]), (2, 2))
        self.assertEqual(result["sampling_intervals"]["median_seconds"], 450)

    def test_valid_long_counts_observations_not_rows(self):
        result = self.check_csv(
            "timestamp,frequency_mhz,value\n"
            "2024-01-01T00:00:00Z,773,0.2\n2024-01-01T00:00:00Z,763,0.1\n"
            "2024-01-01T00:07:30Z,763,0.2\n2024-01-01T00:07:30Z,773,0.3\n",
            file_format="long",
        )
        self.assertEqual((result["observations"], result["csv_data_rows"]), (2, 4))

    def test_nonfinite_or_missing_measurements_fail(self):
        for value in ["NaN", "inf", "", "not-a-number"]:
            with self.subTest(value=value), self.assertRaises(validator.ValidationError):
                self.check_csv(f"timestamp,763\n2024-01-01T00:00:00Z,{value}\n")

    def test_negative_field_strength_fails_but_dbm_is_valid(self):
        text = "timestamp,763\n2024-01-01T00:00:00Z,-53.2\n"
        with self.assertRaises(validator.ValidationError):
            self.check_csv(text)
        self.assertEqual(self.check_csv(text, unit="dBm")["channels"], 1)

    def test_duplicate_or_reversed_wide_timestamps_fail(self):
        for second in ["2024-01-01T00:00:00Z", "2023-12-31T23:59:00Z"]:
            with self.subTest(second=second), self.assertRaises(validator.ValidationError):
                self.check_csv(f"timestamp,763\n2024-01-01T00:00:00Z,0.1\n{second},0.2\n")

    def test_mixed_timezone_conventions_fail(self):
        with self.assertRaisesRegex(validator.ValidationError, "mixed timezone"):
            self.check_csv("timestamp,763\n2024-01-01T00:00:00Z,0.1\n2024-01-01T00:07:30,0.2\n")

    def test_local_clock_regression_requires_explicit_option(self):
        text = "timestamp,763\n2023-10-29T02:56:15,0.1\n2023-10-29T02:03:47,0.2\n2023-10-29T02:11:19,0.3\n"
        with self.assertRaises(validator.ValidationError):
            self.check_csv(text)
        result = self.check_csv(text, allow_local_clock_regressions=True)
        self.assertEqual(len(result["local_clock_regressions"]), 1)
        self.assertEqual(result["observations"], 3)
        self.assertEqual(result["sampling_intervals"]["min_seconds"], 452)

    def test_aware_clock_regression_still_fails_with_option(self):
        with self.assertRaises(validator.ValidationError):
            self.check_csv("timestamp,763\n2024-01-01T01:00:00Z,0.1\n2024-01-01T00:00:00Z,0.2\n", allow_local_clock_regressions=True)

    def test_cli_reports_naive_local_clock_changes_by_default(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "clock.csv"
            path.write_text("timestamp,763\n2023-10-29T02:56:15,0.1\n2023-10-29T02:03:47,0.2\n")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = validator.main([str(path), "--unit", "V/m"])
            report = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(report["status"], "valid_with_warnings")
            self.assertEqual(len(report["local_clock_regressions"]), 1)

    def test_cli_strict_time_order_rejects_local_clock_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "clock.csv"
            path.write_text("timestamp,763\n2023-10-29T02:56:15,0.1\n2023-10-29T02:03:47,0.2\n")
            with contextlib.redirect_stdout(io.StringIO()):
                code = validator.main([str(path), "--unit", "V/m", "--strict-time-order"])
            self.assertEqual(code, 2)

    def test_incomplete_last_long_observation_fails(self):
        with self.assertRaisesRegex(validator.ValidationError, "final timestamp"):
            self.check_csv(
                "timestamp,frequency_mhz,value\n"
                "2024-01-01T00:00:00Z,763,0.1\n2024-01-01T00:00:00Z,773,0.2\n"
                "2024-01-01T00:07:30Z,763,0.2\n", file_format="long",
            )

    def test_incomplete_middle_long_observation_fails(self):
        with self.assertRaisesRegex(validator.ValidationError, "preceding timestamp"):
            self.check_csv(
                "timestamp,frequency_mhz,value\n"
                "2024-01-01T00:00:00Z,763,0.1\n2024-01-01T00:00:00Z,773,0.2\n"
                "2024-01-01T00:07:30Z,763,0.2\n2024-01-01T00:15:00Z,763,0.3\n",
                file_format="long",
            )

    def test_duplicate_long_timestamp_channel_fails(self):
        with self.assertRaisesRegex(validator.ValidationError, "duplicate timestamp-frequency"):
            self.check_csv(
                "timestamp,frequency_mhz,value\n2024-01-01T00:00:00Z,763,0.1\n"
                "2024-01-01T00:00:00Z,763.0,0.2\n", file_format="long",
            )

    def test_frequency_headers_are_numerically_unique(self):
        with self.assertRaises(validator.ValidationError):
            self.check_csv("timestamp,763,763.0\n2024-01-01T00:00:00Z,0.1,0.2\n")

    def test_timestamp_gaps_are_reported_without_resampling(self):
        result = self.check_csv(
            "timestamp,763\n2024-01-01T00:00:00Z,0.1\n2024-01-01T00:07:30Z,0.2\n"
            "2024-01-01T00:15:00Z,0.3\n2024-01-01T01:00:00Z,0.4\n"
        )
        self.assertEqual(result["observations"], 4)
        self.assertEqual(result["sampling_intervals"]["gaps_above_twice_median"], 1)
        self.assertTrue(any("Intervals vary" in x for x in result["warnings"]))

    def test_explicit_timestamp_format_and_header(self):
        result = self.check_csv(
            "Datetime,763\n24/06/2022 18:22:45,0.1\n",
            timestamp_column="Datetime", time_format="%d/%m/%Y %H:%M:%S",
        )
        self.assertEqual(result["first_timestamp"], "2022-06-24T18:22:45")
        self.assertTrue(any("Timezone" in x for x in result["warnings"]))

    def test_header_only_empty_or_bad_width_fail(self):
        for text in ["", "timestamp,763\n", "timestamp,763\n2024-01-01,0.1,0.2\n"]:
            with self.subTest(text=text), self.assertRaises(validator.ValidationError):
                self.check_csv(text)


if __name__ == "__main__":
    unittest.main()

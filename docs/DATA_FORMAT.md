# Measurement file format

The four measurement campaigns are distributed as wide CSV tables. UH2024.zip contains the CSV member `UH2024.csv`. File identities and parsing information are recorded in [dataset_manifest.json](../data/dataset_manifest.json), and frequency labels are listed in [channel_dictionary.csv](../data/channel_dictionary.csv).

## Source schema

Each row contains one observation across the monitored frequency channels:

```text
date,<frequency_1_MHz>,<frequency_2_MHz>,...
```

The `date` column records the observation's local timestamp. Numeric frequency labels give channel center frequencies in MHz; values are electric-field strength in V/m. Preserve the original channel order for model inputs and interpretation.

| Dataset | Date representation |
| --- | --- |
| ED-2022 | Month/day/year, hour:minute |
| UH-2022 | Day/month/year, hour:minute:second |
| ED-2024 | Day/month/year, hour:minute:second |
| UH-2024 | Year-month-day, hour:minute:second |

## Prepared schema

Run `python tools/prepare_datasets.py --output-dir data/processed` from the repository root. The resulting files use UTF-8 and ISO 8601 timestamp text:

```text
timestamp,<frequency_1_MHz>,<frequency_2_MHz>,...
```

The utility verifies source hashes, reads the named ZIP member directly, omits only wholly empty unnamed columns, and preserves measurement strings and observation order. Source files remain unchanged. The preparation report records source/output hashes, dimensions, and time-axis summaries.

## Time-axis interpretation

Timestamps retain the source local-clock convention. The preparation utility preserves acquisition order and reports clock changes without sorting or assigning timezone offsets. For analyses expressed in elapsed time, use the acquisition timestamps and an explicitly chosen timezone and gap-handling policy. For model windows, state the observation-based lookback, horizon, and preprocessing procedure used.

The validator's `--allow-local-clock-regressions` option permits reported local-clock changes while retaining source row order. It does not assign UTC times. Read the preparation report when choosing an elapsed-time analysis procedure.

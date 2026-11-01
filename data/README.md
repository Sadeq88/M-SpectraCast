# Using the measurement exports

The source artifacts are committed at the repository root. Direct links are in the [README](../README.md#datasets). Keep them as the immutable inputs to downstream processing.

## Verify file identity

From the repository root on a system with `sha256sum`:

```bash
sha256sum --check data/SHA256SUMS
```

The Python preparation tool also verifies these hashes automatically and supports Windows, macOS, and Linux without external packages. A matching hash establishes file identity with this release; it does not resolve the documented differences from the paper's Table 2.

## Prepare all four datasets

```bash
python tools/prepare_datasets.py --output-dir data/processed
```

To prepare a single campaign:

```bash
python tools/prepare_datasets.py --dataset UH-2024 --output-dir data/processed
```

The ZIP member is read directly without extracting arbitrary archive paths. Source files are never overwritten. Existing generated files in the chosen output directory may be replaced after the new output passes checks.

## Output schema

Prepared files use UTF-8, comma separation, one header row, and the following wide schema:

```text
timestamp,<frequency_1_MHz>,<frequency_2_MHz>,...
```

`timestamp` is an ISO 8601 representation of the original local clock, with no invented timezone offset. Each frequency column contains electric-field values in V/m. Original measurement strings, channel order, and source row order are preserved. The report records output hashes, counts, empty-column removal, sampling gaps, and local-clock regressions.

The 2024 exports each contain 27 wholly empty unnamed columns. The preparation tool verifies that these columns remain empty before omitting them; a nonempty unnamed column is an error.

## Validate a prepared export

```bash
python tools/validate_dataset.py data/processed/ED2022.csv --unit V/m
python tools/validate_dataset.py data/processed/UH2022.csv --unit V/m --allow-local-clock-regressions
python tools/validate_dataset.py data/processed/ED2024.csv --unit V/m --allow-local-clock-regressions
python tools/validate_dataset.py data/processed/UH2024.csv --unit V/m --allow-local-clock-regressions
```

Local-clock regressions are explicitly reported and allowed only for timezone-naive inputs when that option is selected. It does not resolve clock ambiguity or convert timestamps to UTC. Read [DATA_QUALITY.md](../docs/DATA_QUALITY.md) before elapsed-time analysis or forecasting.

## Metadata

- [dataset_manifest.json](dataset_manifest.json): actual source-artifact identities, dimensions, formats, and paper-reported metadata.
- [channel_dictionary.csv](channel_dictionary.csv): exact frequency labels and channel ordering.
- [source_file_audit.json](source_file_audit.json): direct audit of the committed exports, including the CSV contained in UH2024.zip.
- [SHA256SUMS](SHA256SUMS): original artifact checksums.
- [paper_dataset_catalog.json](paper_dataset_catalog.json): manuscript-reported values for comparison, not an additional dataset release.

Generated exports are excluded from Git because they can be recreated from the original files with the utility above.

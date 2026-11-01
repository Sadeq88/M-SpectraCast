# M-SpectraCast

### Multivariate Cluster-Enhanced Time-Series Forecasting for Wireless Networks

[![DOI](https://img.shields.io/badge/DOI-10.1109%2FOJCOMS.2026.3743620-005a9c)](https://doi.org/10.1109/OJCOMS.2026.3743620)
[![IEEE OJCOMS](https://img.shields.io/badge/IEEE-OJCOMS_2026-00629b)](https://ieeexplore.ieee.org/document/11738776)
[![License](https://img.shields.io/badge/License-Apache_2.0-3c873a)](LICENSE)

**Sadeq Bani Melhem, Hina Tabassum, Luca Chiaraviglio, and Uyen Trang Nguyen**

*IEEE Open Journal of the Communications Society*, vol. 7, pp. 13525-13547, 2026.

[Paper](https://doi.org/10.1109/OJCOMS.2026.3743620) · [Datasets](#datasets) · [Quick start](#quick-start) · [Experimental setup](docs/REPRODUCIBILITY.md) · [Citation](#citation)

**Dataset companion to the published article.** This repository provides the four frequency-selective RF-EMF datasets, their metadata, and supporting data utilities.

M-SpectraCast is a clustering-enhanced framework for multivariate wireless time-series forecasting. It learns soft groups of frequency channels with related temporal behavior and combines cluster-specific forecasting heads, enabling selective information sharing across channels. The paper evaluates the approach with **DLinear, PatchTST, and TSMixer** on long-term, frequency-selective radio-frequency electromagnetic field (RF-EMF) measurements from Rome, Italy.

![M-SpectraCast framework: normalization, temporal backbone, channel clustering and prototype learning, and cluster-aware forecasting.](assets/framework.png)

*Fig. 1 from the authors' manuscript, DOI [10.1109/OJCOMS.2026.3743620](https://doi.org/10.1109/OJCOMS.2026.3743620).*

## What is included

- Four original measurement exports, with checksums and a channel dictionary.
- A dependency-free preparation tool that reads the CSV/ZIP files, checks their identity, and creates consistent CSV exports.
- Dataset provenance, file-format guidance, and the paper's experimental protocol.
- Machine-readable citation metadata and an attributed framework figure.

## Datasets

ED denotes the Electronics Department of the University of Rome Tor Vergata; UH denotes the University Hospital complex. Each numeric column is a monitored frequency channel in MHz, and its values represent electric-field strength in V/m.

| Dataset | Measurement site | Channels | Download |
| --- | --- | ---: | --- |
| ED-2022 | Electronics Department | 27 | [ED2022.csv](ED2022.csv) |
| UH-2022 | University Hospital | 27 | [UH2022.csv](UH2022.csv) |
| ED-2024 | Electronics Department | 29 | [ED2024.csv](ED2024.csv) |
| UH-2024 | University Hospital | 29 | [UH2024.zip](UH2024.zip), containing `UH2024.csv` |

The campaign identifiers follow the paper. Each file contains a multivariate sequence of synchronized frequency-channel measurements. File dimensions, timestamp formats, and exact channel labels are provided in the metadata below.

[Dataset card](docs/DATASET_CARD.md) · [Channel dictionary](data/channel_dictionary.csv) · [SHA-256 checksums](data/SHA256SUMS) · [Machine-readable manifest](data/dataset_manifest.json)

## Quick start

The data utilities require **Python 3.11 or newer** and use only the standard library.

```bash
git clone https://github.com/Sadeq88/M-SpectraCast.git
cd M-SpectraCast
python tools/prepare_datasets.py --output-dir data/processed
```

This creates `ED2022.csv`, `UH2022.csv`, `ED2024.csv`, `UH2024.csv`, and `preparation_report.json` inside `data/processed/`. You can also prepare one campaign:

```bash
python tools/prepare_datasets.py --dataset ED-2022 --output-dir data/processed
```

The tool verifies source-file hashes, removes only wholly empty unnamed columns, converts timestamp text to ISO 8601, and preserves source observation order and measurement strings. It does not resample, interpolate, standardize, or infer a timezone.

To inspect a prepared file:

```bash
python tools/validate_dataset.py data/processed/ED2022.csv --unit V/m
```

See the [data guide](data/README.md) for the output schema, checksum verification, timestamp conventions, and validation options.

## Research protocol

The paper reports chronological **60% / 20% / 20%** training, validation, and test subsets; per-channel standardization fitted on training data only; a main lookback of **336 observations**; and horizons of **96, 192, 336, and 720 observations**. The main comparisons use **two latent clusters**, Adam with learning rate `1e-3`, batch size `32`, up to `30` epochs, and early stopping with patience `5`. Main results are averaged over five random seeds.

The paper also evaluates frozen-model cross-dataset forecasting from **ED-2022 to ED-2024**, aligning physically corresponding channels and retaining the source-training normalization statistics. See [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) for the experimental setup and evaluation procedure.

## Citation

Please cite the paper when using these datasets or the associated research:

> S. B. Melhem, H. Tabassum, L. Chiaraviglio, and U. T. Nguyen, "M-SpectraCast: Multivariate Cluster-Enhanced Time-Series Forecasting for Wireless Networks," *IEEE Open Journal of the Communications Society*, vol. 7, pp. 13525-13547, 2026, doi: 10.1109/OJCOMS.2026.3743620.

```bibtex
@article{Melhem2026MSpectraCast,
  author  = {Melhem, Sadeq Bani and Tabassum, Hina and Chiaraviglio, Luca and Nguyen, Uyen Trang},
  title   = {{M-SpectraCast}: Multivariate Cluster-Enhanced Time-Series Forecasting for Wireless Networks},
  journal = {IEEE Open Journal of the Communications Society},
  year    = {2026},
  volume  = {7},
  pages   = {13525--13547},
  doi     = {10.1109/OJCOMS.2026.3743620},
  url     = {https://doi.org/10.1109/OJCOMS.2026.3743620}
}
```

Also available as [CITATION.cff](CITATION.cff) and [references.bib](references.bib).

## Support and contributions

Open a [GitHub issue](https://github.com/Sadeq88/M-SpectraCast/issues) for a dataset problem or reproducibility question. Include the dataset filename and hash, code revision, command, and relevant output. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

The existing [Apache License 2.0](LICENSE) is preserved. The manuscript and reproduced framework figure carry [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSING.md](LICENSING.md) for scope and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for attribution.

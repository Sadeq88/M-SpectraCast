# RF-EMF datasets

## Overview

Four long-term, frequency-selective RF-EMF measurement campaigns accompany the [M-SpectraCast paper](https://doi.org/10.1109/OJCOMS.2026.3743620). They support multivariate forecasting, inter-frequency dependency analysis, temporal characterization, and cross-dataset research.

The measurements were collected at the Electronics Department of the University of Rome Tor Vergata (ED) and a University Hospital complex (UH), in Rome, Italy. Campaign identifiers follow the paper: ED-2022, UH-2022, ED-2024, and UH-2024.

## Measurement chain

The paper describes a calibrated measurement chain comprising a **Keysight N6850A** omnidirectional passive antenna, an **Anritsu MS27102A** remote spectrum-monitoring unit, a 1.5 m low-loss coaxial cable, and **ARPA-Lazio Search24** control software. The setup covers monitored cellular bands up to 6 GHz.

The distributed values represent electric-field strength in **V/m**. Frequency-column labels identify channel center frequencies in **MHz**. The paper describes an average acquisition interval of approximately 7-7.5 minutes.

## Download

| Campaign | Site | Channels | Source file |
| --- | --- | ---: | --- |
| ED-2022 | Electronics Department | 27 | [ED2022.csv](../ED2022.csv) |
| UH-2022 | University Hospital | 27 | [UH2022.csv](../UH2022.csv) |
| ED-2024 | Electronics Department | 29 | [ED2024.csv](../ED2024.csv) |
| UH-2024 | University Hospital | 29 | [UH2024.zip](../UH2024.zip), member `UH2024.csv` |

Each row provides synchronized measurements across its monitored frequency channels. See the [file-format guide](DATA_FORMAT.md) for CSV schemas and timestamp handling, the [manifest](../data/dataset_manifest.json) for file metadata, and [SHA256SUMS](../data/SHA256SUMS) for checksums.

## Frequency channels

The [channel dictionary](../data/channel_dictionary.csv) records each campaign's exact frequency labels, channel order, and descriptive physical group:

| Group | Approximate frequency region |
| --- | --- |
| G1 | 763-1870 MHz |
| G2 | 2120-2680 MHz |
| G3 | 3447-3760 MHz |

These regions describe the monitored channels; they do not imply continuous spectral coverage. M-SpectraCast learns latent clusters from temporal representations rather than imposing these physical groups as prediction clusters.

## Physical quantities

The paper relates calibrated received power to RMS electric-field strength through

$$
P_r^{(W)}(f)=10^{(P_r^{(dBm)}(f)-30)/10},\qquad
E_f=\sqrt{\frac{P_r^{(W)}(f)Z_0}{A_e(f)}}.
$$

Here $Z_0=376.73\,\Omega$, $A_e(f)=G_f\lambda_f^2/(4\pi)$, and $\lambda_f=c/f$. The supplied CSV values are already expressed in V/m; the data-preparation utility preserves those values.

## Use and citation

Preserve channel order and acquisition order when constructing multivariate inputs. Fit normalization and learned preprocessing on training data only. Report the campaign identifiers, input hashes, temporal split, and preprocessing procedure with derived research results.

Please cite the paper using [CITATION.cff](../CITATION.cff) or [references.bib](../references.bib) and retain the applicable [license and attribution](../LICENSING.md).

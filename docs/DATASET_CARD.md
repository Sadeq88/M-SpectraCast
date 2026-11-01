# RF-EMF dataset card

## Scope

Four frequency-selective RF-EMF measurement exports accompany the M-SpectraCast paper. They support multichannel forecasting, inter-frequency dependency analysis, temporal characterization, and cross-dataset research with an explicitly defined channel correspondence.

The campaigns were collected at the Electronics Department of the University of Rome Tor Vergata (ED) and a University Hospital complex (UH), in Rome, Italy. Campaign names follow the paper; the later campaigns began in 2023 and retain the `2024` suffix.

The [README dataset table](../README.md#datasets) lists actual export dimensions and date coverage. [DATA_QUALITY.md](DATA_QUALITY.md) compares these files with the manuscript's Table 2 and documents timestamp gaps and local-clock reversals.

## Measurement provenance

The paper describes a calibrated measurement chain comprising a **Keysight N6850A** omnidirectional passive antenna, an **Anritsu MS27102A** remote spectrum-monitoring unit, a 1.5 m low-loss coaxial cable, and **ARPA-Lazio Search24** control software. The setup covers monitored cellular bands up to 6 GHz.

The distributed values are electric-field magnitudes in **V/m**. Frequency-column labels are channel center frequencies in **MHz**. The paper describes acquisition at an average interval of about 7-7.5 minutes. The exports have campaign-specific timestamp formats and interruptions; the actual intervals are reported in the quality notes.

## Files and channel definitions

| Campaign | Source artifact | Channels | Data representation |
| --- | --- | ---: | --- |
| ED-2022 | [ED2022.csv](../ED2022.csv) | 27 | Wide CSV |
| UH-2022 | [UH2022.csv](../UH2022.csv) | 27 | Wide CSV |
| ED-2024 | [ED2024.csv](../ED2024.csv) | 29 | Wide CSV with empty trailing columns |
| UH-2024 | [UH2024.zip](../UH2024.zip), member `UH2024.csv` | 29 | Zipped wide CSV with empty trailing columns |

Each source row contains a `date` field followed by one value for every monitored frequency channel. The [channel dictionary](../data/channel_dictionary.csv) preserves exact labels and order for each campaign and assigns the paper's descriptive G1/G2/G3 regions. The machine-readable [manifest](../data/dataset_manifest.json) specifies exact filenames, formats, hashes, and observed dimensions.

The descriptive physical groups cover approximately 763-1870 MHz (G1), 2120-2680 MHz (G2), and 3447-3760 MHz (G3). These intervals do not imply continuous spectral coverage. They are not the learned latent clusters used by M-SpectraCast.

## Units and conversion

The paper converts calibrated received power in dBm into RMS electric-field strength using

$$
P_r^{(W)}(f)=10^{(P_r^{(dBm)}(f)-30)/10},\qquad
E_f=\sqrt{\frac{P_r^{(W)}(f) Z_0}{A_e(f)}}.
$$

Here $Z_0=376.73\,\Omega$, $A_e(f)=G_f\lambda_f^2/(4\pi)$, and $\lambda_f=c/f$. Frequency-dependent antenna calibration is required for the original conversion. The released CSVs already contain field values; the preparation utility performs no power-to-field conversion. Raw received-power logs and calibration files are not included in this repository.

## Preprocessing and time interpretation

Source artifacts are preserved. The preparation utility verifies file identity, removes only wholly empty unnamed columns, normalizes date text, and preserves channel order, observation order, and measurement strings. No timezone, missing values, or additional observations are inferred.

Three exports have local-clock regressions consistent with daylight-saving transitions, and some contain long acquisition interruptions. Confirm source timezone and gap policy before interpreting elapsed-time dependencies. An explicit source-to-target physical channel map is needed for cross-dataset evaluation; one cannot infer the paper's exact map from array indices or broad frequency regions.

Fit any normalization, learned imputation, clustering, or other statistical preprocessing using the training portion only. Keep chronological forecast targets within their assigned split. Record any changes in channel count, row count, or timestamp coverage introduced by downstream preprocessing.

## Intended uses and limitations

These are observational measurements from two environments and selected channels. They do not represent all frequency bands, devices, countries, or deployment conditions. A time-series forecast alone is not a regulatory compliance assessment. Exact reproduction of the article additionally requires its final experiment inputs, forecasting implementation, saved settings, seeds, and channel map; those artifacts are not currently included.

Please cite the paper using [CITATION.cff](../CITATION.cff) or [references.bib](../references.bib), and retain the applicable [license and attribution](../LICENSING.md).

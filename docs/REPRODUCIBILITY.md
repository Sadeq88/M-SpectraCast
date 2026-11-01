# Experimental protocol and reproduction status

This repository currently distributes measurement exports, dataset inspection/preparation utilities, and research documentation. It does not yet distribute the forecasting training implementation, checkpoints, exact seed list, or source-to-target frequency correspondence used for the article's reported models.

The information below summarizes the authors' manuscript associated with DOI [10.1109/OJCOMS.2026.3743620](https://doi.org/10.1109/OJCOMS.2026.3743620). It is not a claim that the data utilities execute those experiments.

## Paper protocol

| Component | Reported setting |
| --- | --- |
| Datasets | ED-2022, UH-2022, ED-2024, UH-2024 |
| Temporal split | Chronological 60% training / 20% validation / 20% test |
| Standardization | Per-channel training mean and standard deviation; epsilon 1e-8 |
| Window stride | One observation |
| Main lookback L | 336 observations |
| Forecast horizons H | 96, 192, 336, 720 observations |
| Backbones | DLinear, PatchTST, TSMixer |
| Main cluster count K | 2 |
| Optimizer / learning rate | Adam / 1e-3 |
| Batch size / maximum epochs | 32 / 30 |
| Early stopping | Validation MSE, patience 5 |
| Main repeated runs | Five random seeds; report mean and standard deviation |
| Sensitivity analysis | Three repeated runs in the sensitivity table |
| Metrics | MSE and MAE |

The sensitivity table uses tau=0.2 and beta=0.05 unless varied. Those values do not, by themselves, establish every experiment's exact configuration.

The paper describes Python/PyTorch on Ubuntu 24.04.3 LTS, an Intel Core Ultra 9 285K processor, about 62 GB system RAM, an NVIDIA GeForce RTX 5090 with 32 GB memory, and CUDA 12.9. Exact training-package pins are not established by that hardware description. The dataset utilities in this repository require Python 3.11+ and no third-party packages; this is a separate environment from model training.

## Data preparation

Run the [quick start](../README.md#quick-start) to verify source hashes and create uniform CSV exports. Read [DATA_QUALITY.md](DATA_QUALITY.md): current export counts/date ranges do not all agree with Table 2, three files have local-clock regressions, and some campaigns contain acquisition interruptions. The utilities preserve source row order rather than guessing a timezone or gap policy.

The exact final model inputs must be identified before claiming numerical reproduction. Document any source-to-model conversion, filtering, resampling, time segmentation, or selection. Do not fabricate or remove observations merely to obtain the paper's dimensions.

## Requirements for an executable model release

When the final training implementation is added, connect each reported result to:

- An immutable code revision, original implementation attribution, and tested dependency environment.
- Exact input hashes, channel order, split boundary indices/timestamps, and window/gap handling.
- Actual seed values and complete per-experiment settings.
- Training-only normalization statistics, saved with checkpoints and keyed by channel.
- Checkpoint selection by validation performance, with test targets held out from model selection.
- A definition of the metric scale, aggregation across channels/windows/horizons, and standard-deviation convention.
- Commands for a short real-data run and for the main tables, with expected output locations and per-seed logs.

Training targets must remain inside the training interval. Validation and test inputs may include previously observed history only under an explicit loader protocol; their forecast targets must remain inside the relevant evaluation interval.

## Cross-dataset forecasting

The paper evaluates ED-2022 to ED-2024 without target-dataset retraining. Reproducing it requires the source-trained model, frozen backbone/prototypes/heads, source-training scaler, explicit physical source-to-target channel correspondence, and exact target evaluation interval. Channel counts and some frequency labels differ between campaigns, so matching by array position is insufficient. Do not fit a target-wide scaler or tune on target test errors.

## Verification performed for this repository update

All four source artifacts were downloaded and matched to their original Git blob identifiers. The source measurements were audited for shape, numeric values, timestamp formats/order, gaps, empty columns, and SHA-256 identity. The preparation utility was run on all four artifacts and checked to preserve source hashes, observation counts, channel order, row order, and measurement strings.

The standalone utility tests and documented commands are checked independently of the paper's forecasting models. No model-result reproduction is claimed.

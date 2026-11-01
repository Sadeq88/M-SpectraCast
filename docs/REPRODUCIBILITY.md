# Experimental setup

This page summarizes the forecasting protocol described in [M-SpectraCast: Multivariate Cluster-Enhanced Time-Series Forecasting for Wireless Networks](https://doi.org/10.1109/OJCOMS.2026.3743620).

## Main forecasting experiments

| Component | Setting |
| --- | --- |
| Datasets | ED-2022, UH-2022, ED-2024, UH-2024 |
| Temporal split | Chronological 60% training / 20% validation / 20% test |
| Standardization | Per-channel training mean and standard deviation; epsilon 1e-8 |
| Window stride | One observation |
| Main lookback L | 336 observations |
| Forecast horizons H | 96, 192, 336, 720 observations |
| Temporal backbones | DLinear, PatchTST, TSMixer |
| Main cluster count K | 2 |
| Optimizer / learning rate | Adam / 1e-3 |
| Batch size / maximum epochs | 32 / 30 |
| Early stopping | Validation MSE, patience 5 |
| Main repeated runs | Five random seeds; report mean and standard deviation |
| Primary metrics | Mean squared error (MSE), mean absolute error (MAE) |

The hyperparameter sensitivity analysis uses three repeated runs and varies the clustering temperature, clustering-loss weight, and patch configuration. Its default temperature is tau=0.2 and clustering-loss weight is beta=0.05 unless varied.

## Data preparation

The [quick start](../README.md#quick-start) creates a consistent CSV representation of the distributed measurements and verifies the source-file checksums. The [file-format guide](DATA_FORMAT.md) describes channel ordering, units, date parsing, and timestamp conventions.

For a forecasting experiment, establish the temporal split before fitting normalization or other learned preprocessing. Fit per-channel statistics on training data only and apply the same transformation to validation and test data. Record the file hashes, selected channels, split boundaries, window definitions, seed, and configuration with each run.

Training targets stay inside the training interval. Validation and test targets stay inside their evaluation intervals. Select the checkpoint using validation performance and compute final test errors after model selection. State whether MSE and MAE are evaluated in standardized or physical units and how errors are aggregated.

## Cross-dataset forecasting

The paper evaluates ED-2022 to ED-2024 with the source-trained model fixed. Source and target channels are aligned by physical frequency correspondence. The target inputs use the corresponding source-training normalization statistics, and the temporal backbone, cluster prototypes, and prediction heads remain frozen during inference.

## Reported computing platform

The experiments use Python/PyTorch on Ubuntu 24.04.3 LTS, an Intel Core Ultra 9 285K processor, approximately 62 GB system RAM, an NVIDIA GeForce RTX 5090 with 32 GB memory, and CUDA 12.9. The standalone data utilities in this repository require Python 3.11+ and use its standard library.

## Data utility checks

Run the utility test suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

The checks cover file identity, measurement preservation, CSV schemas, timestamp handling, duplicate observations, and channel completeness.

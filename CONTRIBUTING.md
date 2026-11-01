# Contributing

Please open an issue before proposing changes to the forecasting method or evaluation protocol. Documentation fixes and reproducible bug reports are welcome.

For bugs, provide the code revision, operating system, Python/PyTorch versions, dataset identifier and hash, command or notebook cell, seed, expected behavior, and full traceback. A small example that demonstrates the failure is especially useful. Avoid posting credentials, private paths, or measurement files whose access terms do not permit redistribution.

For model or preprocessing changes, explain the scientific effect and verify that the comparison remains consistent with the paper's chronological evaluation. Keep protocol changes explicit so results remain comparable.

For the standalone CSV validation tool in this update:

```bash
python -m unittest discover -s tests -v
```

Attribute reused implementations and preserve their original license notices. Report a dataset problem with its filename, version, hash, and affected timestamps or channels.

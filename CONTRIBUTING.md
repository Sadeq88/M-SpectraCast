# Contributing

Dataset questions, documentation improvements, and reproducible utility bug reports are welcome through GitHub Issues.

For bugs, provide the code revision, operating system, Python version, dataset identifier and hash, command, expected behavior, and traceback. A small example that demonstrates the failure is especially useful.

For preprocessing changes, explain their effect on measurement values, timestamps, channel ordering, or forecasting windows.

Run the data utility checks with:

```bash
python -m unittest discover -s tests -v
```

Attribute reused implementations and preserve their original license notices. Report a dataset problem with its filename, version, hash, and affected timestamps or channels.

# Verified export characteristics

This audit describes the original files at source commit `2227163d9142aff9869988b6d529593c22b6fafe`. Source files are preserved byte for byte. [dataset_manifest.json](../data/dataset_manifest.json) records their hashes, formats, channels, and observed coverage; [source_file_audit.json](../data/source_file_audit.json) provides the detailed counts.

## Export and paper differences

The paper column below comes from Table 2 of the authors' manuscript associated with DOI [10.1109/OJCOMS.2026.3743620](https://doi.org/10.1109/OJCOMS.2026.3743620). The export column is computed directly from the committed files.

| Dataset | Export rows/channel | Table 2 readings/channel | Export timestamp range | Table 2 coverage |
| --- | ---: | ---: | --- | --- |
| ED-2022 | 34,061 | 34,061 | 2022-06-24 18:22 to 2022-12-07 08:02 | 2022-06-24 18:22:45 to 2022-12-14 16:32:14 |
| UH-2022 | 43,529 | 43,532 | 2022-05-16 11:10:45 to 2022-12-15 15:41:23 | 2022-05-16 11:10:45 to 2022-12-15 15:48:08 |
| ED-2024 | 56,220 | 56,220 | 2023-03-15 16:32:20 to 2024-07-19 14:29:27 | 2023-03-15 16:32:20 to 2024-09-04 03:00:54 |
| UH-2024 | 68,699 | 68,700 | 2023-03-21 14:24:09 to 2024-08-23 20:48:22 | 2023-03-21 14:24:09 to 2024-07-02 04:45:44 |

These differences are not repaired by inventing observations, changing dates, or deleting valid rows. The release records the files as supplied. Matching a row count alone does not prove that an export is identical to the exact model input used for the paper. Confirmation of the publication's final experiment exports remains necessary for exact numerical reproduction.

## Timestamp formats and clock changes

| Export | Source date format | Local-clock reversal |
| --- | --- | --- |
| ED2022.csv | Month/day/year, hour:minute | None observed |
| UH2022.csv | Day/month/year, hour:minute:second | CSV line 33,959: 2022-10-30 02:58:31 to 02:05:31 |
| ED2024.csv | Day/month/year, hour:minute:second | CSV line 22,506: 2023-10-29 02:56:15 to 02:03:47 |
| UH2024.csv inside ZIP | Year-month-day, hour:minute:second | CSV line 37,662: 2023-10-29 02:53:23 to 02:00:55 |

Line numbers include the header. The reversal dates and approximately one-hour changes are consistent with autumn daylight-saving transitions. This is an inference from the timestamps, not a confirmed timezone assignment. The files contain no timezone offsets. Preserve source row order; sorting naive clock times can reorder actual observations across a fall-back transition. Confirm the measurement system's timezone and ambiguity handling before converting to UTC.

ED2022.csv stores only minute-resolution timestamps. The utility does not recover seconds that are absent from that export.

## Acquisition intervals and interruptions

Intervals below use consecutive source rows and positive clock differences. They are local-clock differences; a timezone-aware interpretation is required for precise elapsed-time analysis across clock changes.

| Dataset | Median positive interval | Maximum positive gap | Gaps greater than one hour |
| --- | ---: | ---: | ---: |
| ED-2022 | 420 s | 420 s | 0 |
| UH-2022 | 421 s | 79,543 s | 2 |
| ED-2024 | 452 s | 6,159,241 s | 85 |
| UH-2024 | 452 s | 11,856,904 s | 3 |

These exports must not all be treated as uninterrupted regular grids. In particular, adjacent rows across an acquisition interruption do not represent adjacent uniformly spaced physical instants. Explain any segmentation, resampling, imputation, or gap-exclusion policy when reporting forecasts, FFTs, or lag statistics. Observation-count forecast horizons are not automatically fixed elapsed-time horizons.

## Measurement values and CSV structure

- All four files have finite numeric values in the labeled measurement columns, with no missing or negative magnitudes observed.
- No duplicate timestamp strings or malformed-width data rows were found.
- The 2022 exports have 27 labeled channels. The 2024 exports have 29 labeled channels plus 27 unnamed columns, verified empty in every data row.
- UH2024.zip contains one file, `UH2024.csv`; the ZIP and contained CSV have separate recorded hashes.

The preparation tool removes only the verified empty unnamed columns and standardizes timestamp text. It preserves measurement strings and source observation order. The original files are never overwritten, and the output report records all local-clock regressions and source/output hashes.

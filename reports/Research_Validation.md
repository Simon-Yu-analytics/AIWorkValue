# Research validation and interpretation

## Primary model verification

The primary ANCOVA coefficients, HC3 covariance and t-based 95% intervals were independently reconstructed with NumPy matrix algebra and SciPy quantiles. Both model matrices have full column rank. No real outcomes were changed or trimmed to improve results.

| Model | N | Rank / columns | Independent HC3 SE | Status |
|---|---:|---:|---:|---|
| primary_time | 346 | 15 / 15 | 1.140280 | passed |
| primary_quality | 352 | 15 / 15 | 0.118617 | passed |

## Selection, missingness and post-assignment information

The source sample exclusions and random task-order mapping remain documented in the data protocol. The primary time model uses 346 available baseline/post cases and the quality model uses 352, from 359 retained non-fixed-time participants. Missing outcomes are not imputed. Reported actual AI use is an outcome, not a primary sample filter or regression control. Differential completion and later exclusions still limit full-sample intention-to-treat claims.

Time outliers above the declared QC threshold are flagged, not automatically removed. Valid writing scores remain within the source 1–7 scale. Source checksums, retained-key uniqueness, warehouse round-trip equivalence and dimension/fact constraints are validated by the ETL. There is no predictive train/test benchmark in this experimental reanalysis.

## Baseline-performance heterogeneity

The continuous assignment × baseline writing-score interaction is preferable to inferring a subgroup difference from separate significance tests. The two exploratory interaction tests also receive Holm adjustment. Conditional effects at baseline-score quartiles use linear contrasts of the same fitted interaction models and pointwise robust intervals; they are not independent subgroup experiments or simultaneous confidence bands.

A single baseline writing task is noisy. Quality scores have a ceiling at 7, and comparisons involving baseline and change can be affected by regression to the mean. The pattern is suggestive of task-score moderation, not proof of general worker ability differences or an employee assignment policy.

## Three different conclusions

1. **Statistical:** the retained historical sample supports nonzero assignment contrasts under the stated models.
2. **Practical:** the effect is measured in minutes and writing-rating points for short tasks; it does not establish an equivalent whole-job productivity gain or factual correctness.
3. **Commercial:** a new workflow must cover seat/support costs after review, revision and expected rework. Baseline-duration caps and business assumptions can change value without changing the historical regression result.

## Remaining uncertainty

This validation checks computation and declared analysis choices. It does not establish a new randomized experiment, current-product performance, a company deployment, causal effects for every participant subgroup or realized financial returns. See the original study and the data/methods protocol for context.

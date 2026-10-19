# Project walkthrough

AIWorkValue asks when generative AI writing assistance might create useful business value. The project combines public experimental data, statistical reanalysis and a hypothetical cost example. It uses Python, SQL and explainable regression methods; no large-model training is required.

## 1. Understand the experiment and sample

Read the original study, the authors' ReadMe and [data and methods](DATA_AND_METHODS.md). Run `make download` and `make run`, then inspect the sample-flow audit.

Be able to explain:

- Why 786 raw survey records, 453 retained participants, 359 primary-arm participants, 346 time observations and 352 quality observations refer to different denominators.
- Why task A is not always the baseline task.
- Why the fixed-time arm is excluded from the primary time comparison.
- Why selecting only actual AI users would change the randomized comparison.

Sketch the study design and identify the most important sample limitations.

## 2. Follow the SQL analysis

Read the [SQL guide](../sql/README.md) and [generated findings](../reports/SQL_Analysis.md). Start with coverage, baseline balance and paired changes before moving to the business calculations.

| Query | What to explain |
|---|---|
| `01_sample_funnel.sql` | How LAG measures exclusions between stages and why raw records are not the randomized sample |
| `02_group_coverage.sql` | How conditional aggregation counts complete pairs without turning missing outcomes into zeros |
| `03_baseline_balance.sql` | How CTEs, a self-join and sample variance produce standardized mean differences |
| `04_paired_changes.sql` | Why each change comparison uses complete pairs and differs from an adjusted regression |
| `07_business_scenarios.sql` | How assumptions become capacity value and recurring costs |
| `08_break_even.sql` | How seat-cost, checking-time and task-volume boundaries are calculated, including undefined cases |
| `09_sensitivity_grid.sql` | How a window function compares value across checking-time settings |

All three named business scenarios and 36 sensitivity points are checked against Python. Missing follow-up responses remain missing rather than becoming recorded non-use.

## 3. Re-estimate the statistical models

Run the notebook cell by cell. Compare descriptive group means, changes from baseline and baseline-adjusted regression.

The time coefficient is measured in minutes. The quality coefficient is measured in points on a 1–7 writing scale; +0.70 points does not mean a 70% increase in factual accuracy. Understand why uncertainty is reported, what HC3 robust standard errors address, and why two primary tests receive Holm adjustment.

The participant-average quality estimator is simpler than the original paper's full specification. The paired-grader fixed-effect model is a supplementary check, not evidence of exact replication of every published coefficient. Baseline-score interactions are exploratory.

## 4. Reproduce the task extension

Read the [weekly status-email case](../reports/extensions/Weekly_Status_Email.md) and run `make extension`. Inspect its [configuration](../data/scenarios/weekly_status_email.json) and [SQL](../sql/extensions/weekly_status_email.sql).

The example compares 4, 8 and 20 eligible tasks per month with 1, 3 and 5 extra checking minutes per task. Explain why weekly-only use can release time while failing to cover subscription costs. Also explain why charging the entire subscription to one workflow differs from valuing several uses of the same tool.

Change one clearly labeled assumption, rebuild the results and interpret the change. Without new observations, keep it a hypothetical sensitivity exercise. Do not present it as an email experiment, company interview or measured saving.

## 5. Explain the business conclusion

A short explanation should cover the business question, the experimental comparison, the project's reconstruction and estimation choices, the main effects, and the assumptions required for a new workflow.

Useful questions to practice:

- Why is this an AI project even though it does not train a model?
- Why does a strong task-level effect not guarantee a positive investment case?
- Why is writing quality distinct from factual accuracy?
- Why is released employee capacity distinct from a reduction in cash expenditure?
- Which missing measurement is most likely to change the decision?

The original researchers conducted the experiment and collected the data. This repository contributes reanalysis, SQL, robustness comparisons and a hypothetical commercial extension, with AI assistance disclosed in the project scope. Personal descriptions should accurately reflect the work the author has reproduced, checked and understood.

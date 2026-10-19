# Project scope and reading path

AIWorkValue is a personal business analytics project using public research data. Its purpose is to practice connecting experimental evidence with a modest, explicit business calculation.

## Core analysis

1. Reconstruct the retained sample and map randomized task order to baseline/post outcomes.
2. Use SQL to inspect coverage, baseline differences and changes within complete pairs.
3. Fit one baseline-adjusted regression for completion time and one for writing quality.
4. Check whether time results change when using a different time measure or comparing changes from baseline.
5. Build a hypothetical cost example and investigate how task frequency and extra checking affect it.
6. Apply that calculation to a [weekly status-email example](../reports/extensions/Weekly_Status_Email.md), comparing nine frequency/checking combinations in SQL and Python.

For a first review, read the main README, the notebook, SQL files `02`, `03`, `04`, `07` and `08`, and the [business assumptions](BUSINESS_ASSUMPTIONS.md). These cover the main argument without requiring every optional model.

## Additional analysis

The full report and code also include log-time models, grader fixed effects, baseline-score interactions and follow-up adoption. These are additional learning and robustness exercises. They are not required to explain the main business calculation, and the exploratory results should not be presented as confirmed findings about different types of employees.

The detailed [data and methods](DATA_AND_METHODS.md), [research card](RESEARCH_CARD.md) and [analysis plan](ANALYSIS_PLAN.md) remain available for readers who want the implementation and interpretation details.

## Original research and project work

Noy and Zhang designed and conducted the original experiment and collected the data. This repository contributes a Python reconstruction, SQL analysis, estimator comparisons, visualizations and a hypothetical business extension. It does not report a newly collected experiment, a client project, an actual deployment or measured company savings.

AI tools assisted implementation and draft preparation. Sources, assumptions and executable calculations are documented so readers can inspect and reproduce the work. Personal application statements should accurately describe the author's contribution and follow the receiving institution's disclosure requirements.

## Completed extension and remaining evidence

The task-volume extension is implemented in a scenario configuration, a SQL query, a Python cross-check, an executed notebook section and a narrative with a chart. It is a completed hypothetical calculation, not a personally conducted field study. No email-task observations or company pilot have been collected. The next evidence would be actual task frequency and full checking time for one workflow; personal understanding should be developed by reproducing and explaining the existing calculations.

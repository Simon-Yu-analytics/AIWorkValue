# SQL analysis guide

SQL is used for sample diagnostics, descriptive comparisons and independently calculated business scenarios. Python performs the adjusted regression and robust inference. The dialect is SQLite with window functions and math functions; the project's Python 3.12 SQLite build supports both. No database server is required.

Read the generated [SQL analysis report](../reports/SQL_Analysis.md) for a compact business interpretation, or [all aggregate query outputs](../reports/sql-summaries.json) for exact values.

## Query map

| SQL file | Analytical question | Skills demonstrated |
|---|---|---|
| [00 · Analysis layer](00_analysis_layer.sql) | What common definitions should every query reuse? | Constrained input tables, reusable views, UNION ALL, staged CTEs, CROSS JOIN |
| [01 · Sample funnel](01_sample_funnel.sql) | Where are records excluded? | LAG, FIRST_VALUE, denominator handling |
| [02 · Group coverage](02_group_coverage.sql) | How much outcome data is available in each assigned group? | Conditional aggregation, NULL handling |
| [03 · Baseline balance](03_baseline_balance.sql) | Were observed baseline scores similar in the retained sample? | Long-form transformation, sample variance, self-join, standardized mean differences |
| [04 · Paired changes](04_paired_changes.sql) | How did complete pairs change from baseline? | Reusable view, group aggregation, self-join, unadjusted change contrasts |
| [05 · Design coverage](05_design_coverage.sql) | How are assignment and task order distributed across design strata? | GROUP BY, SUM OVER PARTITION BY |
| [06 · Adoption and follow-up](06_adoption_and_followup.sql) | What share responded, and what share of respondents used AI? | COUNT versus AVG, missingness-aware denominators |
| [07 · Business scenarios](07_business_scenarios.sql) | What capacity value do three sets of assumptions imply? | Querying a staged value model, costs and payback |
| [08 · Break-even](08_break_even.sql) | How much verification, seat cost or task volume can the case support? | Algebraic boundaries, CASE, NULLIF, zero-denominator guards |
| [09 · Sensitivity grid](09_sensitivity_grid.sql) | How does another minute of verification change value? | LAG within scenario partitions, scenario classification |
| [10 · Data quality](10_data_quality.sql) | Are identifiers, design fields, times and rating ranges valid? | Invariant checks, UNION ALL, DISTINCT |
| [Original introductory queries](study_analysis.sql) | What are the basic group means and response counts? | Introductory aggregation; retained for comparison |

## Run locally

From the project root, after installing dependencies:

```bash
make download
make run       # builds participants and runs the full SQL layer
make sql       # reruns only SQL after the initial reconstruction
make notebook  # includes executed SQL examples
```

The local database is `data/processed/study.sqlite`. It contains the participant table, three aggregate/configuration tables and two analysis views. Input assumptions and the historical time-effect estimate are imported from the documented Python outputs; SQL calculates the commercial answers independently. Participant records and the database are never committed.

## Reconciliation

Three named scenarios and all 36 sensitivity points must match Python's commercial calculations within a strict floating-point tolerance. Tests also check sample-variance standardization, missing outcome pairs, follow-up nonresponse and zero-seat boundaries. `make check` runs these tests without downloading research data, using clearly labeled mathematical fixtures and committed aggregate assumptions.

## Task-specific extension

[weekly_status_email.sql](extensions/weekly_status_email.sql) adds a separate nine-case frequency/checking comparison. It uses an in-memory input table, a CROSS JOIN of explicit assumptions and staged CTE calculations. Run `make extension`; the [scenario configuration](../data/scenarios/weekly_status_email.json) and committed historical effect are sufficient, so no participant data is required. See the [case results and explanation](../reports/extensions/Weekly_Status_Email.md).

## Interpretation

- SQL's difference in changes is descriptive and unadjusted; it is not the primary ANCOVA coefficient or its uncertainty interval.
- Balance is assessed among retained primary-arm cases with observed baselines, so it does not prove the absence of attrition bias.
- Missing follow-up responses must not become recorded non-use.
- Commercial outputs remain hypothetical capacity value. No current price or realized savings is claimed.
- The SQL extension was added after the primary estimates were known; it is not an additional preregistered analysis.

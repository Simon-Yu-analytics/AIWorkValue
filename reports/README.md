# Research outputs

- [14-page research and BI report](AIWorkValue_Research_Report.pdf): study design, effects, robustness, heterogeneity, business model, weekly-email extension, data warehouse, numerical verification and Dashboard.
- [Executive memo](Executive_Memo.md): evidence, assumptions and a bounded-pilot recommendation.
- [results.json](results.json): aggregate model records, uncertainty, descriptive results, commercial scenarios and run provenance.
- [data-audit.json](data-audit.json): the reconstruction and sample-flow audit.
- [SQL analysis report](SQL_Analysis.md): coverage, balance, paired changes and independently calculated commercial boundaries.
- [sql-summaries.json](sql-summaries.json): ten named SQL result sets, four introductory query results and Python/SQL reconciliation.
- [Weekly status-email extension](extensions/Weekly_Status_Email.md): nine hypothetical task-frequency/checking cases, a chart and exact JSON/CSV outputs.
- [Research validation](Research_Validation.md): independent HC3 matrix/interval checks and exploratory heterogeneity interpretation.
- [warehouse-summary.json](warehouse-summary.json): aggregate dimensional counts, JOIN/grain checks, missingness and dashboard KPIs.
- [pipeline-audit.json](pipeline-audit.json): Extract → Transform → Validate → Load → Analyze stage status.

Run `make run` to rebuild statistical and SQL outputs from local source files. Run `make report` to regenerate the figures and PDF from aggregate results, or `make notebook` to rebuild the executed walkthrough from the local analysis data. `make check` validates committed deliverables without downloading participant data.

After the initial reconstruction, `make sql` rebuilds just the main SQL layer and its reports. `make extension` rebuilds the task-specific example from committed aggregate inputs without participant data. Primary regression estimates are unchanged.

Primary models have different analytic denominators: 346 time observations and 352 quality observations, from 359 retained people in the primary incentive arms. The complete reconstructed retained sample contains 453 participants. None of these numbers is interchangeable.

Commercial outputs represent hypothetical capacity value under documented assumptions, not actual company profit. The source experiment was conducted by Noy and Zhang; AIWorkValue contributes independent reanalysis and a commercial extension.

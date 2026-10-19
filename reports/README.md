# Research outputs

- [10-page research report](AIWorkValue_Research_Report.pdf): study design, effects, robustness, heterogeneity, adoption and commercial interpretation.
- [Executive memo](Executive_Memo.md): evidence, assumptions and a bounded-pilot recommendation.
- [results.json](results.json): aggregate model records, uncertainty, descriptive results, commercial scenarios and run provenance.
- [data-audit.json](data-audit.json): the reconstruction and sample-flow audit.
- [sql-summaries.json](sql-summaries.json): aggregate SQL tables.

Run `make run` to rebuild statistical and SQL outputs from local source files. Run `make report` to regenerate the figures and PDF from aggregate results, or `make notebook` to rebuild the executed walkthrough from the local analysis data. `make check` validates committed deliverables without downloading participant data.

Primary models have different analytic denominators: 346 time observations and 352 quality observations, from 359 retained people in the primary incentive arms. The complete reconstructed retained sample contains 453 participants. None of these numbers is interchangeable.

Commercial outputs represent hypothetical capacity value under documented assumptions, not actual company profit. The source experiment was conducted by Noy and Zhang; AIWorkValue contributes independent reanalysis and a commercial extension.

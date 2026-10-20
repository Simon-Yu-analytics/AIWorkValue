# Business summary: AI writing assistance

**Main takeaway:** AI improved time and writing scores in this historical experiment, but that does not establish a profitable purchase for a new company. A sensible next investigation would measure one suitable writing workflow's task frequency and additional checking time.

**Evidence.** An independent reconstruction of the Noy–Zhang public experiment retains 453 participants. In the non-fixed-time arms, adjusted assignment contrasts among available cases are -10.34 minutes (95% interval -12.58 to -8.10; N=346) and +0.70 writing-grade points on a 1–7 scale (+0.47 to +0.93; N=352). Change-score, objective-duration and alternative grading checks support the direction of these results.

**Interpretation.** The historical experiment concerns short professional-writing tasks and early-2023 technology. It does not establish current-model performance, factual accuracy, whole-job productivity or company profit. Differential attrition limits a full-sample interpretation. The analysis uses assigned access, not a selected group of actual AI users.

**Additional observation.** Exploratory comparisons suggest larger quality gains at lower baseline writing scores. These are supplementary findings with limited subgroup evidence, not the main basis for the business recommendation.

**Worked business example.** Imagine 100 offered seats in a 200-person company, supporting recurring internal updates, summaries and routine emails. Under the [illustrative assumptions](../docs/BUSINESS_ASSUMPTIONS.md), the model produces about $700/month of net capacity value and an operating seat-cost ceiling of about $32/month. Statistical time-effect uncertainty alone gives approximately -$610 to +$2,010/month; uncertainty in the assumptions is additional. Extra checking above about 2.6 minutes/task removes the positive base operating case. These figures are hypothetical, not a client result or a current price recommendation.

**Next measurement.** Choose one recurring writing task and record full time to an acceptable result, including checking and rework, alongside a simple quality rubric and actual task frequency. Replace the cost assumptions with observed costs before drawing a purchase conclusion. Released capacity is not automatically a cash saving.

**Task-specific check.** The [weekly status-email extension](extensions/Weekly_Status_Email.md) assumes a 10-minute baseline, caps gross savings at that duration, and adds 0.5 revision minutes plus expected rework of 20% × 3 minutes. With all seat/support costs charged to this workflow, four tasks/month and one extra checking minute give about −$2,284/month net capacity value; 20 tasks give about +$581/month. At the higher volume, three checking minutes produce about −$1,752/month. These are conditional capacity values; even the positive point case crosses zero when only the historical effect uncertainty is propagated. No new email experiment, actual company outcome or current price recommendation is claimed.

**BI delivery.** A validated five-dimension/two-fact SQLite model supplies SQL marts, statistical input and public aggregate KPIs. The Streamlit application separates experimental results from adjustable business assumptions. Key uniqueness, foreign keys, fact grain, repeated loads and SQL/Python agreement are checked. This improves reproducibility and decision inspection; it does not add evidence of a real deployment.

Source: Noy and Zhang, Science (2023), DOI 10.1126/science.adh2586; author replication package OSF `xd7qw`. This project contributes reanalysis and a commercial extension; it did not conduct the original experiment.

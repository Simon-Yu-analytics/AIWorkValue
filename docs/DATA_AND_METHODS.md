# Data, reconstruction and interpretation

## Provenance

The original researchers are Shakked Noy and Whitney Zhang. Their study and author-hosted OSF package are linked in the README. `data/source-manifest.json` records exact URLs, byte counts and SHA-256 hashes. The OSF node's `node_license` was null when checked; raw files and participant-level derivatives are not redistributed. The authors' ReadMe states that participant IDs were replaced by random hashes.

The loader reads selected analysis columns from the survey rather than loading essay text, salaries or unrelated free-text responses. CSV exports are decoded with Latin-1 because some source byte sequences are not valid UTF-8; numeric fields and identifiers used here are ASCII. No rows are skipped to suppress decoding errors.

## Sample flow

1. 786 raw survey records.
2. 523 completed records that did not decline consent.
3. 505 earliest unique submissions.
4. 499 after six documented first-task/duplicate flags.
5. 457 after the source quality-check sheets.
6. 453 after excluding participants who had already graded essays.

The quality-check code is normalized from 3 to 1 as documented. The main grading sheet takes priority; the retry sheet fills missing participants. First-task flags are read as data from the downloaded source code, which is never executed.

359 retained people are in the linear/convex arms. The fixed-time arm is excluded from the primary time analysis because task time was constrained by design. Missing baseline/post observations create separate model denominators: 346 for time and 352 for quality. Raw survey records must not be called 786 randomized study participants.

## Minimal data dictionary

| Analysis variable | Source / derivation | Meaning |
|---|---|---|
| assignment | treatment | Randomized AI offer/onboarding assignment, 0/1 |
| a_first | a_first | Randomized order of the two occupational tasks |
| primary_arm | incentive_arm in linear/convex | Appropriate arms for time comparisons |
| time_pre, time_post | sum of time1_4…7 / time2_4…7 | Self-reported minutes; all four components required |
| page_pre, page_post | task A/B page submission durations / 60, mapped by task order | Objective page minutes; may include inactive time |
| grade_pre, grade_post | mean paired valid overall_a/overall_b ratings, mapped by order | Human-rated writing quality, scale 1–7 |
| used_ai | usedgpt mapped to yes/no | Post-randomization use outcome, not a sample filter |
| followup_used_ai | completed follow-up usedgpt_job | Self-reported workplace use among respondents |

## Quality ratings

Exclude the documented test grader, retry grades, invalid ratings and graders who had completed the task survey before grading. Require a valid A/B rating pair. Average eligible paired ratings per participant. This differs from the paper's main rater-level specification and data-dependent grader-correlation exclusions.

The paired-grader sensitivity model includes grader fixed effects, occupation-specific task-order slopes and incentive-arm controls, with standard errors clustered by participant. Redundant categorical columns are avoided and model-matrix rank is checked before inference.

## Estimation

Primary models: post outcome on assignment, its own baseline, occupation × task order and incentive arm. HC3 robust covariance and t-based confidence intervals are used. Two co-primary assignment tests receive Holm adjustment. The results are not an exact reproduction of every author coefficient.

Sensitivity models include unadjusted post differences, baseline changes, log(1+time), objective page time, all incentive arms for quality, and paired-grader fixed effects. The primary outcome is not winsorized or selectively trimmed.

Baseline-score heterogeneity uses a pooled pre-treatment mean for the continuous interaction and a pooled median for visual groups. It is exploratory. A significant result in one group and a nonsignificant result in another is not itself a test of group differences; inspect the interaction instead.

## Interpretation limits

- Assignment effects are estimated among retained available cases. Survey completion differs between groups; baseline adjustment does not guarantee removal of attrition bias.
- Selecting actual AI users would condition on a post-assignment choice and is deliberately avoided.
- Quality scores describe rated writing, not audited factual accuracy or customer outcomes.
- Follow-up use is self-reported and missing for some participants.
- Short writing tasks, incentives, selected occupations and early-2023 technology limit transfer to a new company or current tools.
- Business inputs beyond the estimated time effect are hypothetical. The displayed financial range propagates statistical time-effect uncertainty only.

## Contribution boundaries

Original researchers: experiment, data collection, task design and original findings. This project: independently ported cleaning, simplified estimators, robustness checks, SQL analysis, documented commercial extension and reproducible communication.

## Task-specific sensitivity extension

The weekly status-email example varies eligible task frequency (4, 8, 20 per month) and incremental checking time (1, 3, 5 minutes), holding the other configured assumptions fixed. Its SQL calculation is checked against Python. It uses the historical estimate as an input and does not estimate a new email-writing effect. Full seat and support costs are allocated to this workflow; other paid-tool uses are omitted. Four weeks is a simplifying scenario convention, and actual task duration could make the historical saving inapplicable. The extension is exploratory and was added after the main results were known.

The BI upgrade adds an assumed 10-minute email baseline, caps gross transferred saving at that duration, and deducts 0.5 revision minutes plus expected rework of 20% × 3 minutes. These inputs are hypothetical and incremental beyond effort reflected in the source estimate. SQL and Python use the same cap and cost definitions. The original reference case uses a nonbinding 30-minute cap and zero additional revision/rework so its original value remains comparable. Changes in the revised email values are model-scope changes, not altered experimental outcomes.

## Warehouse and model-input validation

The reconstructed source frame is validated before dimensional loading. SQL creates five dimensions, two facts and a one-participant mart. Round-trip checks require that the mart exactly preserves the cleaned participant variables and missingness. Primary models then read this SQL mart; source-data matrix calculations independently verify the primary HC3 standard errors and t intervals. Foreign-key, grain and JOIN-count checks must pass. Time values above 180 minutes are flagged, not automatically excluded. The warehouse contains source-level participant data and stays local; only aggregate KPIs and audits are committed.

Continuous baseline-score interactions now also include exploratory Holm-adjusted p-values and conditional effects at baseline quartiles. Those intervals are pointwise, not simultaneous bands. Noisy baseline scores, regression-to-the-mean concerns and the bounded quality scale limit interpretation; no employee-ability or allocation claim is made.

## Differences from the initial analysis plan

The plan mentions willingness to pay, but no willingness-to-pay analysis is included in the final project. Those selected-user hypothetical responses would not provide a company purchase price or a market demand curve, so that topic is left outside the final scope. The paired-grader fixed-effect sensitivity model and the expanded SQL/task examples were added as supplementary checks after the initial plan; they are not presented as newly preregistered analyses. The two primary outcomes and their primary estimators remain as documented.

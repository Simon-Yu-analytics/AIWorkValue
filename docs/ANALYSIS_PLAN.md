# Analysis plan: independent reanalysis and business extension

Written 19 October 2026 before this project's outcome models are estimated. The original paper is already public and its main findings are known. This is a transparent analysis plan, not a new preregistration or an independent experiment.

## Question

How does being assigned access and onboarding to a generative AI writing tool affect time and rated quality in the historical experiment? What conditions would make similar work commercially worth piloting?

## Data and sample

Use the Noy and Zhang (2023) OSF replication package, project `xd7qw`. Respect consent, completion, duplicate, documented first-task quality and prior-grader exclusions. Retain a numbered sample-flow audit. Compare completion rates among consented linear/convex participants who reached the first-task assessment.

The primary productivity analysis excludes the fixed-time incentive arm because task time was constrained by design. Do not restrict the analysis to respondents who actually used AI: take-up is post-randomization. Treat estimates as assignment contrasts among retained available cases; differential attrition limits a full-sample intention-to-treat claim.

## Outcomes and estimators

- Co-primary outcomes: post-task self-reported minutes (sum of four workflow components) and mean overall quality rating on the 1-7 scale.
- Primary estimator: participant-level ANCOVA, `post ~ assignment + baseline + occupation × task_order + incentive_arm`, HC3 robust standard errors with t intervals.
- Quality ratings: average paired valid grader observations per participant. Retain all eligible graders rather than reproducing the paper's data-dependent grader-correlation exclusion. State this deliberate simplification and do not promise exact published coefficients.
- Multiplicity: show Holm-adjusted p-values for the two primary assignment contrasts, alongside effect sizes and 95% intervals. Business decisions use magnitude and uncertainty, not a p-value threshold alone.

## Prespecified sensitivity checks

Compare unadjusted post-task differences, changes from baseline with design controls, log-time ANCOVA, objective page-duration ANCOVA, and inclusion of the fixed-time arm for quality only. No outcome-dependent trimming in the primary analysis.

## Exploratory extensions

Use the baseline writing grade, centered at its pooled mean, in an assignment interaction. Show lower/higher baseline-score groups using the pooled pre-treatment median. These are writing-task scores, not general employee ability labels. Small subgroups do not justify personalized employment decisions.

Describe two-week self-reported workplace use and follow-up response by assigned group. Nonresponse and self-report limit the interpretation. Show willingness to pay only among respondents who were asked and answered; hypothetical selected-user responses are not a market demand curve.

## Commercial extension

Convert the assignment-based minutes estimate into hypothetical capacity value using explicit assumptions for eligible task frequency, rollout coverage, transferability to a new setting, additional verification time, labor value and costs. Do not multiply the assignment effect by the experiment's take-up rate a second time. Distinguish released capacity from realized cash savings.

No current-model benchmark, original field trial, production deployment or realized business savings will be claimed. The experiment occurred in early 2023 using the technology available then.

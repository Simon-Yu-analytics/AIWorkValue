# Research card: AIWorkValue

## Intended use

An educational business analytics project for evaluating historical experimental evidence and designing an enterprise writing-workflow pilot. Intended readers are researchers, business analysts and portfolio reviewers. The commercial model supports explicit scenario discussion, not an automated investment or personnel decision.

## Original evidence and contribution

Original experiment: Noy and Zhang (2023), Science 381, 187–192, DOI [10.1126/science.adh2586](https://doi.org/10.1126/science.adh2586). Source materials: [OSF xd7qw](https://osf.io/xd7qw/).

The original authors designed the tasks, randomized the intervention, collected the data and published the research. AIWorkValue independently reconstructs the sample in Python, compares estimators, summarizes data in SQL and extends the estimates into explicitly hypothetical business scenarios. It is not a new experiment or an exact reproduction of every author specification.

## Population, intervention and estimand

- Population: selected professionals performing short occupation-specific writing tasks in early 2023.
- Intervention: assignment to AI access and onboarding between the baseline and post-task exercises.
- Primary comparison: assigned intervention versus control in the retained linear/convex incentive arms, among cases with the outcome and required covariates.
- Primary outcomes: self-reported post-task completion minutes and mean paired human writing rating on a 1–7 scale.
- Retained sample: 453; primary arms: 359; time model: 346; quality model: 352.

Selecting only actual AI users would condition on post-assignment behavior and is avoided. The available-case estimand must not be described as an unqualified full-sample intention-to-treat estimate.

## Estimation and evaluation

ANCOVA controls for the outcome's own baseline, occupation × randomized task order and incentive arm. Primary uncertainty uses HC3 robust covariance and t intervals; two primary assignment tests receive Holm adjustment. Model matrices must have full column rank.

Sensitivity checks compare unadjusted outcomes, changes, log time, objective page duration, inclusion of the fixed-time arm for quality, and paired-grader fixed effects with participant-clustered uncertainty. Baseline-score interactions and follow-up use are exploratory.

## Main outputs

Time: −10.34 minutes, 95% interval −12.58 to −8.10. Writing rating: +0.70 points, 95% interval +0.47 to +0.93. These are this project's adjusted historical assignment contrasts; they do not measure current-model performance.

The business model converts the time effect into capacity value under assumptions about rollout, eligible task volume, transferability, verification effort and costs. It preserves negative outcomes and separates statistical uncertainty from uncertain commercial inputs. Study take-up is already reflected in the assignment effect and is not multiplied in again.

## Main failure modes

- Differential completion and exclusions can bias a retained-sample comparison.
- Task order must be mapped correctly: A is not always baseline.
- Human writing quality is not factual accuracy or compliance.
- Objective page time can include inactivity, and self-reported minutes have measurement error.
- Historical short-task effects may not transfer to present-day tools or a new workflow.
- Exploratory baseline writing scores are not general employee ability labels.
- Released capacity does not automatically become a cash saving.

## Distribution and reproduction

Raw materials and participant-level derivatives remain local and are excluded from Git and the ZIP. Author download URLs and hashes are recorded in the manifest. Committed aggregate outputs, notebook, figures and report can be checked offline after installing dependencies. Full data reconstruction requires separately downloading the author-hosted files.

See [data and methods](DATA_AND_METHODS.md), [analysis plan](ANALYSIS_PLAN.md) and [third-party notices](../THIRD_PARTY_NOTICES.md).

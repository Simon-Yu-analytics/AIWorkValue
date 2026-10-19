# Task extension: weekly project-status email

**Question:** would a paid AI tool cover its recurring cost if employees used it only to draft a weekly internal project-status email? This is a worked sensitivity exercise, not an email-writing experiment or an observed company outcome.

## What changed?

The original base case assumes 20 eligible tasks per offered employee/month and 2 extra checking minutes/task. This extension varies task frequency (4, 8, 20) and extra checking (1, 3, 5 minutes). Other configured costs and the assumed 50% transfer of the historical effect stay fixed. Four weeks and twenty working days are simplifying scenario conventions, not measured calendar averages. Higher frequencies represent a broader set of comparable status-writing tasks.

The calculation charges all seat and support costs to this workflow. It does not value other uses of a shared subscription. A short email may take less time than the assumed saving: in that case the extrapolation is unsuitable. No email baseline time has been measured here.

## Results

| Tasks/person/month | Extra checking minutes/task | Net capacity hours/month | Net capacity value/month |
|---:|---:|---:|---:|
| 4 | 1 | 27.8 | $-2,027 |
| 4 | 3 | 14.5 | $-2,494 |
| 4 | 5 | 1.1 | $-2,960 |
| 8 | 1 | 55.6 | $-1,054 |
| 8 | 3 | 28.9 | $-1,987 |
| 8 | 5 | 2.3 | $-2,921 |
| 20 | 1 | 139.0 | $1,865 |
| 20 | 3 | 72.3 | $-469 |
| 20 | 5 | 5.7 | $-2,802 |

![Frequency and review sensitivity](../../figures/extensions/weekly_status_email.png)

## Why does the conclusion change?

A low-frequency task creates fewer opportunities to recover the monthly seat cost. More checking also reduces the useful minutes gained from each task. The recurring cost stays $3,000/month across these cases; 1 of 9 cases have positive net capacity value at the selected point estimate. A negative value does not mean writing becomes slower; it can mean that time value fails to cover the recurring bill.

With 4 tasks/month and 1 extra checking minute(s), the model gives **$-2,027/month net capacity value**. With 20 tasks and the same checking effort, it gives **$1,865/month**. Holding frequency at 20 but changing checking to 3 minutes gives **$-469/month**. These are conditional illustrations, not measured savings.

The CSV/JSON also carry ranges propagating only the historical time-effect interval. They do not capture uncertain transferability, task duration, frequency or cost allocation. No new statistical effect was estimated for email writing.

## What would be useful to measure next?

For one real writing workflow, record task frequency and full time to an acceptable result, including checking and rework. Use a simple quality rubric to prevent speed from masking worse output. Determine whether the tool would be purchased for this task alone or shared across other uses. These measurements have not been collected in this project.

## Reproduce and inspect

Run `make extension` from the project root; no participant data is required. Edit the [scenario configuration](../../data/scenarios/weekly_status_email.json), inspect the [SQL](../../sql/extensions/weekly_status_email.sql), or read the [exact JSON](weekly_status_email.json) and [CSV](weekly_status_email.csv). All nine SQL cases are checked against the Python capacity-value function. This extension was added after the historical main results were known.

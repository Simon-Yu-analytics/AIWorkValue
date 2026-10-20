# The business example and its assumptions

## A specific, hypothetical use case

Consider a company where some employees regularly draft internal project updates, meeting summaries and routine emails. The question is whether giving writing-tool access to 100 people would release enough useful time to cover the cost.

This is a worked example, not a client engagement. No company supplied these inputs, no employees were interviewed for this project, and no pilot was conducted. The original experiment covered occupation-specific writing tasks rather than this exact company workflow, so applying its estimate here requires an explicit assumption.

## What comes from data, and what does not?

| Input | Base value | Basis and reason for including it | What a real evaluation would measure |
|---|---|---|---|
| Historical assignment effect | About 10.3 minutes saved per study task | Estimated from the public experiment; uncertainty interval about 8.1–12.6 minutes saved | Full time to accepted output in the new workflow |
| Employees / offered-seat coverage | 200 / 50%, giving 100 seats | Chosen to make the scale of the example clear; not a measured company characteristic | Number of people doing suitable tasks and requiring a paid seat |
| Eligible tasks per offered employee/month | 20 | Illustrates roughly one suitable task per working day; the frequency is not observed in the study | Task logs or a short diary, including tasks where AI cannot help |
| Share of historical time effect that transfers | 50% | A chosen sensitivity input, not a fitted parameter or evidence-based forecast; other values are tested | A comparison of comparable tasks with and without the tool |
| Additional checking time | 2 minutes/task | Incremental checking beyond workflow time already reflected in the study estimate; not all editing time should be charged twice | Checking and rework attributable to AI output |
| Baseline task duration | 30 minutes in the reference case | A round illustrative cap, not a company measurement; it does not bind the reference saving | Full original workflow time at acceptable quality |
| Additional revision and expected rework | 0 in the reference case | Keeps the original reference result comparable; the email extension explicitly includes these costs | Incremental correction/rework beyond source-study workflow effort |
| Value of employee time | $35/hour | An illustrative value for released capacity, not a wage estimate or automatic budget saving | Relevant loaded cost and how released time would actually be used |
| Seat cost | $25/month | A hypothetical input, not a current vendor price or product recommendation | A quote for the actual plan and number of paid seats |
| Fixed support cost | $500/month | A simplified allowance for ongoing administration/support; no actual invoice is claimed | Actual recurring support and administration effort |
| Initial setup | $3,000 | An illustrative training/setup allowance; it affects simple payback, not the operating break-even calculation | Actual one-time training, configuration and onboarding effort |

The sensitivity analysis varies transferability and extra checking time because these are particularly uncertain and directly affect the value of each task. The remaining assumptions are still uncertain even though the displayed grid holds them fixed.

## How to read the answer

Under the base assumptions, the calculation produces about **106 hours of released capacity and $700 of net capacity value per month**. This is a model result, not realized savings. A result such as $698.03 in a machine-readable file is arithmetic precision, not evidence that the business inputs are known to the cent.

The operating case turns nonpositive when additional checking exceeds about **2.6 minutes/task**, or when eligible task volume falls below about **16 tasks per offered employee/month**, with other base assumptions held fixed. These are useful quantities to investigate, not universal thresholds.

The next practical step would be to measure task frequency and full checking time for one narrow workflow. The project does not establish a reason to purchase tools for an entire company today.

## Bounded email-workflow model

The email extension uses a separate, explicit **10-minute baseline**, **0.5 revision minutes** and **20% rework probability × 3 rework minutes**. These are assumptions, not observed task characteristics. Gross saving is `min(historical assignment minutes × transferability, baseline duration)`. Net saving subtracts review, revision and expected rework; AI workflow duration equals baseline minus net saving. This prevents impossible savings and permits a slower AI workflow if overhead outweighs the saving.

At four tasks/month and one review minute, net capacity value is about −$2,284/month; at 20 tasks with the same review it is about +$581/month. At three review minutes and 20 tasks, it is about −$1,752/month. These figures replace the earlier email calculation that omitted explicit revision/rework. The historical primary effects and original reference case are unchanged.

Review/revision/rework inputs must represent additional overhead beyond the time already reflected in the source estimate, avoiding double-counting ordinary editing. Dashboard defaults use this bounded workflow with two review minutes; this differs from the original reference case and is identified as a selected scenario.

## Deliberately limited scope

The model does not estimate company revenue, quality-related financial benefits, a full procurement budget or organizational change costs. Quality is analyzed separately rather than assigned an invented dollar value. More detailed finance should be added only if credible company inputs become available.

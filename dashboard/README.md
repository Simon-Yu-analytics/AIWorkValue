# Interactive business intelligence dashboard

Run from the repository root after installing `requirements.txt`:

```bash
make dashboard
```

Open the printed local URL, normally `http://127.0.0.1:8501`. The committed aggregate outputs are sufficient; no source-data download, model API key or paid BI license is required to explore the app. Full warehouse rebuilding is a separate `make download && make run` workflow.

| View | What it shows | What changes interactively |
|---|---|---|
| Experiment Overview | Retained versus primary-arm samples, assignment/period means, fact-row grain and integrity | Occupation filter for descriptive aggregates |
| Productivity Analysis | Primary time/quality effects, 95% intervals, robustness and exploratory baseline-score contrasts | Expandable detailed results; primary models remain full-sample estimates |
| Business Decision | Offered seats, costs, expected workflow time, net capacity value, interval propagation and break-even boundaries | Baseline duration, task frequency, review, revision, rework probability/time, costs and transferability |

The business page caps transferred savings at the assumed original task duration. It then subtracts incremental checking, revision and expected rework. A negative net capacity value is retained and explained. One-time setup cost changes the illustrative capacity-value payback, while recurring monthly value stays separate; this is not cash-investment payback. With zero offered seats, per-seat and task-volume boundaries are undefined and fixed operating costs remain. The heatmap varies task frequency and review while holding other selected assumptions fixed. Downloading a scenario exports its explicit assumptions and calculation.

The app reads public aggregate snapshots only. It does not expose participant records or silently refit a subgroup causal model when an occupation is selected. Cache keys include input-file versions so a regenerated aggregate snapshot is picked up on rerun.

## Hosting

The repository contains a runnable Streamlit application and actual preview screenshots. GitHub alone does not host this Python server. An optional Streamlit-compatible host can use `dashboard/app.py` as the entrypoint with the repository requirements. This project does not claim a public hosted app until such deployment is actually completed.

## Interpretation

Historical short-task evidence, present-day workflow assumptions and realized company benefits are different things. Writing scores do not establish factual accuracy. The displayed financial range propagates the historical time-effect interval only and is not a confidence interval for business profit. Current tool prices and actual company performance are not measured here.

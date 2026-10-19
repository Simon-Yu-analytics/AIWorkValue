# AIWorkValue

[**Read the analysis report →**](reports/AIWorkValue_Research_Report.pdf) · [Business summary](reports/Executive_Memo.md) · [Executed notebook](notebooks/01_experiment_to_business.ipynb) · [SQL findings](reports/SQL_Analysis.md)

[Specific task extension: weekly project-status email](reports/extensions/Weekly_Status_Email.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Analysis checks](https://github.com/Simon-Yu-analytics/AIWorkValue/actions/workflows/ci.yml/badge.svg)](https://github.com/Simon-Yu-analytics/AIWorkValue/actions/workflows/ci.yml)

**A personal business analytics project asking when AI writing assistance might be worth its cost.**

The project reanalyzes a public experiment on writing time and quality, then uses a hypothetical business example to examine tool costs and extra checking time. Python handles the statistical models; SQL supports data checks, group comparisons and business calculations.

The original experiment was conducted by **Shakked Noy and Whitney Zhang**. This project contributes a separate data reconstruction, analysis and business extension; it did not collect the original data or work with a real company.

## The question

An AI tool may help someone draft an email faster, but a company also needs to consider checking the output, how often suitable tasks occur and the cost of paid seats. The question is: **under what assumptions does a task-level time saving become useful business value?**

A worked example considers employees drafting routine internal updates, summaries and emails. The [assumption notes](docs/BUSINESS_ASSUMPTIONS.md) distinguish measured experimental effects from chosen inputs. No company interviews, deployment or realized savings are claimed.

## Main findings

The cleaning pipeline reconstructs 453 retained participants. The primary incentive arms contain 359 people; available baseline/post observations yield different model denominators.

| Outcome | Adjusted AI-assignment contrast | 95% interval | Analytic N |
|---|---:|---:|---:|
| Completion time | **−10.3 minutes** | −12.6 to −8.1 | 346 |
| Writing quality, 1–7 scale | **+0.70 points** | +0.47 to +0.93 | 352 |

These are historical assignment comparisons among retained available cases. They are not estimates of all employees' productivity or the performance of current AI tools. A writing score is not a factual-accuracy score.

In the hypothetical base case, the calculation gives about **106 hours of released capacity and $700 of net capacity value per month**. The result turns nonpositive above about **2.6 extra checking minutes/task**, with the other assumptions fixed. Uncertainty in the historical time estimate alone also takes the scenario across zero.

The practical takeaway is to measure **task frequency and total checking time for one workflow** before drawing a purchasing conclusion. Released capacity is not automatically a cash saving.

## Analysis and figures

```text
Public experimental data
        ↓
Sample reconstruction and task-order mapping
        ↓
SQL checks: coverage, baseline differences, paired changes
        ↓
Python: baseline-adjusted time and quality regressions
        ↓
Checks using alternative measurements and specifications
        ↓
Hypothetical costs, checking time and break-even calculation
```

| Experimental result | Business sensitivity |
|---|---|
| ![Adjusted time and quality contrasts](figures/02_primary_effects.png) | ![Value under transferability and extra-checking assumptions](figures/07_business_sensitivity.png) |

The [11-page report](reports/AIWorkValue_Research_Report.pdf) presents the analysis and task extension. The [figure gallery](figures/README.md) contains the additional plots.

## Methods and scope

The core analysis uses two regressions: one for completion time and one for writing quality. Each compares assigned AI access with control while accounting for the participant's baseline result and the experiment's design variables. It reports robust 95% intervals and adjusts the two primary p-values for multiple testing.

The analysis keeps assignment as the comparison rather than selecting only actual AI users. It also maps randomized task order correctly: task A is not always the baseline task. Comparisons using changes from baseline and objective page duration help check the results.

Additional models, including grader fixed effects, baseline-score interactions and follow-up adoption, are supplementary exercises. They are separated from the core reading path in [project scope](docs/PROJECT_SCOPE.md). Full definitions and estimator differences from the original paper are in [data and methods](docs/DATA_AND_METHODS.md).

## SQL work

Start with these five queries to follow the main argument:

| Question | Query | SQL used |
|---|---|---|
| How much outcome data is available in each group? | [Group coverage](sql/02_group_coverage.sql) | Conditional aggregation and NULL handling |
| Were observed baseline scores similar? | [Baseline balance](sql/03_baseline_balance.sql) | CTEs, sample variance and a self-join |
| How did complete pairs change? | [Paired changes](sql/04_paired_changes.sql) | Reusable view, aggregation and a self-join |
| What do the three cost examples imply? | [Business scenarios](sql/07_business_scenarios.sql) | A staged value calculation from assumptions |
| What checking time and task volume cover the cost? | [Break-even boundaries](sql/08_break_even.sql) | CASE, NULLIF and boundary calculations |

Supporting queries cover the sample funnel, design coverage, follow-up use, a sensitivity grid and data-quality checks, including window functions. The [SQL guide](sql/README.md) explains each file; the [generated findings](reports/SQL_Analysis.md) show aggregate results. SQL business calculations are checked against Python across three named cases and 36 sensitivity points.

SQL's unadjusted change comparison is distinct from the Python regression. The SQL extension was added after the main estimates were known and is not a preregistered analysis.

## A concrete task extension

For a [weekly project-status email](reports/extensions/Weekly_Status_Email.md), the extension compares 4, 8 and 20 eligible tasks/month with 1, 3 and 5 extra checking minutes/task, holding other assumptions fixed. Charging the full subscription/support cost to this workflow makes weekly-only use negative in all three checking cases. More frequent eligible work can support the cost when checking effort is low.

The [editable configuration](data/scenarios/weekly_status_email.json), [SQL query](sql/extensions/weekly_status_email.sql), Python cross-check and notebook make this a reproducible calculation. This is not a new experiment on emails. A short email may not support the assumed historical saving, and other uses of the same paid tool would change the cost allocation.

## Reproduce

Use Python 3.12+ from the repository root:

```bash
git clone https://github.com/Simon-Yu-analytics/AIWorkValue.git
cd AIWorkValue
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
make check
```

`make check` tests calculations and validates committed aggregate outputs. It does not download participant data. To rebuild the analysis:

```bash
make download   # download author-hosted files and verify hashes
make run        # reconstruct data, fit models and run SQL
make sql        # optionally rerun just SQL
make extension  # rebuild the specific task example from aggregate inputs
make report     # rebuild figures and the PDF
make notebook   # rebuild the executed walkthrough
make check
```

The initial download needs internet access. No paid model API, GPU or Stata license is needed. To work interactively, open the notebook in a Jupyter-capable editor with `ipykernel` installed in the same environment. `make package` creates a shareable ZIP without raw or participant-level data.

## Files to explore

```text
notebooks/        executed walkthrough
sql/              analysis views, core queries and supporting checks
src/aiworkvalue/   data reconstruction, models and business calculations
reports/          PDF, business summary, SQL findings and aggregate outputs
figures/          eight main plots plus the task-extension chart
docs/             scope, assumptions, methods and project walkthrough
data/             source manifest; raw/ and processed/ stay local
scripts/          download, analysis and artifact builders
tests/            calculation and boundary tests
```

The [project walkthrough](docs/WALKTHROUGH.md) provides a suggested reading and reproduction path. The [research card](docs/RESEARCH_CARD.md) and [analysis plan](docs/ANALYSIS_PLAN.md) contain additional detail.

## Data and limitations

Source: Noy and Zhang (2023), [*Experimental evidence on the productivity effects of generative artificial intelligence*](https://doi.org/10.1126/science.adh2586), Science 381, 187–192. [Author-hosted replication materials](https://osf.io/xd7qw/).

- The experiment concerns short writing tasks and early-2023 technology. Transfer to a new workflow is uncertain.
- Completion differences, sample exclusions and missing outcomes limit a full-sample intention-to-treat interpretation.
- Human writing ratings do not establish factual accuracy or company performance. Baseline-score subgroup results are exploratory.
- Business assumptions are illustrative. The displayed financial range propagates statistical time-effect uncertainty only, not all business uncertainty.
- The primary quality estimator is deliberately simpler than the paper's full specification; no exact replication of every published coefficient is claimed.

The source OSF node declared no license in its metadata when inspected. Raw files and participant-level derivatives are downloaded separately and excluded from Git and the archive. See [data policy](data/README.md) and [third-party notices](THIRD_PARTY_NOTICES.md).

## Project ownership and next step

**Junhui (Simon) Yu — AIWorkValue portfolio project.** AI tools assisted code and draft preparation. The original study is credited above; [project scope](docs/PROJECT_SCOPE.md) distinguishes implemented work from personal understanding and future extensions.

The weekly-email sensitivity extension is implemented. A useful next step is to reproduce it and measure task frequency and total checking time for a real workflow; those observations have not been collected here. Original project code and documentation use the [MIT License](LICENSE).

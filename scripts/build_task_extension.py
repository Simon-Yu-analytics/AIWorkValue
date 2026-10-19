"""Build a specific, explicitly hypothetical task example from aggregate inputs."""
from pathlib import Path
import csv
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from aiworkvalue.task_extension import evaluate_task_extension


def main():
    results = json.loads((ROOT / "reports/results.json").read_text())
    config = json.loads((ROOT / "data/scenarios/weekly_status_email.json").read_text())
    sql = (ROOT / "sql/extensions/weekly_status_email.sql").read_text()
    extension = evaluate_task_extension(results["primary"][0], config, sql)
    frequencies = sorted({row["tasks_per_employee_month"] for row in extension["cases"]})
    reviews = sorted(config["extra_review_minutes"])
    by_case = {(row["tasks_per_employee_month"], row["review_minutes"]): row
               for row in extension["cases"]}
    low_frequency, high_frequency = frequencies[0], frequencies[-1]
    low_review, middle_review = reviews[0], reviews[len(reviews) // 2]
    weekly = by_case[(low_frequency, low_review)]
    frequent = by_case[(high_frequency, low_review)]
    checked = by_case[(high_frequency, middle_review)]
    original = results["business"]["base"]["assumptions"]
    transfer = config["base_assumptions"]["transferability"]
    positive_cases = sum(row["net_capacity_value"] > 0 for row in extension["cases"])
    target = ROOT / "reports/extensions"
    target.mkdir(exist_ok=True)
    (target / "weekly_status_email.json").write_text(json.dumps(extension, indent=2, allow_nan=False) + "\n")
    with (target / "weekly_status_email.csv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(extension["cases"][0]))
        writer.writeheader()
        writer.writerows(extension["cases"])

    figure_dir = ROOT / "figures/extensions"
    figure_dir.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    for index, review in enumerate(reviews):
        color = ("#237F78", "#173449", "#C37B43")[index % 3]
        rows = [row for row in extension["cases"] if row["review_minutes"] == review]
        ax.plot([row["tasks_per_employee_month"] for row in rows],
                [row["net_capacity_value"] for row in rows], marker="o", color=color,
                label=f"{review:g} extra checking min/task")
    ax.axhline(0, color="#667B87", linewidth=0.8, linestyle="--")
    ax.set_xticks(frequencies)
    ax.set_ylabel("USD/month net capacity value (hypothetical)")
    ax.set_xlabel(f"Eligible tasks per offered employee/month; {weekly['offered_seats']:g} offered seats")
    ax.set_title("Task frequency changes the cost case", loc="left", fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout()
    fig.savefig(figure_dir / "weekly_status_email.png", dpi=180, facecolor="white")
    plt.close(fig)

    lines = [
        "# Task extension: weekly project-status email\n",
        "**Question:** would a paid AI tool cover its recurring cost if employees used it only to draft a weekly internal project-status email? This is a worked sensitivity exercise, not an email-writing experiment or an observed company outcome.\n",
        "## What changed?\n",
        f"The original base case assumes {original['eligible_tasks_per_employee_month']:g} eligible tasks per offered employee/month and {original['additional_review_minutes']:g} extra checking minutes/task. This extension varies task frequency ({', '.join(f'{v:g}' for v in frequencies)}) and extra checking ({', '.join(f'{v:g}' for v in reviews)} minutes). Other configured costs and the assumed {transfer:.0%} transfer of the historical effect stay fixed. {config['frequency_note']}\n",
        "The calculation charges all seat and support costs to this workflow. It does not value other uses of a shared subscription. A short email may take less time than the assumed saving: in that case the extrapolation is unsuitable. No email baseline time has been measured here.\n",
        "## Results\n",
        "| Tasks/person/month | Extra checking minutes/task | Net capacity hours/month | Net capacity value/month |\n|---:|---:|---:|---:|",
    ]
    for row in extension["cases"]:
        lines.append(f"| {row['tasks_per_employee_month']:g} | {row['review_minutes']:g} | {row['capacity_hours']:.1f} | ${row['net_capacity_value']:,.0f} |")
    lines.extend([
        "\n![Frequency and review sensitivity](../../figures/extensions/weekly_status_email.png)\n",
        "## Why does the conclusion change?\n",
        f"A low-frequency task creates fewer opportunities to recover the monthly seat cost. More checking also reduces the useful minutes gained from each task. The recurring cost stays ${weekly['recurring_cost']:,.0f}/month across these cases; {positive_cases} of {len(extension['cases'])} cases have positive net capacity value at the selected point estimate. A negative value does not mean writing becomes slower; it can mean that time value fails to cover the recurring bill.\n",
        f"With {low_frequency:g} tasks/month and {low_review:g} extra checking minute(s), the model gives **${weekly['net_capacity_value']:,.0f}/month net capacity value**. With {high_frequency:g} tasks and the same checking effort, it gives **${frequent['net_capacity_value']:,.0f}/month**. Holding frequency at {high_frequency:g} but changing checking to {middle_review:g} minutes gives **${checked['net_capacity_value']:,.0f}/month**. These are conditional illustrations, not measured savings.\n",
        "The CSV/JSON also carry ranges propagating only the historical time-effect interval. They do not capture uncertain transferability, task duration, frequency or cost allocation. No new statistical effect was estimated for email writing.\n",
        "## What would be useful to measure next?\n",
        "For one real writing workflow, record task frequency and full time to an acceptable result, including checking and rework. Use a simple quality rubric to prevent speed from masking worse output. Determine whether the tool would be purchased for this task alone or shared across other uses. These measurements have not been collected in this project.\n",
        "## Reproduce and inspect\n",
        "Run `make extension` from the project root; no participant data is required. Edit the [scenario configuration](../../data/scenarios/weekly_status_email.json), inspect the [SQL](../../sql/extensions/weekly_status_email.sql), or read the [exact JSON](weekly_status_email.json) and [CSV](weekly_status_email.csv). All nine SQL cases are checked against the Python capacity-value function. This extension was added after the historical main results were known.\n",
    ])
    (target / "Weekly_Status_Email.md").write_text("\n".join(lines))
    print(f"Built {len(extension['cases'])} task cases, SQL/Python reconciliation, narrative and chart.")


if __name__ == "__main__":
    main()

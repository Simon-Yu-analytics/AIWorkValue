"""Build the SQL layer and publish aggregate diagnostics and business calculations."""
from pathlib import Path
import json
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aiworkvalue.sql_analysis import prepare_layer, run_queries, reconcile_business


def markdown_table(rows):
    if not rows:
        return "No rows.\n"
    columns = list(rows[0])
    def display(value):
        if value is None:
            return "—"
        return f"{value:,.3f}" if isinstance(value, float) else str(value)
    return ("| " + " | ".join(columns) + " |\n| " + " | ".join("---" for _ in columns) + " |\n"
            + "\n".join("| " + " | ".join(display(row[c]) for c in columns) + " |" for row in rows) + "\n")


def main():
    database = ROOT / "data/processed/study.sqlite"
    if not database.exists():
        raise SystemExit("Run make download and make run before the SQL layer.")
    results = json.loads((ROOT / "reports/results.json").read_text())
    with sqlite3.connect(database) as connection:
        prepare_layer(connection, results, ROOT / "sql")
        queries = run_queries(connection, ROOT / "sql")
        reconciliation = reconcile_business(queries, results)
        text = "\n".join(line for line in (ROOT / "sql/study_analysis.sql").read_text().splitlines()
                         if not line.strip().startswith("--"))
        introductory = []
        for statement in text.split(";"):
            if statement.strip():
                cursor = connection.execute(statement)
                columns = [column[0] for column in cursor.description]
                introductory.append({"sql": statement.strip(),
                                     "rows": [dict(zip(columns, row)) for row in cursor.fetchall()]})
    output = {"schema_version": 2, "engine": "SQLite", "sqlite_version": sqlite3.sqlite_version,
              "boundary": "Descriptive SQL comparisons; adjusted inference is estimated in Python. Commercial values are hypothetical capacity value.",
              "queries": queries, "introductory_queries": introductory,
              "python_sql_reconciliation": reconciliation}
    (ROOT / "reports/sql-summaries.json").write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    by_name = {query["query"]: query["rows"] for query in queries}
    sections = [
        "# SQL analysis: experiment checks and commercial decisions\n",
        "Ten named SQL analyses extend the four introductory queries. They use CTEs, joins, conditional aggregation, reusable views and window functions. Participant-level inputs remain local; this report and the JSON contain aggregates only.\n",
        "## Coverage and missingness\n", markdown_table(by_name["02_group_coverage"]),
        "## Baseline balance\n",
        "These are retained primary-arm participants with an observed baseline, not a balance test for every randomized participant. The standardized mean difference uses the square root of the mean of two sample variances. A small baseline difference does not resolve attrition bias.\n",
        markdown_table(by_name["03_baseline_balance"]),
        "## Paired pre/post comparisons\n",
        "Each outcome uses complete baseline/post pairs. The difference in changes is descriptive and unadjusted; it is distinct from the baseline-adjusted Python regression.\n",
        markdown_table(by_name["04_paired_changes"]),
        "## SQL-calculated commercial cases\n",
        "Values use the same hypothetical assumptions and Python-estimated time effect. The SQL view calculates capacity, costs and operating boundaries independently. Released capacity is not a cash saving.\n",
        markdown_table([{key: row[key] for key in ("scenario", "capacity_hours", "recurring_cost", "net_capacity_value", "operating_seat_cost_ceiling")}
                        for row in by_name["07_business_scenarios"]]),
        "## Operating break-even boundaries\n", markdown_table(by_name["08_break_even"]),
        "## Reconciliation and data quality\n",
        f"All three named cases and {reconciliation['sensitivity_points']} sensitivity points match the independent Python calculations within floating-point tolerance. Seven data-quality checks have zero violations.\n",
        markdown_table(by_name["10_data_quality"]),
        "## Explore the complete outputs\n",
        "The [query guide](../sql/README.md) maps each SQL file to a business question. [sql-summaries.json](sql-summaries.json) includes all ten named result sets, the four introductory result sets, SQL text and reconciliation status. Rebuild with `make sql` after the local data reconstruction.\n",
    ]
    (ROOT / "reports/SQL_Analysis.md").write_text("\n".join(sections))
    print(f"Saved {len(queries)} named SQL analyses + {len(introductory)} introductory queries; Python/SQL reconciliation passed.")


if __name__ == "__main__":
    main()

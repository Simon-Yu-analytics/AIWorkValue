"""Execute transparent SQL diagnostics and independently reconcile business arithmetic."""
import math
from pathlib import Path


def prepare_layer(connection, results, sql_dir):
    connection.executescript((Path(sql_dir) / "00_analysis_layer.sql").read_text())
    for table in ("analysis_sample_flow", "time_effect", "business_assumptions"):
        connection.execute(f"DELETE FROM {table}")
    connection.executemany("INSERT INTO analysis_sample_flow VALUES (?, ?, ?)",
                           [(i + 1, row["stage"], row["n"])
                            for i, row in enumerate(results["audit"]["sample_flow"])])
    time = results["primary"][0]
    connection.execute("INSERT INTO time_effect VALUES (1, ?, ?, ?)",
                       (-time["coefficient"], -time["ci95"][1], -time["ci95"][0]))
    columns = ("employees", "rollout_coverage", "eligible_tasks_per_employee_month",
               "transferability", "additional_review_minutes", "loaded_hourly_value",
               "assumed_seat_cost_month", "fixed_operating_cost_month", "setup_cost",
               "baseline_task_minutes", "revision_minutes", "rework_probability", "rework_minutes")
    assumptions = [(name, "named", results["business"][name]["assumptions"])
                   for name in ("conservative", "base", "upside")]
    for i, point in enumerate(results["business"]["sensitivity"]):
        scenario = dict(results["business"]["base"]["assumptions"])
        scenario.update(transferability=point["transferability"],
                        additional_review_minutes=point["review_minutes"])
        assumptions.append((f"grid_{i:02d}", "grid", scenario))
    connection.executemany(
        "INSERT INTO business_assumptions VALUES (" + ",".join("?" for _ in range(len(columns)+2)) + ")",
        [(name, kind, *(a[c] for c in columns)) for name, kind, a in assumptions])


def query_file(connection, path):
    cursor = connection.execute(Path(path).read_text())
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def run_queries(connection, sql_dir):
    return [{"query": path.stem, "sql": path.read_text(), "rows": query_file(connection, path)}
            for path in sorted(Path(sql_dir).glob("[0-9][0-9]_*.sql"))
            if not path.name.startswith("00_")]


def reconcile_business(queries, results):
    by_name = {query["query"]: query["rows"] for query in queries}
    fields = {"capacity_hours": "capacity_hours_month", "gross_capacity_value": "capacity_value_month",
              "recurring_cost": "recurring_cost_month", "net_capacity_value": "net_capacity_value_month",
              "operating_seat_cost_ceiling": "operating_break_even_seat_cost",
              "capacity_payback_months": "capacity_value_payback_months"}
    errors = []
    for row in by_name["07_business_scenarios"]:
        python = results["business"][row["scenario"]]
        for sql_key, python_key in fields.items():
            a, b = row[sql_key], python[python_key]
            if a is None or b is None:
                if a != b:
                    raise AssertionError(f"Undefined-value mismatch: {row['scenario']} / {sql_key}")
            else:
                if not math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-8):
                    raise AssertionError(f"Business mismatch: {row['scenario']} / {sql_key}")
                errors.append(abs(a - b))
    reference = {(row["transferability"], row["review_minutes"]): row["net_capacity_value_month"]
                 for row in results["business"]["sensitivity"]}
    for row in by_name["09_sensitivity_grid"]:
        b = reference[(row["transferability"], row["additional_review_minutes"])]
        if not math.isclose(row["net_capacity_value"], b, rel_tol=1e-10, abs_tol=1e-8):
            raise AssertionError("Sensitivity mismatch")
        errors.append(abs(row["net_capacity_value"] - b))
    if any(row["violations"] != 0 for row in by_name["10_data_quality"]):
        raise AssertionError("SQL data quality check failed")
    return {"status": "passed", "business_cases": 3, "sensitivity_points": len(reference),
            "max_absolute_numeric_difference": max(errors, default=0)}

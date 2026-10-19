"""A bounded task-frequency exercise, with independent SQL/Python arithmetic."""
from dataclasses import replace
import math
import sqlite3
from .business import Scenario, value_case


def evaluate_task_extension(primary_time, config, sql_text):
    if not config["frequencies"] or not config["extra_review_minutes"]:
        raise ValueError("At least one frequency and review setting are required.")
    base = Scenario(**config["base_assumptions"])
    saved = -primary_time["coefficient"]
    inputs, python_cases = [], {}
    for frequency in config["frequencies"]:
        tasks = frequency["tasks_per_employee_month"]
        for review in config["extra_review_minutes"]:
            scenario = replace(base, eligible_tasks_per_employee_month=tasks,
                               additional_review_minutes=review)
            python_cases[(tasks, review)] = value_case(saved, scenario)
            inputs.append((frequency["label"], tasks, review))
    if len(python_cases) != len(inputs):
        raise ValueError("Frequency/review combinations must be unique.")

    parameters = dict(config["base_assumptions"], minutes_saved=saved,
                      saved_low=-primary_time["ci95"][1], saved_high=-primary_time["ci95"][0])
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE extension_inputs (frequency TEXT, tasks_per_employee_month REAL, review_minutes REAL)")
        connection.executemany("INSERT INTO extension_inputs VALUES (?, ?, ?)", inputs)
        cursor = connection.execute(sql_text, parameters)
        columns = [column[0] for column in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]

    errors = []
    for row in rows:
        expected = python_cases[(row["tasks_per_employee_month"], row["review_minutes"])]
        for sql_key, python_key in (("capacity_hours", "capacity_hours_month"),
                                    ("recurring_cost", "recurring_cost_month"),
                                    ("net_capacity_value", "net_capacity_value_month")):
            error = abs(row[sql_key] - expected[python_key])
            if not math.isclose(row[sql_key], expected[python_key], rel_tol=1e-10, abs_tol=1e-8):
                raise AssertionError(f"SQL/Python task-case mismatch: {sql_key}")
            errors.append(error)
    return {"task": config["task"], "status": config["status"], "config": config,
            "historical_minutes_saved": saved, "sql": sql_text, "cases": rows,
            "reconciliation": {"status": "passed", "cases": len(rows),
                               "max_absolute_difference": max(errors, default=0)}}

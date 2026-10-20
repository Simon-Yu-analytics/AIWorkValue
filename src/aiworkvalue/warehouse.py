"""Validated atomic snapshot loads into a small, explicit star schema."""
from pathlib import Path
import os
import sqlite3
import tempfile
import numpy as np
import pandas as pd

SOURCE_COLUMNS = ["prolific_pid", "assignment", "occupation", "incentive_arm", "a_first", "primary_arm",
                  "time_pre", "time_post", "grade_pre", "grade_post", "page_pre", "page_post",
                  "used_ai", "followup_used_ai"]


def validate_participants(frame):
    if frame.empty or frame.prolific_pid.isna().any() or not frame.prolific_pid.is_unique or frame.prolific_pid.astype(str).str.strip().eq("").any():
        raise ValueError("Retained participant IDs must be nonempty, present and unique.")
    if not frame.assignment.isin([0, 1]).all() or not frame.a_first.isin([0, 1]).all():
        raise ValueError("Invalid randomized design fields.")
    if frame.occupation.isna().any() or frame.occupation.astype(str).str.strip().eq("").any() or not frame.incentive_arm.isin(["linear", "convex", "exact"]).all():
        raise ValueError("Missing or unknown dimension values.")
    if not (frame.primary_arm == frame.incentive_arm.isin(["linear", "convex"])).all():
        raise ValueError("Primary-arm flag contradicts incentive assignment.")
    missing, outliers = {}, {}
    for col in ["time_pre", "time_post", "page_pre", "page_post", "grade_pre", "grade_post"]:
        values = frame[col].dropna()
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"Nonfinite or negative outcome: {col}")
        if col.startswith("grade") and not values.between(1, 7).all():
            raise ValueError(f"Writing rating outside 1–7: {col}")
        missing[col] = int(frame[col].isna().sum())
        if not col.startswith("grade"):
            outliers[col] = int((values > 180).sum())
    for col in ["used_ai", "followup_used_ai"]:
        if not frame[col].dropna().isin([0, 1]).all():
            raise ValueError(f"Invalid usage indicator: {col}")
    return {"status": "passed", "rows": len(frame), "missing_outcomes": missing,
            "time_above_180_minutes": outliers,
            "outlier_policy": "Flag for inspection; do not trim or impute. Threshold is a QC rule, not an exclusion criterion."}


def load_warehouse(frame, database, sql_dir):
    validation = validate_participants(frame)
    database = Path(database)
    database.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix="warehouse-", suffix=".sqlite", dir=database.parent)
    os.close(handle)
    connection=None
    try:
        with sqlite3.connect(temporary) as connection:
            connection.execute("PRAGMA foreign_keys=ON")
            frame[SOURCE_COLUMNS].to_sql("stg_participant", connection, index=False, if_exists="replace")
            connection.executescript((Path(sql_dir) / "01_schema.sql").read_text())
            connection.executescript((Path(sql_dir) / "02_transform.sql").read_text())
            checks = [dict(zip(["check_name", "violations"], row)) for row in
                      connection.execute((Path(sql_dir) / "03_integrity.sql").read_text())]
            foreign = connection.execute("PRAGMA foreign_key_check").fetchall()
            if foreign or any(row["violations"] != 0 for row in checks):
                raise ValueError("Warehouse integrity failed; existing snapshot preserved.")
            mart = pd.read_sql_query("SELECT * FROM mart_participant ORDER BY prolific_pid", connection)
            expected = frame[SOURCE_COLUMNS].sort_values("prolific_pid").reset_index(drop=True)
            for col in SOURCE_COLUMNS:
                if col in ("prolific_pid", "occupation", "incentive_arm"):
                    if mart[col].tolist() != expected[col].tolist():
                        raise ValueError(f"Warehouse round-trip changed {col}")
                elif not np.array_equal(mart[col].to_numpy(dtype=float), expected[col].to_numpy(dtype=float), equal_nan=True):
                    raise ValueError(f"Warehouse round-trip changed {col}")
            cursor = connection.execute("SELECT * FROM mart_experiment_kpi ORDER BY assignment, occupation, period_name")
            names = [c[0] for c in cursor.description]
            kpis = [dict(zip(names, row)) for row in cursor.fetchall()]
            tables = ["dim_participant", "dim_assignment", "dim_occupation", "dim_incentive", "dim_period", "fact_outcome", "fact_usage"]
            counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in tables}
            connection.execute("DROP TABLE stg_participant")
        connection.close()
        os.replace(temporary, database)
    finally:
        if connection is not None:
            connection.close()
        Path(temporary).unlink(missing_ok=True)
    return {"validation": validation, "table_rows": counts, "foreign_key_violations": len(foreign),
            "integrity_checks": checks, "kpis": kpis,
            "load_strategy": "Validated atomic full snapshot; deterministic natural-key ordering; no appending on rerun.",
            "outcome_grain": "One retained participant x baseline/post period",
            "usage_grain": "One retained participant"}

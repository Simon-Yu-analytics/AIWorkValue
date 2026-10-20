"""Extract -> Transform -> Validate -> Load -> Analyze, reusing the study loader."""
from pathlib import Path
import hashlib
import json
import sqlite3
import pandas as pd
from .data import load_study
from .warehouse import validate_participants, load_warehouse
from .analysis import run_analysis
from .business import business_results


def run_pipeline(root):
    root = Path(root)
    manifest = json.loads((root / "data/source-manifest.json").read_text())
    for asset in manifest["assets"]:
        path = root / asset["path"]
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != asset["sha256"]:
            raise ValueError(f"Missing or changed source asset: {asset['path']}. Run make download.")
    frame, audit, grades = load_study(root, return_grades=True)
    validation = validate_participants(frame)
    warehouse = load_warehouse(frame, root / "data/processed/study.sqlite", root / "sql/warehouse")
    with sqlite3.connect(root/"data/processed/study.sqlite") as connection:
        model_frame=pd.read_sql_query("SELECT * FROM mart_participant ORDER BY prolific_pid",connection)
    model_frame["primary_arm"]=model_frame.primary_arm.astype(bool)
    model_frame["time_change"]=model_frame.time_post-model_frame.time_pre
    model_frame["grade_change"]=model_frame.grade_post-model_frame.grade_pre
    results = run_analysis(model_frame, grades)
    results["audit"] = audit
    results["business"] = business_results(results["primary"][0])
    run = {"stages": [
        {"stage": "Extract", "status": "passed", "verified_assets": len(manifest["assets"])},
        {"stage": "Transform", "status": "passed", "retained_participants": len(frame)},
        {"stage": "Validate", "status": "passed", "details": validation},
        {"stage": "Load", "status": "passed", "table_rows": warehouse["table_rows"]},
        {"stage": "Analyze", "status": "passed", "primary_model_n": [r["n"] for r in results["primary"]]},
    ], "distribution": "Only aggregates are published; source and participant-level warehouse remain local."}
    return model_frame, results, warehouse, run

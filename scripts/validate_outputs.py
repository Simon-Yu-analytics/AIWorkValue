"""Offline integrity checks for aggregate research deliverables."""
from pathlib import Path
import json,math
from aiworkvalue.sql_analysis import reconcile_business
from aiworkvalue.task_extension import evaluate_task_extension
ROOT=Path(__file__).resolve().parents[1]


def main():
    r=json.loads((ROOT/"reports/results.json").read_text())
    assert r["audit"]["retained_participants"]==453
    assert r["audit"]["primary_arm_participants"]==359
    for row in r["primary"]+r["robustness"]+r["heterogeneity"]["interaction_tests"]:
        assert row["ci95"][0]<=row["coefficient"]<=row["ci95"][1]
        assert math.isfinite(row["standard_error"]) and 0<=row["p_value"]<=1
    assert [x["n"] for x in r["primary"]]==[346,352]
    warehouse=json.loads((ROOT/"reports/warehouse-summary.json").read_text())
    assert warehouse["table_rows"]["dim_participant"]==453
    assert warehouse["table_rows"]["fact_outcome"]==906
    assert warehouse["table_rows"]["fact_usage"]==453
    assert warehouse["foreign_key_violations"]==0
    assert all(row["violations"]==0 for row in warehouse["integrity_checks"])
    pipeline=json.loads((ROOT/"reports/pipeline-audit.json").read_text())
    assert [row["stage"] for row in pipeline["stages"]]==["Extract","Transform","Validate","Load","Analyze"]
    assert all(row["status"]=="passed" for row in pipeline["stages"])
    research=json.loads((ROOT/"reports/research-validation.json").read_text())
    assert len(research["primary_model_checks"])==len(r["primary"])==2
    assert research["sample_audit"]==r["audit"]
    assert research["interaction_tests"]==r["heterogeneity"]["interaction_tests"]
    assert research["conditional_effects"]==r["heterogeneity"]["conditional_effects"]
    for audit,model in zip(research["primary_model_checks"],r["primary"]):
        assert audit["model"]==model["name"] and audit["status"]=="passed"
        assert audit["n"]==model["n"] and audit["rank"]==audit["design_columns"]
        assert math.isclose(audit["independent_hc3_se"],model["standard_error"],rel_tol=0,abs_tol=1e-10)
        assert len(audit["independent_ci95"])==len(model["ci95"])==2
        assert all(math.isclose(a,b,rel_tol=0,abs_tol=1e-10)
                   for a,b in zip(audit["independent_ci95"],model["ci95"]))
    sql=json.loads((ROOT/"reports/sql-summaries.json").read_text())
    assert sql["schema_version"]==2 and len(sql["queries"])==10
    assert reconcile_business(sql["queries"],r)["status"]=="passed"
    by_name={q["query"]:q["rows"] for q in sql["queries"]}
    coverage=by_name["02_group_coverage"]
    assert sum(row["time_pairs"] for row in coverage)==r["primary"][0]["n"]
    assert sum(row["quality_pairs"] for row in coverage)==r["primary"][1]["n"]
    for q in sql["queries"]:
        assert q["sql"]==(ROOT/"sql"/(q["query"]+".sql")).read_text()
    for key in ["conservative","base","upside"]:
        b=r["business"][key]
        assert math.isclose(b["capacity_value_month"]-b["recurring_cost_month"],b["net_capacity_value_month"])
    config=json.loads((ROOT/"data/scenarios/weekly_status_email.json").read_text())
    extension=evaluate_task_extension(r["primary"][0],config,(ROOT/"sql/extensions/weekly_status_email.sql").read_text())
    committed=json.loads((ROOT/"reports/extensions/weekly_status_email.json").read_text())
    assert extension==committed and len(extension["cases"])==9
    assert (ROOT/"figures/extensions/weekly_status_email.png").read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    notebook=json.loads((ROOT/"notebooks/01_experiment_to_business.ipynb").read_text())
    assert all(c.get("execution_count") for c in notebook["cells"] if c["cell_type"]=="code")
    assert len(list((ROOT/"figures").glob("*.png")))==8
    assert (ROOT/"reports/AIWorkValue_Research_Report.pdf").read_bytes().startswith(b"%PDF")
    assert (ROOT/"dashboard/app.py").is_file()
    assert (ROOT/"figures/dashboard/business_decision.jpg").read_bytes().startswith(b"\xff\xd8\xff")
    for file in ["reports/Executive_Memo.md","reports/SQL_Analysis.md","sql/README.md","docs/DATA_AND_METHODS.md","docs/ANALYSIS_PLAN.md"]:
        assert (ROOT/file).is_file()
    print("Validated warehouse, ETL stages, independent inference, SQL/Python cases, notebook, dashboard and report artifacts.")


if __name__=="__main__":main()

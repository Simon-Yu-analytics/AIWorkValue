"""Offline integrity checks for aggregate research deliverables."""
from pathlib import Path
import json,math
from aiworkvalue.sql_analysis import reconcile_business
ROOT=Path(__file__).resolve().parents[1]


def main():
    r=json.loads((ROOT/"reports/results.json").read_text())
    assert r["audit"]["retained_participants"]==453
    assert r["audit"]["primary_arm_participants"]==359
    for row in r["primary"]+r["robustness"]+r["heterogeneity"]["interaction_tests"]:
        assert row["ci95"][0]<=row["coefficient"]<=row["ci95"][1]
        assert math.isfinite(row["standard_error"]) and 0<=row["p_value"]<=1
    assert [x["n"] for x in r["primary"]]==[346,352]
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
    notebook=json.loads((ROOT/"notebooks/01_experiment_to_business.ipynb").read_text())
    assert all(c.get("execution_count") for c in notebook["cells"] if c["cell_type"]=="code")
    assert len(list((ROOT/"figures").glob("*.png")))==8
    assert (ROOT/"reports/AIWorkValue_Research_Report.pdf").read_bytes().startswith(b"%PDF")
    for file in ["reports/Executive_Memo.md","reports/SQL_Analysis.md","sql/README.md","docs/DATA_AND_METHODS.md","docs/ANALYSIS_PLAN.md"]:
        assert (ROOT/file).is_file()
    print("Validated sample, models, 10 SQL analyses, SQL/Python reconciliation, notebook and research deliverables.")


if __name__=="__main__":main()

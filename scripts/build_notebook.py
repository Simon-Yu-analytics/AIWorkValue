"""Create and execute an editable walkthrough; only aggregate outputs are saved."""
from pathlib import Path
import contextlib,io,json,os
ROOT=Path(__file__).resolve().parents[1]


def main():
    os.chdir(ROOT);cells=[];namespace={}
    def md(text):cells.append({"cell_type":"markdown","metadata":{},"source":text.splitlines(keepends=True)})
    def code(text):
        output=io.StringIO()
        with contextlib.redirect_stdout(output):exec(compile(text,"<research notebook>","exec"),namespace)
        cells.append({"cell_type":"code","metadata":{},"execution_count":sum(c["cell_type"]=="code" for c in cells)+1,
                      "source":text.splitlines(keepends=True),"outputs":[{"output_type":"stream","name":"stdout","text":output.getvalue().splitlines(keepends=True)}]})
    md("# AIWorkValue: From Experimental Evidence to a Business Decision\n\nIndependent reanalysis of the Noy–Zhang (2023) experiment with explicit commercial scenarios. This project did not conduct the original experiment or benchmark current AI products. First run `make download && make run` from the project root.")
    code('''from pathlib import Path
import json, sys, sqlite3
ROOT = Path.cwd()
if not (ROOT / "reports/results.json").exists(): ROOT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))
from aiworkvalue.data import load_study
d, audit = load_study(ROOT)
r = json.loads((ROOT / "reports/results.json").read_text())
for row in audit["sample_flow"]: print(row)
print("Primary incentive arms:", int(d.primary_arm.sum()))
''')
    md("## 1. Preserve the Assigned-Group Comparison\n\nActual AI use is a choice made after assignment, so it must not be used to select the treatment sample. The fixed-time incentive arm is excluded from the primary productivity comparison.")
    code('''with sqlite3.connect(ROOT / "data/processed/study.sqlite") as connection:
    q = """SELECT assignment, COUNT(*), ROUND(AVG(time_pre),2),
    ROUND(AVG(time_post),2), ROUND(AVG(grade_post),3)
    FROM participants WHERE primary_arm=1 GROUP BY assignment"""
    print("assignment / N / baseline minutes / post minutes / post grade")
    for row in connection.execute(q): print(row)
''')
    md("### SQL: From Sample Checks to Business Scenarios\n\nExecute the repository's SQL files directly. Paired changes are unadjusted descriptive comparisons, distinct from the regression estimates below. SQL independently calculates the commercial cases using the same assumptions and checks them against Python. Missing follow-up responses must not be treated as recorded non-use.")
    code('''from aiworkvalue.sql_analysis import query_file
with sqlite3.connect(ROOT / "data/processed/study.sqlite") as connection:
    for name in ("02_group_coverage.sql", "03_baseline_balance.sql", "04_paired_changes.sql"):
        print("\\n", name)
        for row in query_file(connection, ROOT / "sql" / name): print(row)
''')
    code('''with sqlite3.connect(ROOT / "data/processed/study.sqlite") as connection:
    for row in query_file(connection, ROOT / "sql/07_business_scenarios.sql"):
        expected = r["business"][row["scenario"]]["net_capacity_value_month"]
        assert abs(row["net_capacity_value"] - expected) < 1e-8
        print(row["scenario"], "SQL monthly net capacity value:", round(row["net_capacity_value"], 2))
sql_results = json.loads((ROOT / "reports/sql-summaries.json").read_text())
print("Python / SQL reconciliation:", sql_results["python_sql_reconciliation"])
''')
    md("## 2. Re-estimate a Primary Model\n\nAdjust for the baseline outcome, occupation by task order, and incentive arm. The coefficient is measured in minutes; a negative value means faster completion. Distinguish the retained available-case sample from the full randomized population.")
    code('''import statsmodels.formula.api as smf
primary = d[d.primary_arm].copy()
formula = "time_post ~ assignment + time_pre + C(occupation)*C(a_first) + C(incentive_arm)"
fit = smf.ols(formula, data=primary).fit(cov_type="HC3", use_t=True)
print("N:", int(fit.nobs))
print("Assignment coefficient (minutes):", round(fit.params["assignment"], 4))
print("95% interval:", fit.conf_int().loc["assignment"].round(4).tolist())
assert abs(fit.params["assignment"] - r["primary"][0]["coefficient"]) < 1e-8
''')
    md("![Primary effects](../figures/02_primary_effects.png)\n\nQuality is a difference in writing-rating points on a 1–7 scale, not factual accuracy.")
    code('''for row in r["primary"]:
    print(row["name"], "N=", row["n"], "effect=", round(row["coefficient"],3),
          "CI=", [round(x,3) for x in row["ci95"]], "Holm p=", row["holm_p_value"])
''')
    md("## 3. Robustness and Exploratory Differences\n\nDifferent within-group significance levels do not establish a difference between groups; inspect the interaction instead. Occupation and baseline writing scores should not become employee-ability rankings.")
    code('''for row in r["robustness"]:
    print(row["name"], "N=", row["n"], "effect=", round(row["coefficient"],3))
print("Exploratory interaction tests:")
for row in r["heterogeneity"]["interaction_tests"]:
    print(row["name"], round(row["coefficient"],3), [round(x,3) for x in row["ci95"]])
''')
    md("## 4. Change the Business Assumptions\n\nThe estimate describes a historical assignment effect. Task frequency, transferability, verification effort and seat costs are business assumptions. Vary additional checking time to see how the commercial conclusion can reverse.")
    code('''from aiworkvalue.business import Scenario, value_case
from dataclasses import replace
saved = -r["primary"][0]["coefficient"]
for review in (1, 2, 3, 4):
    case = value_case(saved, replace(Scenario(), additional_review_minutes=review))
    print("Additional review minutes:", review,
          "monthly net capacity value:", round(case["net_capacity_value_month"],2))
print("Released capacity is not automatically cash savings.")
''')
    md("![Business sensitivity](../figures/07_business_sensitivity.png)\n\n## 5. Task Extension: A Weekly Project-Status Email\n\nCompare 4, 8 and 20 eligible tasks per month with 1, 3 and 5 extra checking minutes per task, keeping other costs and the 50% transferability assumption fixed. This recalculates scenarios rather than conducting a new email experiment. All subscription and support costs are charged to this workflow; other subscription uses are not valued.")
    code('''from aiworkvalue.task_extension import evaluate_task_extension
config = json.loads((ROOT / "data/scenarios/weekly_status_email.json").read_text())
task_sql = (ROOT / "sql/extensions/weekly_status_email.sql").read_text()
extension = evaluate_task_extension(r["primary"][0], config, task_sql)
for row in extension["cases"]:
    print("tasks/month:", row["tasks_per_employee_month"],
          "extra checking minutes:", row["review_minutes"],
          "net capacity value:", round(row["net_capacity_value"], 2))
print("SQL/Python check:", extension["reconciliation"])
assert extension == json.loads((ROOT / "reports/extensions/weekly_status_email.json").read_text())
''')
    md("![Task frequency extension](../figures/extensions/weekly_status_email.png)\n\n**Interpretation:** weekly-only use can release time without covering a full month's costs. More eligible tasks can make a low-checking scenario positive. This is not a purchase conclusion: actual task duration, task frequency, verification and rework must be measured. A very short email may not support the assumed historical saving. See `reports/extensions/Weekly_Status_Email.md` for assumptions and results.")
    notebook={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":4}
    path=ROOT/"notebooks/01_experiment_to_business.ipynb";path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+"\n");print(path)


if __name__=="__main__":main()

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
    md("# AIWorkValue：真实实验数据怎样支持商业判断\n\n独立重分析 Noy–Zhang (2023) 实验，并作透明的商业情景延伸。不是本项目自行实施的实验，也不是当前模型性能测试。先从项目根目录运行 `make download && make run`。")
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
    md("## 1. 保留分配效应的比较\n\n实际是否使用 AI 是随机分配之后的选择，不能据此筛选处理组。固定时长组也不适合放入主要时间比较。")
    code('''with sqlite3.connect(ROOT / "data/processed/study.sqlite") as connection:
    q = """SELECT assignment, COUNT(*), ROUND(AVG(time_pre),2),
    ROUND(AVG(time_post),2), ROUND(AVG(grade_post),3)
    FROM participants WHERE primary_arm=1 GROUP BY assignment"""
    print("assignment / N / baseline minutes / post minutes / post grade")
    for row in connection.execute(q): print(row)
''')
    md("### SQL：从样本检查到商业情景\n\n下面直接执行仓库里的 SQL 文件。配对变化属于未调整的描述比较，不等于后面的回归系数。商业情景用相同假设独立计算，并与 Python 结果核对。缺失的随访回答不能当成没有使用 AI。")
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
    md("## 2. 自己重新估计一个主模型\n\n控制基线、职业×任务顺序及激励组。系数是分钟；负值代表更快。可用样本与原始随机入组总体要分开解释。")
    code('''import statsmodels.formula.api as smf
primary = d[d.primary_arm].copy()
formula = "time_post ~ assignment + time_pre + C(occupation)*C(a_first) + C(incentive_arm)"
fit = smf.ols(formula, data=primary).fit(cov_type="HC3", use_t=True)
print("N:", int(fit.nobs))
print("Assignment coefficient (minutes):", round(fit.params["assignment"], 4))
print("95% interval:", fit.conf_int().loc["assignment"].round(4).tolist())
assert abs(fit.params["assignment"] - r["primary"][0]["coefficient"]) < 1e-8
''')
    md("![Primary effects](../figures/02_primary_effects.png)\n\n质量的单位是 1–7 分量表上的分数差，不是事实准确率。")
    code('''for row in r["primary"]:
    print(row["name"], "N=", row["n"], "effect=", round(row["coefficient"],3),
          "CI=", [round(x,3) for x in row["ci95"]], "Holm p=", row["holm_p_value"])
''')
    md("## 3. 稳健性与探索性差异\n\n不要仅凭分组内显著与否判断两组差异；应看交互项。职业和基线写作分数也不应变成真实员工能力排行榜。")
    code('''for row in r["robustness"]:
    print(row["name"], "N=", row["n"], "effect=", round(row["coefficient"],3))
print("Exploratory interaction tests:")
for row in r["heterogeneity"]["interaction_tests"]:
    print(row["name"], round(row["coefficient"],3), [round(x,3) for x in row["ci95"]])
''')
    md("## 4. 亲自修改商业假设\n\n研究估计给出历史任务中的分配效应。任务频率、可迁移比例、复核成本和席位费用是商业假设。下面修改复核时间，展示商业结论怎样反转。")
    code('''from aiworkvalue.business import Scenario, value_case
from dataclasses import replace
saved = -r["primary"][0]["coefficient"]
for review in (1, 2, 3, 4):
    case = value_case(saved, replace(Scenario(), additional_review_minutes=review))
    print("Additional review minutes:", review,
          "monthly net capacity value:", round(case["net_capacity_value_month"],2))
print("Released capacity is not automatically cash savings.")
''')
    md("![Business sensitivity](../figures/07_business_sensitivity.png)\n\n## 5. 具体任务扩展：每周项目进度邮件\n\n把每月适用次数改为 4、8、20，把额外复核改为 1、3、5 分钟，其他成本和 50% 效果迁移假设保持一致。这里重新计算情景，不是重新做邮件实验。全部订阅和支持成本计入这一流程，没有计入订阅的其他用途。")
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
    md("![Task frequency extension](../figures/extensions/weekly_status_email.png)\n\n**怎样解释？** 每周一次的任务可能产生正的时间价值，但次数不足以抵消整个月的成本。任务更多时，低复核负担的情景才可能转正。这不是采购结论：需要实际测量原始任务时长、适用次数、复核和返工。如果实际写邮件只需很短时间，直接套用历史节省分钟数就不合理。详细假设和结果见 `reports/extensions/Weekly_Status_Email.md`。")
    notebook={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":4}
    path=ROOT/"notebooks/01_experiment_to_business.ipynb";path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+"\n");print(path)


if __name__=="__main__":main()

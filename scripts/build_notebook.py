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
    md("![Business sensitivity](../figures/07_business_sensitivity.png)\n\n## 你自己的延伸\n\n选择一种熟悉的写作工作，写清与实验任务的相同/不同之处。只改变一个有业务依据的假设，重建图表，并解释哪项新的实测最可能改变投入决策。明确标记推测，不虚构访谈、员工试验或公司收益。")
    notebook={"cells":cells,"metadata":{"kernelspec":{"display_name":"Python 3","language":"python","name":"python3"},"language_info":{"name":"python","version":"3.12"}},"nbformat":4,"nbformat_minor":4}
    path=ROOT/"notebooks/01_experiment_to_business.ipynb";path.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+"\n");print(path)


if __name__=="__main__":main()

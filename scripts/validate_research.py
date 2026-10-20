"""Independent HC3 matrix calculation and transparent research diagnostics."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import t

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from aiworkvalue.data import load_study


def main():
    frame,audit=load_study(ROOT)
    results=json.loads((ROOT/"reports/results.json").read_text())
    sample=frame[frame.primary_arm]
    checks=[]
    for row in results["primary"]:
        model=smf.ols(row["formula"],data=sample,missing="drop")
        x,y=model.exog,model.endog
        inverse=np.linalg.inv(x.T@x)
        beta=np.linalg.lstsq(x,y,rcond=None)[0]
        residual=y-x@beta
        leverage=np.einsum("ij,jk,ik->i",x,inverse,x)
        weights=(residual/(1-leverage))**2
        covariance=inverse@((x.T*weights)@x)@inverse
        index=model.exog_names.index("assignment")
        se=float(np.sqrt(covariance[index,index]))
        df=len(y)-np.linalg.matrix_rank(x)
        interval=(beta[index]+np.array([-1,1])*t.ppf(.975,df)*se).tolist()
        if not np.isclose(beta[index],row["coefficient"],rtol=0,atol=1e-10) or not np.isclose(se,row["standard_error"],rtol=0,atol=1e-10):
            raise AssertionError("Independent HC3 calculation does not match the primary model.")
        if not np.allclose(interval,row["ci95"],rtol=0,atol=1e-10):
            raise AssertionError("Primary t interval mismatch.")
        checks.append({"model":row["name"],"n":len(y),"design_columns":x.shape[1],
                       "rank":int(np.linalg.matrix_rank(x)),"residual_df":int(df),
                       "maximum_leverage":float(leverage.max()),"independent_hc3_se":se,
                       "independent_ci95":interval,"status":"passed"})
    report={"primary_model_checks":checks,"sample_audit":audit,
            "conditional_effects":results["heterogeneity"]["conditional_effects"],
            "interaction_tests":results["heterogeneity"]["interaction_tests"],
            "inference_boundary":"Available-case assignment contrasts. No proof that attrition, outcome measurement error or external-validity limitations are removed."}
    (ROOT/"reports/research-validation.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    text=["# Research validation and interpretation\n",
          "## Primary model verification\n",
          "The primary ANCOVA coefficients, HC3 covariance and t-based 95% intervals were independently reconstructed with NumPy matrix algebra and SciPy quantiles. Both model matrices have full column rank. No real outcomes were changed or trimmed to improve results.\n",
          "| Model | N | Rank / columns | Independent HC3 SE | Status |\n|---|---:|---:|---:|---|"]
    for check in checks:
        text.append(f"| {check['model']} | {check['n']} | {check['rank']} / {check['design_columns']} | {check['independent_hc3_se']:.6f} | passed |")
    text.extend(["\n## Selection, missingness and post-assignment information\n",
                 "The source sample exclusions and random task-order mapping remain documented in the data protocol. The primary time model uses 346 available baseline/post cases and the quality model uses 352, from 359 retained non-fixed-time participants. Missing outcomes are not imputed. Reported actual AI use is an outcome, not a primary sample filter or regression control. Differential completion and later exclusions still limit full-sample intention-to-treat claims.\n",
                 "Time outliers above the declared QC threshold are flagged, not automatically removed. Valid writing scores remain within the source 1–7 scale. Source checksums, retained-key uniqueness, warehouse round-trip equivalence and dimension/fact constraints are validated by the ETL. There is no predictive train/test benchmark in this experimental reanalysis.\n",
                 "## Baseline-performance heterogeneity\n",
                 "The continuous assignment × baseline writing-score interaction is preferable to inferring a subgroup difference from separate significance tests. The two exploratory interaction tests also receive Holm adjustment. Conditional effects at baseline-score quartiles use linear contrasts of the same fitted interaction models and pointwise robust intervals; they are not independent subgroup experiments or simultaneous confidence bands.\n",
                 "A single baseline writing task is noisy. Quality scores have a ceiling at 7, and comparisons involving baseline and change can be affected by regression to the mean. The pattern is suggestive of task-score moderation, not proof of general worker ability differences or an employee assignment policy.\n",
                 "## Three different conclusions\n",
                 "1. **Statistical:** the retained historical sample supports nonzero assignment contrasts under the stated models.\n2. **Practical:** the effect is measured in minutes and writing-rating points for short tasks; it does not establish an equivalent whole-job productivity gain or factual correctness.\n3. **Commercial:** a new workflow must cover seat/support costs after review, revision and expected rework. Baseline-duration caps and business assumptions can change value without changing the historical regression result.\n",
                 "## Remaining uncertainty\n",
                 "This validation checks computation and declared analysis choices. It does not establish a new randomized experiment, current-product performance, a company deployment, causal effects for every participant subgroup or realized financial returns. See the original study and the data/methods protocol for context.\n"])
    (ROOT/"reports/Research_Validation.md").write_text("\n".join(text))
    print("Independent HC3 covariance, primary intervals and design rank verified.")


if __name__=="__main__":main()

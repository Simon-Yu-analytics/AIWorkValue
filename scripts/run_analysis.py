"""Recreate sample, models, SQL-ready data and independent commercial scenarios."""
from pathlib import Path
import sys,json,platform,importlib.metadata
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from aiworkvalue.pipeline import run_pipeline


def main():
    d,result,warehouse,pipeline=run_pipeline(ROOT)
    result["meta"]={"project":"AIWorkValue","study":"Noy and Zhang (Science, 2023)","osf_project":"xd7qw",
                    "analysis_date":"2026-10-19","python":platform.python_version(),
                    "packages":{k:importlib.metadata.version(k) for k in ["numpy","pandas","scipy","statsmodels"]},
                    "claim":"Independent reanalysis plus commercial scenarios, not an original experiment or exact author-code replication."}
    (ROOT/"data/processed").mkdir(parents=True,exist_ok=True)
    d.to_csv(ROOT/"data/processed/participants.csv",index=False)
    (ROOT/"reports/results.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    (ROOT/"reports/data-audit.json").write_text(json.dumps(result["audit"],indent=2)+"\n")
    (ROOT/"reports/warehouse-summary.json").write_text(json.dumps(warehouse,indent=2,allow_nan=False)+"\n")
    (ROOT/"reports/pipeline-audit.json").write_text(json.dumps(pipeline,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"primary":result["primary"],"retained":len(d),"business_base":result["business"]["base"]},indent=2))


if __name__=="__main__":main()

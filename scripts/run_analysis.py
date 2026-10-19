"""Recreate sample, models, SQL-ready data and independent commercial scenarios."""
from pathlib import Path
import sys,json,hashlib,platform,importlib.metadata,sqlite3
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"src"))
from aiworkvalue.data import load_study
from aiworkvalue.analysis import run_analysis
from aiworkvalue.business import business_results


def main():
    manifest=json.loads((ROOT/"data/source-manifest.json").read_text())
    for asset in manifest["assets"]:
        if hashlib.sha256((ROOT/asset["path"]).read_bytes()).hexdigest()!=asset["sha256"]:
            raise ValueError("Source checksum mismatch: "+asset["path"])
    d,audit,grades=load_study(ROOT,return_grades=True)
    result=run_analysis(d,grades)
    result["audit"]=audit
    result["business"]=business_results(result["primary"][0])
    result["meta"]={"project":"AIWorkValue","study":"Noy and Zhang (Science, 2023)","osf_project":"xd7qw",
                    "analysis_date":"2026-10-19","python":platform.python_version(),
                    "packages":{k:importlib.metadata.version(k) for k in ["numpy","pandas","scipy","statsmodels"]},
                    "claim":"Independent reanalysis plus commercial scenarios, not an original experiment or exact author-code replication."}
    d.to_csv(ROOT/"data/processed/participants.csv",index=False)
    with sqlite3.connect(ROOT/"data/processed/study.sqlite") as con:
        cols=["prolific_pid","assignment","occupation","incentive_arm","a_first","primary_arm",
              "time_pre","time_post","grade_pre","grade_post","used_ai","followup_used_ai"]
        d[cols].to_sql("participants",con,if_exists="replace",index=False)
    (ROOT/"reports/results.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    (ROOT/"reports/data-audit.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps({"primary":result["primary"],"retained":len(d),"business_base":result["business"]["base"]},indent=2))


if __name__=="__main__":main()

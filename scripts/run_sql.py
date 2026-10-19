"""Run and save aggregate SQL summaries, not participant-level extracts."""
from pathlib import Path
import json,sqlite3
ROOT=Path(__file__).resolve().parents[1]
if __name__=="__main__":
    sql="\n".join(s for s in (ROOT/"sql/study_analysis.sql").read_text().splitlines() if not s.strip().startswith("--"))
    summaries=[]
    with sqlite3.connect(ROOT/"data/processed/study.sqlite") as con:
        for statement in sql.split(";"):
            if not statement.strip():continue
            c=con.execute(statement);cols=[d[0] for d in c.description]
            summaries.append({"sql":statement.strip(),"rows":[dict(zip(cols,r)) for r in c.fetchall()]})
    (ROOT/"reports/sql-summaries.json").write_text(json.dumps(summaries,indent=2)+"\n")
    print("Saved",len(summaries),"aggregate SQL tables.")

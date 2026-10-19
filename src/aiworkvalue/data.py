"""Auditable, minimal-column reconstruction of the public study sample."""
import json
from pathlib import Path
import re
import numpy as np
import pandas as pd


def dates(values):
    return pd.to_datetime(values, format="mixed", errors="coerce").dt.normalize()


def map_tasks(a, b, a_first):
    """Counterbalancing is essential: task A is not always the baseline."""
    return np.where(a_first == 1, a, b), np.where(a_first == 1, b, a)


def load_study(root: Path, return_grades: bool = False):
    raw = root/"data/raw"
    keys = {"prolific_pid","startdate","finished","consent","consent_exact","treatment","a_first",
            "occupation","incentive_arm","task_realism","usedgpt","chatgpt_wtp","usage",
            "task_a_timespent_pagesubmit","task_b_timespent_pagesubmit"}
    keys.update(f"time{n}_{k}" for n in (1,2) for k in (4,5,6,7))
    d = pd.read_csv(raw/"fullsurvey.csv", usecols=lambda c:c in keys, low_memory=False,encoding="latin-1")
    for c in keys-{"prolific_pid","startdate","occupation","incentive_arm","usage"}:
        if c in d:
            d[c] = pd.to_numeric(d[c],errors="coerce")
    d["task_date"] = dates(d.startdate)
    flow=[]
    def record(stage):
        flow.append({"stage":stage,"n":len(d),"control":int((d.treatment==0).sum()),"ai_offer":int((d.treatment==1).sum())})
    record("raw_survey_records")
    eligible_start = d[(d.incentive_arm.isin(["linear","convex"])) & (d.consent==1) & d.task_realism.notna()]
    attrition = [{"assignment":int(g),"reached_first_task":len(x),"finished":int((x.finished==1).sum()),
                  "completion_rate":float((x.finished==1).mean())} for g,x in eligible_start.groupby("treatment")]
    d = d[(d.finished==1) & (d.consent!=2) & (d.consent_exact!=2)].copy()
    record("completed_and_not_declined")
    task_dates = d.groupby("prolific_pid").task_date.min()
    d = d.sort_values(["prolific_pid","startdate"]).drop_duplicates("prolific_pid")
    record("unique_first_submission")
    # Read documented study exclusions as data; never execute upstream Stata code.
    code=(raw/"clean.do").read_text()
    block=code[code.index("gen plagiarism"):code.index("* dropping bad responses")]
    excluded=set(re.findall(r'prolific_pid=="([a-f0-9]{64})"',block))
    d=d[~d.prolific_pid.isin(excluded)].copy();record("documented_first_task_and_duplicate_flags")
    qchecks=[]
    for name in ("grading.xlsx","grading_retry.xlsx"):
        q=pd.read_excel(raw/name,usecols=["prolific_pid","qcheck"])
        q["qcheck"]=pd.to_numeric(q.qcheck,errors="coerce").replace(3,1)
        grouped=q.groupby("prolific_pid").qcheck.agg(["min","max"])
        qchecks.append(grouped)
    # Match the source's primary-sheet priority, falling back to the retry sheet.
    q=pd.concat(qchecks).loc[lambda x:~x.index.duplicated(keep="first")]
    d=d.join(q,on="prolific_pid")
    d=d[~((d["max"]>1)|(d["min"]<1))].copy();record("author_quality_check")
    long=pd.read_csv(raw/"grading_long_complete.csv",usecols=["grader_id","StartDate"],encoding="latin-1")
    long["grade_date"]=dates(long.StartDate)
    prior=long.groupby("grader_id").grade_date.min()
    d=d.join(prior.rename("prior_grade_date"),on="prolific_pid")
    d=d[~(d.task_date>d.prior_grade_date)].copy();record("exclude_prior_graders")
    assert d.prolific_pid.is_unique and d.treatment.isin([0,1]).all() and d.a_first.isin([0,1]).all()
    for n in (1,2):
        cols=[f"time{n}_{k}" for k in (4,5,6,7)]
        d[f"time_pre" if n==1 else "time_post"]=d[cols].sum(axis=1,min_count=4)
    d["page_pre"],d["page_post"]=map_tasks(d.task_a_timespent_pagesubmit/60,d.task_b_timespent_pagesubmit/60,d.a_first)
    for c in ("time_pre","time_post","page_pre","page_post"):
        d.loc[d[c]<0,c]=np.nan
    wide=pd.read_csv(raw/"grading_wide_complete.csv",low_memory=False,encoding="latin-1")
    grading_code=(raw/"grade_cleaning_jul21.do").read_text()
    test_graders=set(re.findall(r'drop if grader_id=="([a-f0-9]{64})"',grading_code))
    wide=wide[~wide.grader_id.isin(test_graders)].copy()
    for c in ("retry_a","retry_b","overall_a","overall_b"):
        wide[c]=pd.to_numeric(wide[c],errors="coerce")
    wide=wide[(wide.retry_a!=1)&(wide.retry_b!=1)]
    graded_day=dates(wide.StartDate_a).fillna(dates(wide.StartDate_b))
    earlier_task=wide.grader_id.map(task_dates)
    wide=wide[~(graded_day>earlier_task)].copy()
    wide=wide[wide.overall_a.between(1,7)&wide.overall_b.between(1,7)]
    grades=wide.groupby("prolific_pid").agg(grade_a=("overall_a","mean"),grade_b=("overall_b","mean"),raters=("grader_id","nunique"))
    d=d.join(grades,on="prolific_pid")
    d["grade_pre"],d["grade_post"]=map_tasks(d.grade_a,d.grade_b,d.a_first)
    d["assignment"]=d.treatment.astype(int)
    d["primary_arm"]=d.incentive_arm.isin(["linear","convex"])
    d["used_ai"]=d.usedgpt.map({1:1,2:0,4:0})
    follow=pd.read_csv(raw/"followupsurvey.csv",low_memory=False,encoding="latin-1")
    follow["finished"]=pd.to_numeric(follow.finished,errors="coerce")
    follow["usedgpt_job"]=pd.to_numeric(follow.usedgpt_job,errors="coerce")
    follow=follow[follow.finished==1].sort_values("startdate").drop_duplicates("prolific_pid")
    d=d.join(follow.set_index("prolific_pid").usedgpt_job.map({1:1,2:0}).rename("followup_used_ai"),on="prolific_pid")
    d["time_change"]=d.time_post-d.time_pre
    d["grade_change"]=d.grade_post-d.grade_pre
    audit={"sample_flow":flow,"attrition_after_baseline":attrition,"retained_participants":len(d),
           "primary_arm_participants":int(d.primary_arm.sum()),"valid_quality_pairs":int(d.grade_pre.notna().sum()),
           "valid_time_pairs":int((d.time_pre.notna()&d.time_post.notna()).sum()),
           "paired_rater_rows":len(wide),"documented_excluded_ids_count":len(excluded),
           "grading_choice":"All eligible paired graders; participant-level mean; no data-dependent grader-correlation exclusion.",
           "primary_sample":"Linear and convex incentive arms; retained available cases, not all randomized participants."}
    return (d,audit,wide) if return_grades else (d,audit)

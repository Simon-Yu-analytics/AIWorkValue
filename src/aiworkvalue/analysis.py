"""Simple assignment-based regressions; study context and attrition remain explicit."""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

DESIGN = "C(occupation) * C(a_first) + C(incentive_arm)"


def fit_record(data, formula, name, outcome, term="assignment", covariance="HC3", groups=None):
    model=smf.ols(formula,data=data,missing="drop")
    if np.linalg.matrix_rank(model.exog) < model.exog.shape[1]:
        raise ValueError("Redundant model columns; simplify nuisance controls before inference: "+name)
    if groups is None:
        fitted=model.fit(cov_type=covariance,use_t=True)
    else:
        aligned_groups=pd.Series(groups,index=data.index).loc[model.data.row_labels]
        fitted=model.fit(cov_type="cluster",cov_kwds={"groups":aligned_groups,"use_correction":True,"df_correction":True},use_t=True)
    lo,hi=fitted.conf_int().loc[term]
    return {"name":name,"outcome":outcome,"formula":formula,"term":term,"n":int(fitted.nobs),
            "coefficient":float(fitted.params[term]),"standard_error":float(fitted.bse[term]),
            "ci95":[float(lo),float(hi)],"p_value":float(fitted.pvalues[term]),
            "covariance":covariance if groups is None else "participant-clustered",
            "r_squared":float(fitted.rsquared)}


def run_analysis(d,grade_pairs):
    primary=d[d.primary_arm].copy()
    primary["log_time_pre"]=np.log1p(primary.time_pre)
    primary["log_time_post"]=np.log1p(primary.time_post)
    main=[fit_record(primary,f"time_post ~ assignment + time_pre + {DESIGN}","primary_time","minutes"),
          fit_record(primary,f"grade_post ~ assignment + grade_pre + {DESIGN}","primary_quality","grade_points")]
    adjusted=multipletests([r["p_value"] for r in main],method="holm")[1]
    for r,p in zip(main,adjusted):r["holm_p_value"]=float(p)
    specs=[("unadjusted_time","minutes","time_post ~ assignment",primary),
           ("time_change_design_controls","minutes",f"time_change ~ assignment + {DESIGN}",primary),
           ("log_time_ancova","log1p_minutes",f"log_time_post ~ assignment + log_time_pre + {DESIGN}",primary),
           ("objective_page_duration","minutes",f"page_post ~ assignment + page_pre + {DESIGN}",primary),
           ("unadjusted_quality","grade_points","grade_post ~ assignment",primary),
           ("quality_change_design_controls","grade_points",f"grade_change ~ assignment + {DESIGN}",primary),
           ("quality_including_fixed_time_arm","grade_points",f"grade_post ~ assignment + grade_pre + {DESIGN}",d)]
    robustness=[fit_record(data,formula,name,outcome) for name,outcome,formula,data in specs]
    pairs=grade_pairs.merge(primary[["prolific_pid","assignment","a_first","occupation","incentive_arm"]],on="prolific_pid",suffixes=("_grader",""))
    pairs["grade_delta"]=np.where(pairs.a_first==1,pairs.overall_b-pairs.overall_a,pairs.overall_a-pairs.overall_b)
    robustness.append(fit_record(pairs,"grade_delta ~ assignment + C(grader_id) + C(occupation):a_first + C(incentive_arm)",
                                 "paired_grader_fixed_effects","grade_points",groups=pairs.prolific_pid))
    hetero=primary.dropna(subset=["grade_pre"]).copy()
    center=float(hetero.grade_pre.mean());median=float(hetero.grade_pre.median())
    hetero["baseline_score_centered"]=hetero.grade_pre-center
    interactions=[fit_record(hetero,f"time_post ~ assignment * baseline_score_centered + time_pre + {DESIGN}",
                             "time_baseline_writing_score_interaction","minutes_per_baseline_point","assignment:baseline_score_centered"),
                  fit_record(hetero,f"grade_post ~ assignment * baseline_score_centered + {DESIGN}",
                             "quality_baseline_writing_score_interaction","grade_points_per_baseline_point","assignment:baseline_score_centered")]
    for row,p in zip(interactions,multipletests([row["p_value"] for row in interactions],method="holm")[1]):
        row["exploratory_holm_p_value"]=float(p)
    conditional=[]
    for outcome,formula in [("minutes",f"time_post ~ assignment * baseline_score_centered + time_pre + {DESIGN}"),
                            ("grade_points",f"grade_post ~ assignment * baseline_score_centered + {DESIGN}")]:
        fitted=smf.ols(formula,data=hetero).fit(cov_type="HC3",use_t=True)
        for quantile in (.25,.5,.75):
            score=float(hetero.grade_pre.quantile(quantile))
            contrast=np.zeros(len(fitted.params))
            contrast[fitted.params.index.get_loc("assignment")]=1
            contrast[fitted.params.index.get_loc("assignment:baseline_score_centered")]=score-center
            test=fitted.t_test(contrast)
            interval=np.asarray(test.conf_int()).ravel()
            conditional.append({"outcome":outcome,"baseline_quantile":quantile,"baseline_grade":score,
                                "effect":float(np.asarray(test.effect).item()),"ci95":[float(v) for v in interval],
                                "n":int(fitted.nobs),"status":"Exploratory pointwise contrast, not simultaneous subgroup inference."})
    groups=[]
    for label,mask in (("lower_baseline_score",hetero.grade_pre<=median),("higher_baseline_score",hetero.grade_pre>median)):
        sample=hetero[mask]
        for outcome,baseline,unit in (("time_post","time_pre","minutes"),("grade_post","grade_pre","grade_points")):
            groups.append({"group":label,"baseline_cutoff":median,
                           **fit_record(sample,f"{outcome} ~ assignment + {baseline} + {DESIGN}",label+"_"+outcome,unit)})
    means=[]
    for arm,sample in primary.groupby("assignment"):
        means.append({"assignment":int(arm),"n":len(sample),
                      **{k:float(sample[k].mean()) for k in ["time_pre","time_post","grade_pre","grade_post","used_ai"]},
                      "followup_respondents":int(sample.followup_used_ai.notna().sum()),
                      "followup_response_rate":float(sample.followup_used_ai.notna().mean()),
                      "followup_use_among_respondents":float(sample.followup_used_ai.mean())})
    follow=fit_record(primary,"followup_used_ai ~ assignment","two_week_use_available_respondents","probability_points")
    balance=[]
    for variable in ("time_pre","grade_pre","a_first"):
        c=primary.loc[primary.assignment==0,variable].dropna();t=primary.loc[primary.assignment==1,variable].dropna()
        sd=np.sqrt((c.var(ddof=1)+t.var(ddof=1))/2)
        balance.append({"variable":variable,"control_mean":float(c.mean()),"offer_mean":float(t.mean()),"standardized_difference":float((t.mean()-c.mean())/sd)})
    return {"primary":main,"robustness":robustness,"heterogeneity":{"baseline_mean":center,"baseline_median":median,
            "interaction_tests":interactions,"conditional_effects":conditional,"groups":groups,"status":"exploratory; not an employee allocation rule"},
            "descriptive_means":means,"baseline_balance":balance,"followup_assignment_contrast":follow,
            "inference":"Assignment contrasts among retained available cases; differential attrition limits full-sample ITT interpretation."}

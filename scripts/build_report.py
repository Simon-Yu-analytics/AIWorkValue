"""Build publication-style figures and a ten-page business research report."""
from pathlib import Path
import os,json
from xml.sax.saxutils import escape
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR",str(ROOT/".cache/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Image,PageBreak

INK="#173449";TEAL="#237F78";ORANGE="#C37B43";GRAY="#667B87"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":10,"axes.spines.top":False,
                     "axes.spines.right":False,"text.color":INK,"axes.labelcolor":INK,
                     "axes.titleweight":"bold","figure.facecolor":"white"})
FIG=ROOT/"figures";FIG.mkdir(exist_ok=True)


def save(fig,name):
    fig.savefig(FIG/name,dpi=180,bbox_inches="tight",facecolor="white");plt.close(fig)


def interval_plot(ax,rows,labels,title,unit):
    for i,row in enumerate(rows):
        b=row["coefficient"];lo,hi=row["ci95"]
        ax.errorbar(b,i,xerr=[[b-lo],[hi-b]],fmt="o",color=TEAL,capsize=4,markersize=6)
    ax.axvline(0,color=GRAY,linestyle="--",linewidth=.8)
    ax.set_yticks(range(len(rows)),labels);ax.invert_yaxis()
    ax.set_xlabel(unit);ax.set_title(title,loc="left",pad=15)


def figures(r):
    flow=r["audit"]["sample_flow"]
    fig,ax=plt.subplots(figsize=(8.8,3.5))
    labels=["Raw survey records","Completed / consent","Unique submission","Documented flags","Quality checks","Prior-grader check"]
    ax.barh(labels,[s["n"] for s in flow],color=["#A6BBC4"]*5+[TEAL]);ax.invert_yaxis()
    for i,s in enumerate(flow):ax.text(s["n"]+8,i,str(s["n"]),va="center")
    ax.set_xlim(0,870);ax.set_xlabel("Records retained; raw records are not the randomized analysis sample")
    ax.set_title("Reconstruct the sample before estimating effects",loc="left",pad=15)
    fig.tight_layout();save(fig,"01_sample_flow.png")

    fig,axes=plt.subplots(1,2,figsize=(9,3.1))
    for ax,row,title,unit in zip(axes,r["primary"],["Time effect","Quality effect"],["Minutes (negative means faster)","Points on 1-7 rating scale"]):
        interval_plot(ax,[row],["AI offer"],title,unit);ax.set_ylim(.6,-.6)
        ax.text(.03,.03,f"N = {row['n']} · HC3 95% interval",transform=ax.transAxes,fontsize=9,color=GRAY)
    fig.tight_layout(w_pad=3);save(fig,"02_primary_effects.png")

    means=r["descriptive_means"];fig,axes=plt.subplots(1,2,figsize=(9,3.6))
    for ax,outcome,title in zip(axes,["time","grade"],["Unadjusted time means","Unadjusted quality means"]):
        for row,color,label in zip(means,[INK,TEAL],["Control","AI offer"]):
            ax.plot([0,1],[row[outcome+"_pre"],row[outcome+"_post"]],marker="o",color=color,label=label,linewidth=2)
        ax.set_xticks([0,1],["Before offer","After offer"]);ax.set_title(title,loc="left")
        ax.set_ylabel("Minutes" if outcome=="time" else "Grade points");ax.legend(frameon=False)
    fig.tight_layout();save(fig,"03_before_after_means.png")

    rows=r["robustness"];fig,axes=plt.subplots(1,2,figsize=(10,4))
    t=[x for x in rows if x["name"] in ["unadjusted_time","time_change_design_controls","objective_page_duration"]]
    q=[x for x in rows if x["name"] in ["unadjusted_quality","quality_change_design_controls","quality_including_fixed_time_arm","paired_grader_fixed_effects"]]
    interval_plot(axes[0],t,["Unadjusted post","Change + controls","Objective duration"],"Time sensitivity","Minutes")
    interval_plot(axes[1],q,["Unadjusted post","Change + controls","Include fixed-time","Paired grader FE"],"Quality sensitivity","Grade points")
    fig.tight_layout(w_pad=2);save(fig,"04_robustness.png")

    fig,axes=plt.subplots(1,2,figsize=(9,3.4))
    for ax,outcome,title,unit in zip(axes,["minutes","grade_points"],["Time by baseline score","Quality by baseline score"],["Minutes","Grade points"]):
        rows=[x for x in r["heterogeneity"]["groups"] if x["outcome"]==outcome]
        interval_plot(ax,rows,["Lower baseline","Higher baseline"],title,unit)
    fig.tight_layout(w_pad=2);save(fig,"05_heterogeneity.png")

    fig,ax=plt.subplots(figsize=(8.7,3.4));x=np.arange(2);width=.34
    ax.bar(x-width/2,[v["used_ai"]*100 for v in means],width,color=INK,label="Used AI in experiment")
    ax.bar(x+width/2,[v["followup_use_among_respondents"]*100 for v in means],width,color=TEAL,label="Workplace use at two-week follow-up")
    ax.set_xticks(x,["Control assigned","AI offer assigned"]);ax.set_ylim(0,100);ax.set_ylabel("Percent of available respondents")
    ax.set_title("Access and onboarding changed use, with incomplete follow-up",loc="left",pad=16)
    ax.legend(frameon=False,loc="upper center",bbox_to_anchor=(.5,-.12),ncol=1)
    fig.tight_layout();save(fig,"06_adoption.png")

    business=r["business"];grid=business["sensitivity"]
    fs=sorted({x["transferability"] for x in grid});rs=sorted({x["review_minutes"] for x in grid})
    matrix=np.array([[next(x["net_capacity_value_month"] for x in grid if x["transferability"]==f and x["review_minutes"]==v) for v in rs] for f in fs])
    fig,ax=plt.subplots(figsize=(8.6,4.2));im=ax.imshow(matrix,cmap="RdYlGn",vmin=-6500,vmax=8500,aspect="auto",origin="lower")
    ax.set_xticks(range(len(rs)),[f"{v:g}" for v in rs]);ax.set_yticks(range(len(fs)),[f"{f:.0%}" for f in fs])
    for i in range(len(fs)):
        for j in range(len(rs)):ax.text(j,i,f"{matrix[i,j]/1000:+.1f}k",ha="center",va="center",fontsize=9)
    ax.set_xlabel("Additional verification minutes per task (assumed)");ax.set_ylabel("Share of historical time effect transferable (assumed)")
    ax.set_title("Company value depends on transferability and verification cost",loc="left",pad=18)
    fig.colorbar(im,ax=ax,label="USD monthly net capacity value; hypothetical")
    fig.tight_layout();save(fig,"07_business_sensitivity.png")

    fig,ax=plt.subplots(figsize=(8.6,3.1));names=["conservative","base","upside"];vals=[business[n]["net_capacity_value_month"] for n in names]
    ax.barh(names,vals,color=[ORANGE,TEAL,INK]);ax.axvline(0,color=GRAY,linewidth=.8);ax.invert_yaxis()
    for i,v in enumerate(vals):ax.text(v+(100 if v>=0 else -100),i,f"${v:+,.0f}",va="center",ha="left" if v>=0 else "right")
    ax.set_xlim(-5000,6500);ax.set_xlabel("USD/month; scenario assumptions, not observed company outcomes")
    ax.set_title("A positive experiment does not guarantee a profitable rollout",loc="left",pad=15)
    fig.tight_layout();save(fig,"08_commercial_scenarios.png")


def pdf(r):
    styles=getSampleStyleSheet()
    for name,font,size,leading,color,after in [("KickerA","Helvetica-Bold",9,13,TEAL,14),("TitleA","Helvetica-Bold",27,32,INK,20),
          ("BodyA","Helvetica",10,15,INK,10),("SmallA","Helvetica",8.3,11.5,GRAY,8),("SubA","Helvetica-Bold",13,18,INK,10)]:
        styles.add(ParagraphStyle(name=name,fontName=font,fontSize=size,leading=leading,textColor=colors.HexColor(color),spaceAfter=after))
    story=[]
    def p(text,style="BodyA"):story.append(Paragraph(text,styles[style]))
    def page(n,title,kicker):
        if story:story.append(PageBreak())
        p(f"AIWORKVALUE / {n:02d} / {kicker.upper()}","KickerA");p(title,"TitleA")
    def chart(name,height=230):
        story.append(Image(str(FIG/name),width=480,height=height,kind="proportional"));story.append(Spacer(1,12))
    def table(rows,widths):
        t=Table([[Paragraph(escape(str(c)),styles["SmallA"]) for c in row] for row in rows],colWidths=widths,hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E9F2EF")),("VALIGN",(0,0),(-1,-1),"TOP"),
              ("LINEBELOW",(0,0),(-1,0),1,colors.HexColor(TEAL)),("LINEBELOW",(0,1),(-1,-1),.4,colors.HexColor("#DFE6E8")),
              ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),7)]))
        story.extend([t,Spacer(1,12)])
    time,quality=r["primary"];b=r["business"]["base"];unc=r["business"]["effect_uncertainty_only"]
    saved=-time["coefficient"];save_ci=[-time["ci95"][1],-time["ci95"][0]]
    page(1,"When does generative AI create business value?","Executive research brief")
    p("Independent reanalysis of a randomized professional-writing experiment, with a separate commercial adoption model.")
    p("<b>Recommendation:</b> investigate a bounded writing-workflow pilot. The historical experiment shows faster completion and better rated writing in retained respondents. A new company's investment case remains sensitive to verification effort, task mix and cost.")
    table([["Evidence", "This project's estimate", "Decision implication"],
      ["Time, available cases",f"{saved:.2f} minutes saved; 95% interval {save_ci[0]:.2f} to {save_ci[1]:.2f}; N={time['n']}.","Test recurring, self-contained writing tasks first."],
      ["Rated quality",f"+{quality['coefficient']:.2f} points on a 1-7 scale; interval {quality['ci95'][0]:.2f} to {quality['ci95'][1]:.2f}; N={quality['n']}.","Writing scores do not establish factual accuracy."],
      ["Commercial base scenario",f"${b['net_capacity_value_month']:,.0f}/month net capacity value under assumptions.","Do not present this as measured company savings."]],[110,210,160])
    p("What this project contributes","SubA")
    p("A reconstructed sample audit, independent Python estimators, counterbalancing checks, sensitivity analyses, exploratory baseline-score differences, SQL summaries and a transparent translation from experimental evidence to a company budget boundary.")
    p("Source experiment: Shakked Noy and Whitney Zhang, Science (2023). Analysis prepared 19 October 2026. This project did not recruit participants or conduct the original experiment.","SmallA")

    page(2,"Understand the experiment and the retained sample","Study design")
    chart("01_sample_flow.png",220)
    p("Participants completed two occupation-specific writing tasks. Between tasks, the treatment group was offered ChatGPT access and onboarding; the control group completed a signup comparison. Task order was randomized. The experiment used the technology available in early 2023, not current AI models.")
    p(f"The cleaning pipeline reconstructs {r['audit']['retained_participants']} retained participants. Primary productivity analyses use {r['audit']['primary_arm_participants']} participants in the linear/convex incentive arms; the fixed-time arm is excluded from the time analysis because time was constrained by design.")
    table([["Primary outcome", "Available baseline/post pairs", "Why the denominator differs"],
           ["Self-reported time",time["n"],"Some respondents lack one or more workflow-time components."],
           ["Mean paired rating",quality["n"],"Some retained submissions lack eligible paired ratings."]],[145,120,215])
    p("Raw records include incomplete or excluded entries and must not be called the randomized analysis sample. Every filtering stage is saved in reports/data-audit.json.","SmallA")

    page(3,"Estimate assignment effects without selecting AI users","Identification and methods")
    p("The estimand is the effect of assignment to the AI offer among retained available cases. Selecting only people who chose to use AI would condition on a post-randomization behavior and break the comparison.")
    table([["Choice", "Implementation", "Reason"],
      ["Counterbalancing", "Map task A/B to baseline/post using the randomized task order.", "Task A is not always the pre-treatment task."],
      ["Time outcome", "Sum reported brainstorming, drafting, editing and other minutes.", "Preserve the documented workflow components."],
      ["Quality outcome", "Average valid paired grader ratings per participant.", "Each participant contributes one baseline/post pair."],
      ["Primary adjustment", "Post outcome on assignment, baseline, occupation x task order, and incentive arm.", "Improve precision while respecting the study design."],
      ["Uncertainty", "HC3 robust standard errors, t intervals; Holm adjustment for two primary tests.", "Report uncertainty and limit two-outcome multiplicity."]],[105,225,150])
    p("The study's grading model included grader-level details. This project's participant-average estimator is deliberately simpler; a paired-grader fixed-effect sensitivity model is also estimated. No exact reproduction of every published coefficient is claimed.")
    p("The full analysis plan was written before this project's models were fitted, after the original public findings were already known. It is not a new preregistration. Differential attrition limits a full-sample intention-to-treat interpretation.","SmallA")

    page(4,"The historical effects are sizable in both outcomes","Main findings")
    chart("02_primary_effects.png",210)
    chart("03_before_after_means.png",210)
    p(f"Adjusted assignment contrast: {time['coefficient']:.2f} minutes and +{quality['coefficient']:.2f} quality points. Both co-primary tests remain below 0.001 after Holm adjustment. The lower chart shows descriptive available-case means, not adjusted estimates.")
    p("A grade is a rubric-based assessment of writing output, not an audited measure of factual correctness, customer impact or firm performance. Saving minutes on a study task does not establish a proportional increase in total employee productivity.","SmallA")

    page(5,"Check whether the result survives reasonable alternatives","Robustness and attrition")
    chart("04_robustness.png",230)
    p("The time effect remains negative with unadjusted outcomes, change-score controls and an objective page-duration measure. The quality effect remains positive with changes, inclusion of the fixed-time arm and a paired-grader fixed-effect model with participant-clustered inference.")
    a=r["audit"]["attrition_after_baseline"]
    table([["Assignment", "Reached first-task assessment", "Completed survey", "Completion rate"]]+
          [["Control" if x["assignment"]==0 else "AI offer",x["reached_first_task"],x["finished"],f"{x['completion_rate']:.1%}"] for x in a],[95,145,120,120])
    p("These completion rates concern consented linear/convex participants who reached the first-task assessment. They are not the final analytic-sample counts. Differential completion and later quality exclusions remain limitations; baseline adjustment cannot guarantee their elimination.","SmallA")

    page(6,"Quality gains vary with baseline writing performance","Exploratory heterogeneity")
    chart("05_heterogeneity.png",225)
    qi=r["heterogeneity"]["interaction_tests"][1];ti=r["heterogeneity"]["interaction_tests"][0]
    p(f"The quality interaction is {qi['coefficient']:.3f} points per baseline writing-score point (95% interval {qi['ci95'][0]:.3f} to {qi['ci95'][1]:.3f}). This is consistent with a larger quality improvement among lower baseline scorers in this task setting.")
    p(f"The time interaction is {ti['coefficient']:.3f} minutes per baseline score point (interval {ti['ci95'][0]:.3f} to {ti['ci95'][1]:.3f}); it remains imprecise. Similar time benefits in the two plotted groups should not be described as a proven subgroup difference.")
    p("Business interpretation","SubA")
    p("Provide onboarding broadly and investigate where writing assistance improves an existing workflow. Use task needs and source-verification requirements to scope a pilot. A single baseline writing exercise is not a general employee-ability measure and should not become a hiring or workforce-allocation score.")
    p("Group cutoffs use the pooled pre-treatment median. These extensions are exploratory, with small subgroups and no claim of an independent confirmatory subgroup experiment.","SmallA")

    page(7,"Adoption persists, but external validity remains limited","Behavior and transfer")
    chart("06_adoption.png",240)
    f=r["followup_assignment_contrast"]
    p(f"Among {f['n']} available two-week follow-up respondents in the primary arms, the assignment contrast in reported workplace use is {f['coefficient']*100:.1f} percentage points (95% interval {f['ci95'][0]*100:.1f} to {f['ci95'][1]*100:.1f}). This is a response-based, self-reported result; it is not a measured long-run productivity effect.")
    p("The source experiment used short, self-contained writing tasks across selected occupations. Real business work can require proprietary context, exact facts, collaboration and longer review cycles. The new company's time effect, quality and maintenance burden remain unknown.")
    p("Treat this as historical evidence motivating a new pilot. Do not present the 2023 effect as an estimate of current AI products or assume that workplace adoption makes the company economically better off.")

    page(8,"Translate minutes into a transparent budget boundary","Commercial extension")
    table([["Input", "Base assumption", "Status"],
      ["Employees / rollout coverage","200 / 50% (100 offered seats)","Company scenario"],
      ["Eligible writing tasks","20 per offered employee per month","Company scenario"],
      ["Transferable historical effect","50% of the study assignment estimate","External-validity assumption"],
      ["Additional verification","2 minutes per eligible task","Company scenario"],
      ["Employee time value","$35 per hour","Capacity valuation assumption"],
      ["Assumed license / fixed monthly cost","$25 per offered seat / $500","Illustrative costs, not market quotes"],
      ["One-time setup","$3,000","Company scenario"]],[140,200,140])
    p("Net minutes per task = historical assignment minutes saved x transferability - additional verification time. Capacity hours = offered employees x eligible tasks x net minutes / 60. Net capacity value = hours x hourly value - seat costs - fixed operating cost.")
    p(f"Base output: {b['capacity_hours_month']:.1f} hours/month of capacity, ${b['capacity_value_month']:,.0f} gross time value, ${b['recurring_cost_month']:,.0f} recurring cost and ${b['net_capacity_value_month']:,.0f} net capacity value. Simple capacity-value payback is {b['capacity_value_payback_months']:.1f} months under these assumptions.")
    p("The assignment effect already includes the source experiment's take-up pattern. Multiplying by that take-up rate again would double-discount the same mechanism. Offered seats incur cost even if some people do not use them.","SmallA")

    page(9,"A strong task effect can still produce a fragile investment case","Sensitivity and downside")
    chart("07_business_sensitivity.png",235)
    p(f"The assumed operating break-even seat cost is ${b['operating_break_even_seat_cost']:.2f}/month, before recovering setup cost. It is a budget ceiling under a scenario, not an observed willingness to pay or recommended market price.")
    low=unc["lower"]["net_capacity_value_month"];high=unc["upper"]["net_capacity_value_month"]
    p(f"Holding all commercial assumptions fixed and propagating only the statistical time-effect interval gives monthly net capacity value from ${low:,.0f} to ${high:,.0f}. This range crosses zero. It is not a complete confidence interval for company profit because transferability and cost assumptions have further unmeasured uncertainty.")
    threshold=saved*.5-3000*60/(100*20*35)
    p(f"At the base costs and task volume, additional verification above about {threshold:.2f} minutes per task removes the positive operating case. This is a concrete quantity for a pilot to measure.")
    p("Conservative, base and upside results are saved separately in reports/results.json. Released employee capacity becomes a cash saving only if a specific budget expense actually falls; that has not been measured.","SmallA")

    page(10,"Use the evidence to design the next decision","Recommendation and reproducibility")
    p("Scope a small trial around recurring, generic writing work where factual review can be observed. Measure time to accepted output including checking and rework, blinded quality, real eligible task volume, offered-seat usage and operating cost. Stop or redesign if review burden consumes the expected gain.")
    table([["Decision", "Evidence needed in the new company"],
      ["Expand", "Useful verified time improvement, acceptable quality and positive downside economics."],
      ["Revise", "Benefits concentrated in a narrow task category or avoidable verification friction."],
      ["Stop", "Quality problems, unsuitable documents, low eligible volume or costs above the budget ceiling."]],[85,395])
    p("Reproduction and original contribution","SubA")
    p("The repository contains a hash-verified downloader, a sample-flow audit, Python statistical models, SQL summaries, an executed analysis notebook, eight reproducible figures and this report. Raw and participant-level data are downloaded separately and are not republished. The source package has no declared license in its OSF metadata.")
    p("Source study and data","SubA")
    for text in ["Noy, S. and Zhang, W. (2023). Experimental evidence on the productivity effects of generative artificial intelligence. Science 381, 187-192. doi.org/10.1126/science.adh2586.",
                 "Author-hosted replication package: osf.io/xd7qw/; DOI 10.17605/OSF.IO/XD7QW. The source ReadMe documents anonymization and variable definitions.",
                 "This project: independent reanalysis, estimator comparisons and commercial scenarios. It does not claim original data collection, a current-model benchmark or realized business benefits."]:
        p(escape(text),"SmallA")
    def footer(c,doc):
        c.setStrokeColor(colors.HexColor("#DDE5E8"));c.line(52,40,543,40);c.setFont("Helvetica",8);c.setFillColor(colors.HexColor(GRAY))
        c.drawString(52,27,"AIWORKVALUE  |  Independent historical reanalysis + hypothetical commercial extension")
        c.drawRightString(543,27,str(doc.page))
    target=ROOT/"reports/AIWorkValue_Research_Report.pdf"
    doc=SimpleDocTemplate(str(target),pagesize=(595.28,841.89),leftMargin=55,rightMargin=55,topMargin=47,bottomMargin=55,
                          title="AIWorkValue - Generative AI, Productivity and Adoption Economics",author="AIWorkValue project")
    doc.build(story,onFirstPage=footer,onLaterPages=footer);print(target)


if __name__=="__main__":
    r=json.loads((ROOT/"reports/results.json").read_text());figures(r);pdf(r)

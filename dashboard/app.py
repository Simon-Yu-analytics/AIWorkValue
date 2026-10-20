"""Public aggregate-only BI application; no participant files or model API needed."""
from pathlib import Path
import json
import sys
from dataclasses import replace
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from aiworkvalue.business import Scenario, value_case

st.set_page_config(page_title="AIWorkValue | Evidence to Decision", page_icon="📊", layout="wide")
st.markdown("""<style>
.block-container{padding-top:4rem;max-width:1300px}
h1,h2,h3{color:#173449} [data-testid="stMetricValue"]{color:#237F78}
[data-testid="stMetric"]{background:#f0f5f6;border-radius:8px;padding:14px}
</style>""", unsafe_allow_html=True)


@st.cache_data
def load_aggregates(results_version, warehouse_version):
    return (json.loads((ROOT / "reports/results.json").read_text()),
            json.loads((ROOT / "reports/warehouse-summary.json").read_text()))


def style_chart(fig):
    fig.update_layout(template="plotly_white", font=dict(color="#173449"),
                      margin=dict(l=20, r=20, t=45, b=30), height=350,
                      legend=dict(orientation="h", y=-0.25))
    return fig


results, warehouse = load_aggregates((ROOT/"reports/results.json").stat().st_mtime_ns,
                                     (ROOT/"reports/warehouse-summary.json").stat().st_mtime_ns)
st.caption("AIWORKVALUE  /  BUSINESS ANALYTICS RESEARCH")
st.title("AI writing assistance: evidence to decision")
st.write("Explore a public writing experiment, then test what its historical time effect could mean under explicit business assumptions.")
view = st.radio("Analysis view", ["Experiment Overview", "Productivity Analysis", "Business Decision"], horizontal=True, key="analysis_view")

if view == "Experiment Overview":
    st.subheader("Understand the sample before comparing groups")
    columns = st.columns(3)
    columns[0].metric("Retained participants", results["audit"]["retained_participants"])
    columns[1].metric("Primary incentive arms", results["audit"]["primary_arm_participants"])
    columns[2].metric("Outcome fact rows", warehouse["table_rows"]["fact_outcome"])
    st.caption("Outcome fact rows are participant × period observations, not additional people. Only the linear/convex arms enter primary productivity comparisons.")
    kpi = pd.DataFrame(warehouse["kpis"])
    occupation = st.selectbox("Occupation (descriptive comparison only)", ["All occupations"] + sorted(kpi.occupation.unique()), key="occupation")
    selected = kpi if occupation == "All occupations" else kpi[kpi.occupation == occupation]
    rows = []
    for (assignment, period), group in selected.groupby(["assignment_label", "period_name"]):
        rows.append({"Assignment": assignment, "Period": period,
                     "Participants": int(group.participants.sum()),
                     "Time observations": int(group.time_observations.sum()),
                     "Mean minutes": (group.mean_minutes * group.time_observations).sum() / group.time_observations.sum() if group.time_observations.sum() else None,
                     "Quality observations": int(group.quality_observations.sum()),
                     "Mean rating": (group.mean_quality * group.quality_observations).sum() / group.quality_observations.sum() if group.quality_observations.sum() else None})
    table = pd.DataFrame(rows)
    fig = go.Figure()
    for arm, color in [("Control", "#173449"), ("AI offer", "#237F78")]:
        arm_rows = table[table.Assignment == arm].set_index("Period").reindex(["Baseline", "Post"])
        fig.add_trace(go.Bar(name=arm, x=["Baseline", "Post"], y=arm_rows["Mean minutes"], marker_color=color))
    fig.update_layout(title="Unadjusted completion time", yaxis_title="Minutes", barmode="group")
    st.plotly_chart(style_chart(fig), width="stretch")
    st.dataframe(table.round(2), hide_index=True, width="stretch")
    st.info("Occupation filters change descriptive aggregates only. The adjusted primary model estimates shown on the next page remain full-sample estimates.")
    with st.expander("Sample flow and warehouse integrity"):
        st.dataframe(pd.DataFrame(results["audit"]["sample_flow"]), hide_index=True, width="stretch")
        st.dataframe(pd.DataFrame(warehouse["integrity_checks"]), hide_index=True, width="stretch")

elif view == "Productivity Analysis":
    st.subheader("Historical effects, with uncertainty")
    time, quality = results["primary"]
    left, right = st.columns(2)
    left.metric("Adjusted time difference", f"{time['coefficient']:.2f} min")
    right.metric("Adjusted writing-rating difference", f"+{quality['coefficient']:.2f} points")
    st.caption(f"Time N={time['n']}; quality N={quality['n']}. Baseline-adjusted assignment contrasts, HC3 t intervals; two primary tests receive Holm adjustment.")
    for record, label, color in [(time, "Completion time (minutes)", "#237F78"), (quality, "Writing rating (1–7 points)", "#173449")]:
        effect, (low, high) = record["coefficient"], record["ci95"]
        fig = go.Figure(go.Scatter(x=[effect], y=["AI offer vs control"], mode="markers",
                                  marker=dict(size=13, color=color),
                                  error_x=dict(type="data", symmetric=False, array=[high-effect], arrayminus=[effect-low])))
        fig.add_vline(x=0, line_dash="dash", line_color="#8da1aa")
        fig.update_layout(title=label + " — 95% interval", height=230)
        fig = style_chart(fig); fig.update_layout(height=230)
        st.plotly_chart(fig, width="stretch")
    st.warning("Statistical evidence of faster study-task completion does not establish whole-job productivity, factual accuracy or positive commercial returns.")
    with st.expander("Robustness checks"):
        st.dataframe(pd.DataFrame([{k:r[k] for k in ["name","n","coefficient","standard_error","p_value"]} for r in results["robustness"]]), hide_index=True, width="stretch")
    st.markdown("#### Does baseline writing performance change the effect?")
    conditional = pd.DataFrame(results["heterogeneity"]["conditional_effects"])
    st.dataframe(conditional[["outcome","baseline_quantile","baseline_grade","effect","ci95","n"]], hide_index=True, width="stretch")
    st.caption("Exploratory pointwise contrasts, not simultaneous subgroup intervals. One baseline writing score is noisy and ceiling-constrained; this is not an employee allocation rule.")

else:
    st.subheader("Change the assumptions, inspect the decision")
    st.caption("All controls are hypothetical inputs. Costs and benefits are allocated to one workflow, with no company deployment or realized-profit claim.")
    with st.sidebar:
        st.header("Business assumptions")
        employees = st.number_input("Employees", 1, 10000, 200, step=10, key="employees")
        coverage = st.slider("Offered-seat coverage (%)", 0, 100, 50, key="coverage") / 100
        tasks = st.number_input("Eligible tasks/person/month", 0.0, 200.0, 20.0, step=1.0, key="tasks")
        baseline = st.number_input("Baseline task duration (minutes)", 0.5, 240.0, 10.0, step=0.5, key="baseline")
        transfer = st.slider("Historical-effect transfer (%)", 0, 100, 50, key="transfer") / 100
        review = st.number_input("Extra review minutes/task", 0.0, 60.0, 2.0, step=0.5, key="review")
        revision = st.number_input("Extra revision minutes/task", 0.0, 60.0, 0.5, step=0.5, key="revision")
        rework_probability = st.slider("Rework probability (%)", 0, 100, 20, key="rework_probability") / 100
        rework = st.number_input("Minutes when rework is needed", 0.0, 120.0, 3.0, step=0.5, key="rework")
        hourly = st.number_input("Capacity value/hour ($)", 0.0, 500.0, 35.0, step=1.0, key="hourly")
        seat = st.number_input("Seat cost/month ($)", 0.0, 500.0, 25.0, step=1.0, key="seat")
        fixed = st.number_input("Fixed operating cost/month ($)", 0.0, 50000.0, 500.0, step=50.0, key="fixed")
        setup = st.number_input("One-time setup cost ($)", 0.0, 100000.0, 3000.0, step=100.0, key="setup")
    scenario = Scenario(employees, coverage, tasks, transfer, review, hourly, seat, fixed, setup,
                        baseline, revision, rework_probability, rework)
    saved = -results["primary"][0]["coefficient"]
    case = value_case(saved, scenario)
    cols = st.columns(3)
    cols[0].metric("Net capacity value / month", f"${case['net_capacity_value_month']:,.0f}")
    cols[1].metric("Net capacity hours / month", f"{case['capacity_hours_month']:.1f}")
    cols[2].metric("Estimated AI workflow / task", f"{case['ai_workflow_minutes_per_task']:.2f} min")
    st.write(f"{case['offered_employees']:g} offered seats · ${case['recurring_cost_month']:,.0f} recurring monthly cost · {case['expected_rework_minutes']:.2f} expected extra rework minutes/task")
    if case["baseline_cap_applied"]:
        st.info("Baseline-duration cap applied: transferred savings cannot exceed the task's assumed original duration.")
    low, high = results["primary"][0]["ci95"]
    bounds = [value_case(-high, scenario)["net_capacity_value_month"], value_case(-low, scenario)["net_capacity_value_month"]]
    st.caption(f"Historical-effect interval only: USD {bounds[0]:,.0f} to {bounds[1]:,.0f}/month. Transfer, duration, cost and task-frequency uncertainty are additional.")
    c1,c2,c3 = st.columns(3)
    ceiling = case["operating_break_even_seat_cost"]
    minimum = case["operating_break_even_tasks_per_employee_month"]
    maximum = case["max_review_minutes_at_operating_break_even"]
    c1.metric("Operating seat-cost ceiling", "Undefined" if ceiling is None else f"${ceiling:.2f}/month")
    c2.metric("Tasks/person/month to break even", "Undefined" if minimum is None else f"{minimum:.1f}")
    c3.metric("Extra-review budget to break even", "Undefined" if maximum is None else f"{maximum:.2f} min")
    payback = case["capacity_value_payback_months"]
    payback_text = ("not reached at the selected monthly value" if payback is None
                    else f"{payback:.1f} months")
    st.caption(f"One-time setup: USD {setup:,.0f}. Illustrative capacity-value payback: {payback_text}. Setup is separate from recurring monthly costs; this is not cash-investment payback.")
    if case["offered_employees"] == 0:
        st.info("No seats are offered. Per-seat and task-frequency break-even values are undefined; fixed operating costs remain in the scenario.")
    elif minimum is None:
        st.info("Increasing task volume cannot cover costs when net capacity value per task is nonpositive.")
    if (ceiling is not None and ceiling < 0) or (maximum is not None and maximum < 0):
        st.caption("A negative seat-cost ceiling or review budget means even zero seat cost or zero extra review, respectively, cannot cover recurring costs with the other inputs fixed.")
    frequencies = [4,8,12,16,20,30,40]
    reviews = [0,1,2,3,4,5]
    z = [[value_case(saved, replace(scenario, eligible_tasks_per_employee_month=f, additional_review_minutes=r))["net_capacity_value_month"] for f in frequencies] for r in reviews]
    fig = go.Figure(go.Heatmap(x=frequencies, y=reviews, z=z, colorscale="RdYlGn", zmid=0, colorbar_title="USD/month"))
    fig.update_layout(title="Sensitivity: task frequency × extra review", xaxis_title="Tasks/person/month", yaxis_title="Extra review min/task")
    st.plotly_chart(style_chart(fig), width="stretch")
    st.write("**Decision readout:** " + ("The selected point scenario covers recurring costs; verify the inputs and downside before considering purchase." if case["net_capacity_value_month"] >= 0 else "The selected scenario does not cover recurring costs. Investigate task fit, actual checking effort and shared uses before drawing a purchase conclusion."))
    st.caption("Released capacity is not cash savings. Quality is not monetized. Baseline duration and all review/revision/rework inputs require measurement; the historical experiment did not estimate this new workflow.")
    st.download_button("Download scenario assumptions and calculation", json.dumps(case, indent=2), "aiworkvalue_scenario.json", "application/json")

st.divider()
st.caption("Source experiment: Noy & Zhang, Science (2023), OSF xd7qw. This project is independent reanalysis plus hypothetical business modeling, not an original randomized experiment.")

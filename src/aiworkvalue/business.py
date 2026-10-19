"""Commercial extension of an experimental assignment effect, with explicit assumptions."""
from dataclasses import dataclass,asdict,replace
import math


@dataclass(frozen=True)
class Scenario:
    employees: int=200
    rollout_coverage: float=.5
    eligible_tasks_per_employee_month: float=20
    transferability: float=.5
    additional_review_minutes: float=2
    loaded_hourly_value: float=35
    assumed_seat_cost_month: float=25
    fixed_operating_cost_month: float=500
    setup_cost: float=3000


def value_case(time_saved_minutes,assumptions=Scenario()):
    if not math.isfinite(time_saved_minutes):raise ValueError("Time effect must be finite.")
    for key,value in asdict(assumptions).items():
        if not math.isfinite(value) or value<0:raise ValueError(f"Invalid {key}")
    if assumptions.rollout_coverage>1 or assumptions.transferability>1:
        raise ValueError("Coverage and transferability are fractions.")
    offered=assumptions.employees*assumptions.rollout_coverage
    net_minutes=time_saved_minutes*assumptions.transferability-assumptions.additional_review_minutes
    hours=offered*assumptions.eligible_tasks_per_employee_month*net_minutes/60
    value=hours*assumptions.loaded_hourly_value
    recurring=offered*assumptions.assumed_seat_cost_month+assumptions.fixed_operating_cost_month
    net=value-recurring
    ceiling=(value-assumptions.fixed_operating_cost_month)/offered if offered>0 else None
    return {"assumptions":asdict(assumptions),"study_assignment_minutes_saved":time_saved_minutes,
            "offered_employees":offered,"net_minutes_per_eligible_task":net_minutes,
            "capacity_hours_month":hours,"capacity_value_month":value,"recurring_cost_month":recurring,
            "net_capacity_value_month":net,"operating_break_even_seat_cost":ceiling,
            "capacity_value_payback_months":assumptions.setup_cost/net if net>0 else None,
            "boundary":"Illustrative capacity value, not cash savings. Historical assignment effect already includes study take-up; do not multiply by that take-up rate again."}


def business_results(primary_time):
    saved=-primary_time["coefficient"]
    low,high=-primary_time["ci95"][1],-primary_time["ci95"][0]
    cases={"conservative":Scenario(transferability=.25,additional_review_minutes=3),"base":Scenario(),
           "upside":Scenario(transferability=.75,additional_review_minutes=1)}
    result={name:value_case(saved,a) for name,a in cases.items()}
    result["effect_uncertainty_only"]={"minutes_saved_ci95":[low,high],"lower":value_case(low),"upper":value_case(high),
                                      "boundary":"This range propagates statistical effect uncertainty only; assumptions and external validity have additional unmeasured uncertainty."}
    result["sensitivity"]=[{"transferability":f,"review_minutes":r,
                            "net_capacity_value_month":value_case(saved,replace(Scenario(),transferability=f,additional_review_minutes=r))["net_capacity_value_month"]}
                           for f in (.25,.4,.5,.6,.75,1.) for r in (0.,1.,2.,3.,4.,5.)]
    return result

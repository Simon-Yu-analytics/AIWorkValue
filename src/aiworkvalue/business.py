"""A worked business example with explicit, hypothetical assumptions."""
from dataclasses import asdict, dataclass, replace
import math


@dataclass(frozen=True)
class Scenario:
    employees: int = 200
    rollout_coverage: float = 0.5
    eligible_tasks_per_employee_month: float = 20
    transferability: float = 0.5
    additional_review_minutes: float = 2
    loaded_hourly_value: float = 35
    assumed_seat_cost_month: float = 25
    fixed_operating_cost_month: float = 500
    setup_cost: float = 3000


def value_case(time_saved_minutes, assumptions=Scenario()):
    """Convert a historical assignment effect into conditional capacity value.

    The effect already includes source-study take-up. Transferability represents
    a separate assumption about a new setting. Review minutes are incremental
    checking effort, not all editing time already captured in the study.
    """
    if not math.isfinite(time_saved_minutes):
        raise ValueError("Time effect must be finite.")
    for key, value in asdict(assumptions).items():
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"Invalid {key}")
    if assumptions.rollout_coverage > 1 or assumptions.transferability > 1:
        raise ValueError("Coverage and transferability are fractions.")

    offered = assumptions.employees * assumptions.rollout_coverage
    net_minutes = (time_saved_minutes * assumptions.transferability
                   - assumptions.additional_review_minutes)
    hours = offered * assumptions.eligible_tasks_per_employee_month * net_minutes / 60
    value = hours * assumptions.loaded_hourly_value
    recurring = (offered * assumptions.assumed_seat_cost_month
                 + assumptions.fixed_operating_cost_month)
    net = value - recurring

    # A zero-seat scenario cannot define a per-seat budget. Nonpositive value
    # has no simple setup-cost payback; keep it undefined rather than forcing 0.
    ceiling = ((value - assumptions.fixed_operating_cost_month) / offered
               if offered > 0 else None)
    payback = assumptions.setup_cost / net if net > 0 else None
    return {
        "assumptions": asdict(assumptions),
        "study_assignment_minutes_saved": time_saved_minutes,
        "offered_employees": offered,
        "net_minutes_per_eligible_task": net_minutes,
        "capacity_hours_month": hours,
        "capacity_value_month": value,
        "recurring_cost_month": recurring,
        "net_capacity_value_month": net,
        "operating_break_even_seat_cost": ceiling,
        "capacity_value_payback_months": payback,
        "boundary": ("Illustrative capacity value, not cash savings. Historical assignment effect already includes study take-up; do not multiply by that take-up rate again."),
    }


def business_results(primary_time):
    saved = -primary_time["coefficient"]
    low, high = -primary_time["ci95"][1], -primary_time["ci95"][0]
    cases = {
        "conservative": Scenario(transferability=0.25, additional_review_minutes=3),
        "base": Scenario(),
        "upside": Scenario(transferability=0.75, additional_review_minutes=1),
    }
    result = {name: value_case(saved, scenario) for name, scenario in cases.items()}
    result["effect_uncertainty_only"] = {
        "minutes_saved_ci95": [low, high],
        "lower": value_case(low),
        "upper": value_case(high),
        "boundary": "This range propagates statistical effect uncertainty only; assumptions and external validity have additional unmeasured uncertainty.",
    }
    result["sensitivity"] = [
        {
            "transferability": share,
            "review_minutes": review,
            "net_capacity_value_month": value_case(
                saved, replace(Scenario(), transferability=share,
                               additional_review_minutes=review)
            )["net_capacity_value_month"],
        }
        for share in (0.25, 0.4, 0.5, 0.6, 0.75, 1.0)
        for review in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0)
    ]
    return result

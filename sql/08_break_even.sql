-- Boundary values cover operating costs only; setup cost is handled by payback.
-- A negative verification threshold means zero extra review is still unaffordable.
SELECT scenario, operating_seat_cost_ceiling,
       CASE WHEN offered_seats > 0 AND eligible_tasks_per_employee_month > 0 AND loaded_hourly_value > 0
            THEN MIN(minutes_saved * transferability, baseline_task_minutes) - revision_minutes - rework_probability*rework_minutes
                 - recurring_cost * 60.0 / (offered_seats * eligible_tasks_per_employee_month * loaded_hourly_value)
       END AS max_additional_review_minutes_at_operating_break_even,
       CASE WHEN offered_seats > 0 AND net_minutes > 0 AND loaded_hourly_value > 0
            THEN recurring_cost * 60.0 / (offered_seats * net_minutes * loaded_hourly_value)
       END AS min_tasks_per_offered_employee_month_at_operating_break_even,
       CASE WHEN offered_seats > 0 AND net_minutes > 0 AND loaded_hourly_value > 0
            THEN 'positive per-task value' ELSE 'no positive per-task value at these assumptions'
       END AS boundary_status
FROM v_business_value WHERE scenario_kind = 'named' ORDER BY scenario;

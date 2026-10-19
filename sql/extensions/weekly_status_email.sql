-- Frequency and checking time change; other cost assumptions remain fixed.
-- All values are conditional capacity values, not observed cash savings.
WITH parameters AS (
    SELECT :minutes_saved AS minutes_saved, :saved_low AS saved_low, :saved_high AS saved_high,
           :employees * :rollout_coverage AS offered_seats,
           :transferability AS transferability, :loaded_hourly_value AS hourly_value,
           :assumed_seat_cost_month AS seat_cost, :fixed_operating_cost_month AS fixed_cost
), task_margins AS (
    SELECT i.*, p.*,
           minutes_saved * transferability - review_minutes AS net_minutes_per_task,
           saved_low * transferability - review_minutes AS net_minutes_low,
           saved_high * transferability - review_minutes AS net_minutes_high,
           offered_seats * seat_cost + fixed_cost AS recurring_cost
    FROM extension_inputs AS i CROSS JOIN parameters AS p
), capacity AS (
    SELECT *, offered_seats * tasks_per_employee_month * net_minutes_per_task / 60.0 AS capacity_hours
    FROM task_margins
)
SELECT frequency, tasks_per_employee_month, review_minutes, offered_seats,
       net_minutes_per_task, capacity_hours, recurring_cost,
       capacity_hours * hourly_value - recurring_cost AS net_capacity_value,
       offered_seats * tasks_per_employee_month * net_minutes_low / 60.0 * hourly_value - recurring_cost AS effect_only_low,
       offered_seats * tasks_per_employee_month * net_minutes_high / 60.0 * hourly_value - recurring_cost AS effect_only_high,
       CASE WHEN offered_seats > 0 AND net_minutes_per_task > 0 AND hourly_value > 0
            THEN recurring_cost * 60.0 / (offered_seats * net_minutes_per_task * hourly_value)
       END AS operating_break_even_tasks_per_employee_month
FROM capacity ORDER BY tasks_per_employee_month, review_minutes;

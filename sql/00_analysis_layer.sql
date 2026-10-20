-- SQLite analysis layer. Participant records stay local.
CREATE TABLE IF NOT EXISTS analysis_sample_flow (
    stage_order INTEGER PRIMARY KEY,
    stage TEXT NOT NULL UNIQUE,
    n INTEGER NOT NULL CHECK (n >= 0)
);
CREATE TABLE IF NOT EXISTS time_effect (
    effect_id INTEGER PRIMARY KEY CHECK (effect_id = 1),
    minutes_saved REAL NOT NULL,
    minutes_saved_low REAL NOT NULL,
    minutes_saved_high REAL NOT NULL
);
DROP VIEW IF EXISTS v_business_value;
DROP TABLE IF EXISTS business_assumptions;
CREATE TABLE business_assumptions (
    scenario TEXT PRIMARY KEY,
    scenario_kind TEXT NOT NULL CHECK (scenario_kind IN ('named', 'grid')),
    employees REAL NOT NULL CHECK (employees >= 0),
    rollout_coverage REAL NOT NULL CHECK (rollout_coverage BETWEEN 0 AND 1),
    eligible_tasks_per_employee_month REAL NOT NULL CHECK (eligible_tasks_per_employee_month >= 0),
    transferability REAL NOT NULL CHECK (transferability BETWEEN 0 AND 1),
    additional_review_minutes REAL NOT NULL CHECK (additional_review_minutes >= 0),
    loaded_hourly_value REAL NOT NULL CHECK (loaded_hourly_value >= 0),
    assumed_seat_cost_month REAL NOT NULL CHECK (assumed_seat_cost_month >= 0),
    fixed_operating_cost_month REAL NOT NULL CHECK (fixed_operating_cost_month >= 0),
    setup_cost REAL NOT NULL CHECK (setup_cost >= 0),
    baseline_task_minutes REAL NOT NULL CHECK (baseline_task_minutes > 0),
    revision_minutes REAL NOT NULL CHECK (revision_minutes >= 0),
    rework_probability REAL NOT NULL CHECK (rework_probability BETWEEN 0 AND 1),
    rework_minutes REAL NOT NULL CHECK (rework_minutes >= 0)
);

DROP VIEW IF EXISTS v_outcome_pairs;
CREATE VIEW v_outcome_pairs AS
SELECT assignment, occupation, incentive_arm, a_first,
       'time_minutes' AS outcome, time_pre AS baseline, time_post AS post
FROM participants
WHERE primary_arm = 1 AND time_pre IS NOT NULL AND time_post IS NOT NULL
UNION ALL
SELECT assignment, occupation, incentive_arm, a_first,
       'quality_points', grade_pre, grade_post
FROM participants
WHERE primary_arm = 1 AND grade_pre IS NOT NULL AND grade_post IS NOT NULL;

-- Each stage carries full precision. Round only in presentation queries.
DROP VIEW IF EXISTS v_business_value;
CREATE VIEW v_business_value AS
WITH task_value AS (
    SELECT a.*, e.minutes_saved, e.minutes_saved_low, e.minutes_saved_high,
           employees * rollout_coverage AS offered_seats,
           MIN(e.minutes_saved * transferability, baseline_task_minutes)
               - additional_review_minutes - revision_minutes - rework_probability*rework_minutes AS net_minutes,
           MIN(e.minutes_saved_low * transferability, baseline_task_minutes)
               - additional_review_minutes - revision_minutes - rework_probability*rework_minutes AS net_minutes_low,
           MIN(e.minutes_saved_high * transferability, baseline_task_minutes)
               - additional_review_minutes - revision_minutes - rework_probability*rework_minutes AS net_minutes_high
    FROM business_assumptions AS a
    CROSS JOIN time_effect AS e
), capacity AS (
    SELECT *, offered_seats * eligible_tasks_per_employee_month * net_minutes / 60.0 AS capacity_hours,
           offered_seats * eligible_tasks_per_employee_month * net_minutes_low / 60.0 AS capacity_hours_low,
           offered_seats * eligible_tasks_per_employee_month * net_minutes_high / 60.0 AS capacity_hours_high,
           offered_seats * assumed_seat_cost_month + fixed_operating_cost_month AS recurring_cost
    FROM task_value
), value AS (
    SELECT *, capacity_hours * loaded_hourly_value AS gross_capacity_value
    FROM capacity
)
SELECT *, gross_capacity_value - recurring_cost AS net_capacity_value,
       capacity_hours_low * loaded_hourly_value - recurring_cost AS effect_only_value_low,
       capacity_hours_high * loaded_hourly_value - recurring_cost AS effect_only_value_high,
       (gross_capacity_value - fixed_operating_cost_month) / NULLIF(offered_seats, 0) AS operating_seat_cost_ceiling,
       CASE WHEN gross_capacity_value > recurring_cost
            THEN setup_cost / (gross_capacity_value - recurring_cost) END AS capacity_payback_months
FROM value;

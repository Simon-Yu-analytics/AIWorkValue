-- Window function: records removed at each documented reconstruction stage.
-- The first row is raw survey records, not a randomized-participant denominator.
WITH stages AS (
    SELECT *, LAG(n) OVER (ORDER BY stage_order) AS previous_n,
           FIRST_VALUE(n) OVER (ORDER BY stage_order) AS raw_n
    FROM analysis_sample_flow
)
SELECT stage_order, stage, n,
       previous_n - n AS excluded_at_stage,
       ROUND(100.0 * n / NULLIF(previous_n, 0), 2) AS percent_retained_from_previous,
       ROUND(100.0 * n / NULLIF(raw_n, 0), 2) AS percent_of_raw_records
FROM stages ORDER BY stage_order;

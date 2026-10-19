-- Window totals expose treatment shares and task-order mix within retained strata.
-- These are descriptive diagnostics, not occupation-level causal rankings.
WITH counts AS (
    SELECT occupation, incentive_arm, assignment, COUNT(*) AS n,
           SUM(a_first = 1) AS task_a_first
    FROM participants WHERE primary_arm = 1
    GROUP BY occupation, incentive_arm, assignment
)
SELECT *, SUM(n) OVER (PARTITION BY occupation, incentive_arm) AS stratum_n,
       ROUND(100.0 * n / SUM(n) OVER (PARTITION BY occupation, incentive_arm), 2) AS assignment_share_pct,
       ROUND(100.0 * task_a_first / n, 2) AS task_a_first_pct
FROM counts ORDER BY occupation, incentive_arm, assignment;

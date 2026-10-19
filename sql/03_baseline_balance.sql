-- Balance diagnostic among retained primary-arm cases with observed baseline.
-- SMD = (AI mean - control mean) / sqrt((AI sample variance + control sample variance) / 2).
-- This does not prove balance in all randomized participants or remove attrition bias.
WITH baseline_long AS (
    SELECT assignment, 'time_minutes' AS outcome, time_pre AS baseline
    FROM participants WHERE primary_arm = 1 AND time_pre IS NOT NULL
    UNION ALL
    SELECT assignment, 'quality_points', grade_pre
    FROM participants WHERE primary_arm = 1 AND grade_pre IS NOT NULL
), moments AS (
    SELECT outcome, assignment, COUNT(*) AS n, AVG(baseline) AS mean,
           (SUM(baseline * baseline) - SUM(baseline) * SUM(baseline) / COUNT(*))
               / NULLIF(COUNT(*) - 1, 0) AS sample_variance
    FROM baseline_long GROUP BY outcome, assignment
), paired AS (
    SELECT c.outcome, c.n AS control_n, a.n AS ai_n,
           c.mean AS control_mean, a.mean AS ai_mean,
           (c.sample_variance + a.sample_variance) / 2.0 AS pooled_variance
    FROM moments AS c JOIN moments AS a ON c.outcome = a.outcome
    WHERE c.assignment = 0 AND a.assignment = 1
)
SELECT outcome, control_n, ai_n, control_mean, ai_mean,
       ai_mean - control_mean AS baseline_mean_difference,
       CASE WHEN pooled_variance > 0
            THEN (ai_mean - control_mean) / SQRT(pooled_variance) END AS standardized_mean_difference
FROM paired ORDER BY outcome;

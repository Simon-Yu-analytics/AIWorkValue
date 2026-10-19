-- Descriptive changes use exactly the same baseline/post pairs within each outcome.
-- This unadjusted difference in changes is not the Python ANCOVA coefficient.
WITH group_changes AS (
    SELECT outcome, assignment, COUNT(*) AS n,
           AVG(baseline) AS baseline_mean, AVG(post) AS post_mean,
           AVG(post - baseline) AS mean_change
    FROM v_outcome_pairs GROUP BY outcome, assignment
)
SELECT c.outcome, c.n AS control_n, a.n AS ai_n,
       c.baseline_mean AS control_baseline, a.baseline_mean AS ai_baseline,
       c.post_mean AS control_post, a.post_mean AS ai_post,
       c.mean_change AS control_change, a.mean_change AS ai_change,
       a.mean_change - c.mean_change AS unadjusted_difference_in_changes
FROM group_changes AS c JOIN group_changes AS a ON c.outcome = a.outcome
WHERE c.assignment = 0 AND a.assignment = 1 ORDER BY c.outcome;

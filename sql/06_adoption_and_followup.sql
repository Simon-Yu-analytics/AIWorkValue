-- Report response denominators alongside usage. Missing follow-up is not a 'no'.
SELECT assignment, COUNT(*) AS primary_arm_n,
       COUNT(used_ai) AS experimental_usage_responses,
       ROUND(100.0 * AVG(used_ai), 2) AS experimental_use_pct_among_responses,
       COUNT(followup_used_ai) AS followup_responses,
       ROUND(100.0 * COUNT(followup_used_ai) / COUNT(*), 2) AS followup_response_pct,
       ROUND(100.0 * AVG(followup_used_ai), 2) AS followup_use_pct_among_responses
FROM participants WHERE primary_arm = 1 GROUP BY assignment ORDER BY assignment;

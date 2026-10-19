-- Descriptive summaries of real experimental data; regression inference is in Python.
-- Only aggregate SQL outputs are committed; row-level records remain local.

SELECT assignment,COUNT(*) AS participants,
 ROUND(AVG(time_pre),2) AS mean_baseline_minutes,
 ROUND(AVG(time_post),2) AS mean_post_minutes,
 ROUND(AVG(grade_pre),3) AS mean_baseline_grade,
 ROUND(AVG(grade_post),3) AS mean_post_grade
FROM participants WHERE primary_arm=1 GROUP BY assignment;

-- Complete-case counts differ between the two primary outcomes.
SELECT assignment,COUNT(*) AS retained_primary_arm,
 SUM(time_pre IS NOT NULL AND time_post IS NOT NULL) AS valid_time_pairs,
 SUM(grade_pre IS NOT NULL AND grade_post IS NOT NULL) AS valid_quality_pairs
FROM participants WHERE primary_arm=1 GROUP BY assignment;

-- Observed use is an outcome, not a condition for selecting the causal sample.
SELECT assignment,COUNT(used_ai) AS usage_respondents,ROUND(AVG(used_ai),3) AS experimental_use,
 COUNT(followup_used_ai) AS followup_respondents,
 ROUND(AVG(followup_used_ai),3) AS workplace_use_among_followup_respondents
FROM participants WHERE primary_arm=1 GROUP BY assignment;

-- Occupation estimates are exploratory; no ranking of real workers is supported.
SELECT occupation,assignment,COUNT(*) AS participants,
 ROUND(AVG(time_post-time_pre),2) AS mean_time_change,
 ROUND(AVG(grade_post-grade_pre),3) AS mean_quality_change
FROM participants WHERE primary_arm=1
GROUP BY occupation,assignment ORDER BY occupation,assignment;

-- Conditional aggregation preserves denominators and exposes missing pairs.
SELECT assignment, COUNT(*) AS retained_primary_arm,
       SUM(time_pre IS NOT NULL AND time_post IS NOT NULL) AS time_pairs,
       SUM(grade_pre IS NOT NULL AND grade_post IS NOT NULL) AS quality_pairs,
       ROUND(100.0 * SUM(time_pre IS NOT NULL AND time_post IS NOT NULL) / COUNT(*), 2) AS time_pair_coverage_pct,
       ROUND(100.0 * SUM(grade_pre IS NOT NULL AND grade_post IS NOT NULL) / COUNT(*), 2) AS quality_pair_coverage_pct,
       SUM(time_pre IS NULL OR time_post IS NULL) AS missing_time_pairs,
       SUM(grade_pre IS NULL OR grade_post IS NULL) AS missing_quality_pairs
FROM participants WHERE primary_arm = 1 GROUP BY assignment ORDER BY assignment;

-- Automated zero-count expectations: missing outcomes are allowed, invalid values are not.
SELECT 'duplicate_participant_ids' AS check_name, COUNT(*) - COUNT(DISTINCT prolific_pid) AS violations FROM participants
UNION ALL
SELECT 'invalid_assignment', COUNT(*) FROM participants WHERE assignment IS NULL OR assignment NOT IN (0, 1)
UNION ALL
SELECT 'invalid_task_order', COUNT(*) FROM participants WHERE a_first IS NULL OR a_first NOT IN (0, 1)
UNION ALL
SELECT 'primary_arm_mismatch', COUNT(*) FROM participants
WHERE primary_arm IS NULL OR primary_arm NOT IN (0, 1)
   OR primary_arm != (incentive_arm IN ('linear', 'convex'))
UNION ALL
SELECT 'negative_time', COUNT(*) FROM participants WHERE time_pre < 0 OR time_post < 0
UNION ALL
SELECT 'out_of_range_rating', COUNT(*) FROM participants
WHERE grade_pre < 1 OR grade_pre > 7 OR grade_post < 1 OR grade_post > 7
UNION ALL
SELECT 'invalid_usage', COUNT(*) FROM participants
WHERE used_ai NOT IN (0, 1) OR followup_used_ai NOT IN (0, 1);

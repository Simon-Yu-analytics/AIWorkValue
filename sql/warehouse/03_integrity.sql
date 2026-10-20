SELECT 'dimension_join_row_expansion' AS check_name,
       (SELECT COUNT(*) FROM fact_outcome f
        JOIN dim_participant p USING(participant_key)
        JOIN dim_assignment a USING(assignment_key)
        JOIN dim_occupation o USING(occupation_key)
        JOIN dim_incentive i USING(incentive_key)
        JOIN dim_period t USING(period_key))
       - (SELECT COUNT(*) FROM fact_outcome) AS violations
UNION ALL
SELECT 'participant_mart_grain', ABS((SELECT COUNT(*) FROM mart_participant)
                                   - (SELECT COUNT(*) FROM dim_participant))
UNION ALL
SELECT 'missing_or_extra_measurement_period', COUNT(*) FROM (
    SELECT participant_key FROM fact_outcome GROUP BY participant_key HAVING COUNT(*) != 2
)
UNION ALL
SELECT 'assignment_changes_between_periods', COUNT(*) FROM (
    SELECT participant_key FROM fact_outcome GROUP BY participant_key
    HAVING COUNT(DISTINCT assignment_key)!=1 OR COUNT(DISTINCT occupation_key)!=1
        OR COUNT(DISTINCT incentive_key)!=1
)
UNION ALL
SELECT 'usage_join_count', ABS((SELECT COUNT(*) FROM mart_participant)
                            - (SELECT COUNT(*) FROM fact_usage))
UNION ALL
SELECT 'outcome_grain_duplicates', COUNT(*) FROM (
    SELECT participant_key,period_key FROM fact_outcome
    GROUP BY participant_key,period_key HAVING COUNT(*)>1
);

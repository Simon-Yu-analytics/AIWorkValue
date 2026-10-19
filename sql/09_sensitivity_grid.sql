-- Window comparison: how much value disappears with one more verification minute?
WITH grid AS (
    SELECT scenario, transferability, additional_review_minutes, net_capacity_value,
           LAG(net_capacity_value) OVER (
               PARTITION BY transferability ORDER BY additional_review_minutes
           ) AS previous_review_value
    FROM v_business_value WHERE scenario_kind = 'grid'
)
SELECT *, net_capacity_value - previous_review_value AS change_from_previous_review_setting,
       CASE WHEN net_capacity_value > 0 THEN 'positive capacity case'
            ELSE 'nonpositive capacity case' END AS operating_case
FROM grid ORDER BY transferability, additional_review_minutes;

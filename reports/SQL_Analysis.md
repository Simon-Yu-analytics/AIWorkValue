# SQL analysis: experiment checks and commercial decisions

Ten named SQL analyses extend the four introductory queries. They use CTEs, joins, conditional aggregation, reusable views and window functions. Participant-level inputs remain local; this report and the JSON contain aggregates only.

## Coverage and missingness

| assignment | retained_primary_arm | time_pairs | quality_pairs | time_pair_coverage_pct | quality_pair_coverage_pct | missing_time_pairs | missing_quality_pairs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 187 | 180 | 186 | 96.260 | 99.470 | 7 | 1 |
| 1 | 172 | 166 | 166 | 96.510 | 96.510 | 6 | 6 |

## Baseline balance

These are retained primary-arm participants with an observed baseline, not a balance test for every randomized participant. The standardized mean difference uses the square root of the mean of two sample variances. A small baseline difference does not resolve attrition bias.

| outcome | control_n | ai_n | control_mean | ai_mean | baseline_mean_difference | standardized_mean_difference |
| --- | --- | --- | --- | --- | --- | --- |
| quality_points | 186 | 166 | 3.970 | 3.969 | -0.001 | -0.001 |
| time_minutes | 180 | 167 | 28.969 | 29.802 | 0.833 | 0.057 |

## Paired pre/post comparisons

Each outcome uses complete baseline/post pairs. The difference in changes is descriptive and unadjusted; it is distinct from the baseline-adjusted Python regression.

| outcome | control_n | ai_n | control_baseline | ai_baseline | control_post | ai_post | control_change | ai_change | unadjusted_difference_in_changes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| quality_points | 186 | 166 | 3.970 | 3.969 | 3.830 | 4.518 | -0.140 | 0.549 | 0.689 |
| time_minutes | 180 | 166 | 28.969 | 29.681 | 26.883 | 16.831 | -2.086 | -12.849 | -10.763 |

## SQL-calculated commercial cases

Values use the same hypothetical assumptions and Python-estimated time effect. The SQL view calculates capacity, costs and operating boundaries independently. Released capacity is not a cash saving.

| scenario | capacity_hours | recurring_cost | net_capacity_value | operating_seat_cost_ceiling |
| --- | --- | --- | --- | --- |
| conservative | -13.838 | 3,000.000 | -3,484.321 | -9.843 |
| base | 105.658 | 3,000.000 | 698.025 | 31.980 |
| upside | 225.153 | 3,000.000 | 4,880.371 | 73.804 |

## Operating break-even boundaries

| scenario | operating_seat_cost_ceiling | max_additional_review_minutes_at_operating_break_even | min_tasks_per_offered_employee_month_at_operating_break_even | boundary_status |
| --- | --- | --- | --- | --- |
| base | 31.980 | 2.598 | 16.225 | positive per-task value |
| conservative | -9.843 | 0.013 | — | no positive per-task value at these assumptions |
| upside | 73.804 | 5.183 | 7.614 | positive per-task value |

## Reconciliation and data quality

All three named cases and 36 sensitivity points match the independent Python calculations within floating-point tolerance. Seven data-quality checks have zero violations.

| check_name | violations |
| --- | --- |
| duplicate_participant_ids | 0 |
| invalid_assignment | 0 |
| invalid_task_order | 0 |
| primary_arm_mismatch | 0 |
| negative_time | 0 |
| out_of_range_rating | 0 |
| invalid_usage | 0 |

## Explore the complete outputs

The [query guide](../sql/README.md) maps each SQL file to a business question. [sql-summaries.json](sql-summaries.json) includes all ten named result sets, the four introductory result sets, SQL text and reconciliation status. Rebuild with `make sql` after the local data reconstruction.

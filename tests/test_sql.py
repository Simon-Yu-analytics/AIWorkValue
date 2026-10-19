"""SQL invariants use small mathematical fixtures, not fabricated research results."""
from pathlib import Path
import json
import math
import sqlite3
import unittest
from aiworkvalue.sql_analysis import prepare_layer, query_file, run_queries, reconcile_business

ROOT = Path(__file__).resolve().parents[1]


class SQLTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute("""CREATE TABLE participants (
            prolific_pid TEXT, assignment INTEGER, occupation TEXT, incentive_arm TEXT,
            a_first INTEGER, primary_arm INTEGER, time_pre REAL, time_post REAL,
            grade_pre REAL, grade_post REAL, used_ai INTEGER, followup_used_ai INTEGER)""")
        self.connection.executemany("INSERT INTO participants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("c1", 0, "fixture", "linear", 1, 1, 10, 10, 3, 3, 0, 0),
            ("c2", 0, "fixture", "linear", 0, 1, 14, 12, 5, 4, 0, None),
            ("a1", 1, "fixture", "linear", 1, 1, 12, 8, 3, 4, 1, 1),
            ("a2", 1, "fixture", "linear", 0, 1, 16, 10, 5, 6, 1, None),
        ])
        self.results = json.loads((ROOT / "reports/results.json").read_text())
        prepare_layer(self.connection, self.results, ROOT / "sql")

    def tearDown(self):
        self.connection.close()

    def test_baseline_standardization_uses_sample_variance(self):
        rows = query_file(self.connection, ROOT / "sql/03_baseline_balance.sql")
        time = next(row for row in rows if row["outcome"] == "time_minutes")
        self.assertEqual(time["control_mean"], 12)
        self.assertEqual(time["ai_mean"], 14)
        self.assertAlmostEqual(time["standardized_mean_difference"], 2 / math.sqrt(8))

    def test_missing_post_is_not_counted_as_zero_or_a_complete_pair(self):
        self.connection.execute("INSERT INTO participants VALUES ('a3', 1, 'fixture', 'linear', 1, 1, 20, NULL, 4, NULL, 1, NULL)")
        coverage = query_file(self.connection, ROOT / "sql/02_group_coverage.sql")[1]
        self.assertEqual(coverage["retained_primary_arm"], 3)
        self.assertEqual(coverage["time_pairs"], 2)
        changes = query_file(self.connection, ROOT / "sql/04_paired_changes.sql")
        time = next(row for row in changes if row["outcome"] == "time_minutes")
        self.assertEqual(time["ai_n"], 2)
        self.assertEqual(time["unadjusted_difference_in_changes"], -4)
        usage = query_file(self.connection, ROOT / "sql/06_adoption_and_followup.sql")[1]
        self.assertEqual(usage["followup_responses"], 1)
        self.assertEqual(usage["followup_use_pct_among_responses"], 100)

    def test_business_sql_matches_python_for_named_cases_and_full_grid(self):
        queries = run_queries(self.connection, ROOT / "sql")
        check = reconcile_business(queries, self.results)
        self.assertEqual(check["business_cases"], 3)
        self.assertEqual(check["sensitivity_points"], 36)
        self.assertLess(check["max_absolute_numeric_difference"], 1e-8)

    def test_zero_seats_has_no_break_even_or_payback(self):
        self.connection.execute("UPDATE business_assumptions SET rollout_coverage=0 WHERE scenario='base'")
        row = next(row for row in query_file(self.connection, ROOT / "sql/07_business_scenarios.sql") if row["scenario"] == "base")
        self.assertEqual(row["net_capacity_value"], -500)
        self.assertIsNone(row["operating_seat_cost_ceiling"])
        self.assertIsNone(row["capacity_payback_months"])
        boundary = next(row for row in query_file(self.connection, ROOT / "sql/08_break_even.sql") if row["scenario"] == "base")
        self.assertIsNone(boundary["max_additional_review_minutes_at_operating_break_even"])
        self.assertIsNone(boundary["min_tasks_per_offered_employee_month_at_operating_break_even"])


if __name__ == "__main__":
    unittest.main()

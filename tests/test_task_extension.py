"""Known-value and boundary checks for the task-specific SQL extension."""
from pathlib import Path
import json
import unittest
from aiworkvalue.task_extension import evaluate_task_extension

ROOT = Path(__file__).resolve().parents[1]


class TaskExtensionTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "data/scenarios/weekly_status_email.json").read_text())
        self.sql = (ROOT / "sql/extensions/weekly_status_email.sql").read_text()

    def test_frequency_and_review_can_reverse_a_known_cost_case(self):
        self.config["base_assumptions"].update(revision_minutes=0,rework_probability=0,rework_minutes=0)
        result = evaluate_task_extension({"coefficient": -10, "ci95": [-11, -9]}, self.config, self.sql)
        rows = {(r["tasks_per_employee_month"], r["review_minutes"]): r for r in result["cases"]}
        # 100 seats, 4 tasks, (10*0.5 - 1) minutes, $35/hour, $3,000 recurring cost.
        self.assertAlmostEqual(rows[(4, 1)]["net_capacity_value"], -2066.6666666666665)
        self.assertGreater(rows[(20, 1)]["net_capacity_value"], 0)
        self.assertLess(rows[(20, 3)]["net_capacity_value"], 0)
        self.assertEqual(rows[(20, 5)]["net_capacity_value"], -3000)
        self.assertIsNone(rows[(20, 5)]["operating_break_even_tasks_per_employee_month"])
        self.assertEqual(result["reconciliation"]["cases"], 9)
        for row in rows.values():
            self.assertLessEqual(row["effect_only_low"], row["net_capacity_value"])
            self.assertGreaterEqual(row["effect_only_high"], row["net_capacity_value"])

    def test_baseline_cap_revision_and_expected_rework_reconcile(self):
        self.config["base_assumptions"].update(baseline_task_minutes=2,revision_minutes=.5,
                                                rework_probability=.2,rework_minutes=5)
        self.config["extra_review_minutes"]=[.5]
        result=evaluate_task_extension({"coefficient":-20,"ci95":[-22,-18]},self.config,self.sql)
        for row in result["cases"]:
            self.assertEqual(row["net_minutes_per_task"],0)
            self.assertEqual(row["ai_workflow_minutes"],2)
            self.assertEqual(row["net_capacity_value"],-3000)
            self.assertIsNone(row["operating_break_even_tasks_per_employee_month"])

    def test_invalid_or_duplicate_task_inputs_are_rejected(self):
        self.config["extra_review_minutes"] = [-1]
        with self.assertRaises(ValueError):
            evaluate_task_extension({"coefficient": -10, "ci95": [-11, -9]}, self.config, self.sql)
        self.config["extra_review_minutes"] = [1, 1]
        with self.assertRaises(ValueError):
            evaluate_task_extension({"coefficient": -10, "ci95": [-11, -9]}, self.config, self.sql)


if __name__ == "__main__":
    unittest.main()

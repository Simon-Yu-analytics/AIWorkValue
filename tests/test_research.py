"""Small mathematical fixtures, independent of the real study download."""
from dataclasses import replace
import unittest
import numpy as np
import pandas as pd
from aiworkvalue.data import map_tasks
from aiworkvalue.analysis import fit_record
from aiworkvalue.business import Scenario,value_case


class ResearchTests(unittest.TestCase):
    def test_counterbalanced_tasks_are_not_fixed_pre_post(self):
        pre,post=map_tasks(np.array([10,10]),np.array([20,20]),np.array([1,0]))
        np.testing.assert_array_equal(pre,[10,20]);np.testing.assert_array_equal(post,[20,10])

    def test_regression_recovers_a_known_assignment_contrast(self):
        rng=np.random.default_rng(42);n=600
        treatment=np.tile([0,1],n//2);baseline=rng.normal(size=n)
        outcome=3+2*treatment+.7*baseline+rng.normal(0,.2,n)
        d=pd.DataFrame({"assignment":treatment,"baseline":baseline,"outcome":outcome})
        r=fit_record(d,"outcome ~ assignment + baseline","fixture","units")
        self.assertAlmostEqual(r["coefficient"],2,delta=.06)
        self.assertEqual(r["n"],n)
        self.assertLess(r["ci95"][0],2);self.assertGreater(r["ci95"][1],2)

    def test_redundant_design_is_rejected(self):
        d=pd.DataFrame({"assignment":[0,1,0,1,0,1],"duplicate":[0,1,0,1,0,1],"outcome":[1,3,2,4,1,4]})
        with self.assertRaises(ValueError):fit_record(d,"outcome ~ assignment + duplicate","fixture","units")

    def test_minutes_hours_and_offered_seat_cost_reconcile(self):
        r=value_case(10)
        self.assertEqual(r["offered_employees"],100)
        self.assertEqual(r["capacity_hours_month"],100)
        self.assertEqual(r["recurring_cost_month"],3000)
        self.assertEqual(r["net_capacity_value_month"],500)
        self.assertEqual(r["capacity_value_payback_months"],6)

    def test_no_rollout_keeps_fixed_cost_and_no_payback(self):
        r=value_case(10,replace(Scenario(),rollout_coverage=0))
        self.assertEqual(r["net_capacity_value_month"],-500)
        self.assertIsNone(r["operating_break_even_seat_cost"])
        self.assertIsNone(r["capacity_value_payback_months"])

    def test_verification_can_destroy_value(self):
        r=value_case(10,replace(Scenario(),additional_review_minutes=6))
        self.assertLess(r["capacity_hours_month"],0)
        self.assertIsNone(r["capacity_value_payback_months"])

    def test_invalid_scenario_and_nonfinite_effect_rejected(self):
        for a in [replace(Scenario(),transferability=1.2),replace(Scenario(),assumed_seat_cost_month=-1)]:
            with self.assertRaises(ValueError):value_case(10,a)
        with self.assertRaises(ValueError):value_case(float("nan"))


if __name__=="__main__":unittest.main()

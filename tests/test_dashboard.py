"""Render every BI view and exercise real scenario controls without a browser."""
from pathlib import Path
import unittest
import logging
from streamlit.testing.v1 import AppTest
logging.disable(logging.DEBUG)

ROOT=Path(__file__).resolve().parents[1]


class DashboardTests(unittest.TestCase):
    def test_all_three_views_render_without_runtime_errors(self):
        app=AppTest.from_file(str(ROOT/"dashboard/app.py"),default_timeout=30).run()
        self.assertFalse(app.exception)
        for name in ["Productivity Analysis","Business Decision"]:
            app.radio(key="analysis_view").set_value(name).run()
            self.assertFalse(app.exception)

    def test_duration_and_rework_inputs_change_the_decision(self):
        app=AppTest.from_file(str(ROOT/"dashboard/app.py"),default_timeout=30).run()
        app.radio(key="analysis_view").set_value("Business Decision").run()
        before=app.metric[0].value
        app.number_input(key="baseline").set_value(1.0).run()
        self.assertFalse(app.exception)
        self.assertNotEqual(before,app.metric[0].value)
        self.assertTrue(any("cap applied" in info.value.lower() for info in app.info))
        cap_value=app.metric[0].value
        app.slider(key="rework_probability").set_value(100).run()
        self.assertFalse(app.exception)
        self.assertNotEqual(cap_value,app.metric[0].value)

    def test_setup_cost_changes_payback_but_not_recurring_monthly_value(self):
        app=AppTest.from_file(str(ROOT/"dashboard/app.py"),default_timeout=30).run()
        app.radio(key="analysis_view").set_value("Business Decision").run()
        app.number_input(key="review").set_value(1.0).run()
        monthly=app.metric[0].value
        self.assertTrue(any("payback: 5.2 months" in c.value for c in app.caption))
        app.number_input(key="setup").set_value(6000.0).run()
        self.assertFalse(app.exception)
        self.assertEqual(monthly,app.metric[0].value)
        self.assertTrue(any("payback: 10.3 months" in c.value for c in app.caption))

    def test_zero_coverage_keeps_fixed_cost_and_undefined_boundaries(self):
        app=AppTest.from_file(str(ROOT/"dashboard/app.py"),default_timeout=30).run()
        app.radio(key="analysis_view").set_value("Business Decision").run()
        app.slider(key="coverage").set_value(0).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.metric[0].value,"$-500")
        self.assertTrue(all(m.value=="Undefined" for m in app.metric[3:6]))
        self.assertTrue(any("No seats are offered" in info.value for info in app.info))

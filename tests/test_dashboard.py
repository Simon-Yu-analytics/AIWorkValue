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

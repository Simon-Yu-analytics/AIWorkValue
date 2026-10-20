"""Grain, idempotence, foreign-key and atomic-load checks with small fixtures."""
from pathlib import Path
import hashlib
import sqlite3
import tempfile
import unittest
import pandas as pd
from aiworkvalue.warehouse import load_warehouse, validate_participants

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    return pd.DataFrame([{"prolific_pid":f"fixture_{i}","assignment":i%2,"occupation":"fixture",
                          "incentive_arm":"linear","a_first":i%2,"primary_arm":True,
                          "time_pre":12.+i,"time_post":10.+i,"grade_pre":3.,"grade_post":4.,
                          "page_pre":15.,"page_post":12.,"used_ai":i%2,"followup_used_ai":None}
                         for i in range(4)])


class WarehouseTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.db=Path(self.folder.name)/"study.sqlite"
        self.frame=fixture()

    def tearDown(self):self.folder.cleanup()

    def test_repeated_snapshot_has_same_counts_and_no_join_inflation(self):
        first=load_warehouse(self.frame,self.db,ROOT/"sql/warehouse")
        second=load_warehouse(self.frame.sample(frac=1,random_state=3),self.db,ROOT/"sql/warehouse")
        self.assertEqual(first["table_rows"],second["table_rows"])
        self.assertEqual(first["kpis"],second["kpis"])
        self.assertEqual(second["table_rows"]["fact_outcome"],8)
        self.assertTrue(all(row["violations"]==0 for row in second["integrity_checks"]))
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM participants").fetchone()[0],4)
            unsafe=con.execute("SELECT COUNT(*) FROM fact_outcome a JOIN fact_outcome b USING(participant_key)").fetchone()[0]
            self.assertEqual(unsafe,16)  # why unqualified fact-to-fact joins are unsafe

    def test_invalid_rerun_does_not_replace_prior_good_snapshot(self):
        load_warehouse(self.frame,self.db,ROOT/"sql/warehouse")
        before=hashlib.sha256(self.db.read_bytes()).hexdigest()
        duplicate=pd.concat([self.frame,self.frame.iloc[[0]]],ignore_index=True)
        with self.assertRaises(ValueError):load_warehouse(duplicate,self.db,ROOT/"sql/warehouse")
        self.assertEqual(before,hashlib.sha256(self.db.read_bytes()).hexdigest())

    def test_foreign_keys_and_fact_grain_are_enforced(self):
        load_warehouse(self.frame,self.db,ROOT/"sql/warehouse")
        with sqlite3.connect(self.db) as con:
            con.execute("PRAGMA foreign_keys=ON")
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("INSERT INTO fact_usage VALUES (999,1,0)")
            with self.assertRaises(sqlite3.IntegrityError):
                con.execute("INSERT INTO fact_outcome SELECT * FROM fact_outcome LIMIT 1")

    def test_outlier_is_flagged_without_changing_research_data(self):
        self.frame.loc[0,"time_post"]=240
        audit=validate_participants(self.frame)
        self.assertEqual(audit["time_above_180_minutes"]["time_post"],1)
        self.assertEqual(self.frame.loc[0,"time_post"],240)
        self.frame.loc[0,"grade_post"]=8
        with self.assertRaises(ValueError):validate_participants(self.frame)

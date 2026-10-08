import csv
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare_csv',ROOT/'src/prepare_csv.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class ImportTests(unittest.TestCase):
    def setUp(self):
        with (ROOT/'data/demo_players.csv').open() as file:
            self.rows=list(csv.DictReader(file))
    def test_demo_is_retained_with_three_affected_records(self):
        clean,issues=mod.validate(self.rows)
        self.assertEqual(len(clean),36)
        self.assertEqual(len({i['csv_row'] for i in issues}),3)
    def test_unknown_is_not_zero(self):
        self.assertIsNone(mod.number('unknown',True))
        self.assertEqual(mod.number('0',True),0)
    def test_currency_units(self):
        self.assertEqual(mod.number('£1.2m',True),1200000)
        self.assertEqual(mod.number('£15K',True),15000)
    def test_ambiguous_ranges_and_units_are_rejected(self):
        for value in ['£1m-£2m','€15000','15000 p/a']:
            with self.assertRaises(ValueError):mod.number(value,True)
        with self.assertRaises(ValueError):mod.number('12-15')
    def test_duplicate_quarantine_and_blank_identity(self):
        self.rows[0]['Player ID']=self.rows[1]['Player ID']
        self.rows[2]['Player']=''
        _,issues=mod.validate(self.rows)
        self.assertTrue(any(x['csv_row']==2 and 'Duplicate' in x['reason'] for x in issues))
        self.assertTrue(any(x['csv_row']==3 and 'Duplicate' in x['reason'] for x in issues))
        self.assertTrue(any(x['csv_row']==4 and 'Missing identity' in x['reason'] for x in issues))
    def test_fee_inversion_and_out_of_range_attributes(self):
        self.rows[0]['Fee low GBP']='9000000';self.rows[0]['Passing']='21'
        _,issues=mod.validate(self.rows)
        self.assertEqual(len([x for x in issues if x['csv_row']==2]),2)
    def test_formula_injection_is_neutralised(self):
        self.rows[0]['Player']='=1+1'
        clean,issues=mod.validate(self.rows)
        self.assertEqual(clean[0]['Player'],"'=1+1")
        self.assertTrue(any('Formula-like' in x['reason'] for x in issues))
    def test_capacity_is_not_silently_truncated(self):
        with self.assertRaises(ValueError):mod.validate(self.rows*2)

if __name__=='__main__':unittest.main()

"""Audit the committed Excel artefact and independently check its cached outputs."""
import csv
import unittest
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'c':'http://schemas.openxmlformats.org/drawingml/2006/chart'}

class WorkbookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.zip=zipfile.ZipFile(ROOT/'workbook/FM Scout Lab.xlsx')
        cls.strings=[]
        if 'xl/sharedStrings.xml' in cls.zip.namelist():
            cls.strings=[''.join(n.itertext()) for n in ET.fromstring(cls.zip.read('xl/sharedStrings.xml'))]
        cls.sheets=[ET.fromstring(cls.zip.read(f'xl/worksheets/sheet{i}.xml')) for i in range(1,6)]
        with (ROOT/'data/demo_players.csv').open() as f:cls.rows=list(csv.DictReader(f))
    @classmethod
    def value(cls,sheet,address):
        c=next(c for c in cls.sheets[sheet-1].findall('.//s:c',NS) if c.attrib['r']==address)
        if c.attrib.get('t')=='inlineStr':return ''.join(c.find('s:is',NS).itertext())
        v=c.find('s:v',NS)
        if v is None:return None
        if c.attrib.get('t')=='s':return cls.strings[int(v.text)]
        if c.attrib.get('t')=='str':return v.text or ''
        return float(v.text) if v.text else None
    def test_native_workbook_features(self):
        names=self.zip.namelist()
        charts=[n for n in names if '/charts/chart' in n and n.endswith('.xml')]
        self.assertEqual(len(charts),3)
        for name in charts:
            self.assertTrue(ET.fromstring(self.zip.read(name)).findall('.//c:f',NS))
        self.assertEqual(len([n for n in names if n.startswith('xl/tables/table') and n.endswith('.xml')]),2)
        self.assertGreater(sum(len(s.findall('.//s:f',NS)) for s in self.sheets),900)
        self.assertGreater(sum(len(s.findall('.//s:dataValidation',NS)) for s in self.sheets),5)
        self.assertFalse(any('externalLinks' in n or 'vbaProject' in n for n in names))
    def test_no_cached_errors(self):
        errors=[c.attrib['r'] for s in self.sheets for c in s.findall('.//s:c',NS) if c.attrib.get('t')=='e']
        self.assertEqual(errors,[])
    def test_independent_shortlist(self):
        ids=Counter(r['Player ID'] for r in self.rows)
        expected=[]
        for i,r in enumerate(self.rows):
            if ids[r['Player ID']]!=1 or any(not v for v in r.values()):continue
            if r['Position group']!='Midfielder' or int(r['Age'])>27 or int(r['Fee high GBP'])>4500000 or int(r['Wage GBP/week'])>30000 or int(r['Minutes'])<900:continue
            score=sum(int(r[field])*weight for field,weight in [('Finishing',.05),('Passing',.30),('Tackling',.15),('Positioning',.20),('Pace',.10),('Work rate',.20)])/20*100
            cost=int(r['Fee high GBP'])+int(r['Wage GBP/week'])*52*3
            expected.append((r['Player'],score,cost,i))
        expected.sort(key=lambda r:(-r[1],r[3]))
        self.assertEqual(self.value(1,'B8'),len(expected))
        for i,(name,score,cost,_) in enumerate(expected):
            self.assertEqual(self.value(1,f'C{15+i}'),name)
            self.assertAlmostEqual(self.value(1,f'D{15+i}'),score)
            self.assertEqual(self.value(1,f'G{15+i}'),cost)
            dominated=any((other[1]>=score and other[2]<=cost) and (other[1]>score or other[2]<cost) for other in expected)
            self.assertEqual(self.value(1,f'H{15+i}'),'Dominated' if dominated else 'Frontier')
    def test_deliberate_exceptions_are_not_shortlisted(self):
        self.assertEqual(self.value(1,'J8'),3)
        for row in (35,36,37):self.assertEqual(self.value(3,f'M{row}'),'Fix data')
    def test_settings_and_comparison_are_live_formulas(self):
        for sheet,address in [(1,'C15'),(2,'C11'),(3,'K3'),(3,'P3'),(4,'C22')]:
            cell=next(c for c in self.sheets[sheet-1].findall('.//s:c',NS) if c.attrib['r']==address)
            self.assertIsNotNone(cell.find('s:f',NS))

if __name__=='__main__':unittest.main()

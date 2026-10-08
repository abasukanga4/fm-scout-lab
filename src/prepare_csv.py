"""Validate a mapped scouting CSV without replacing unknowns with invented values."""
import argparse
import csv
import json
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

HEADERS = ['Player ID','Player','Position group','Age','Fee low GBP','Fee high GBP',
           'Wage GBP/week','Minutes','Finishing','Passing','Tackling','Positioning','Pace','Work rate']
ROLES = {'Centre-back','Midfielder','Striker','Wide forward'}

def number(raw, money=False):
    text = str(raw).strip()
    if text.lower() in {'','-','unknown','n/a','na'}:
        return None
    if money:
        text = text.replace('£','').replace(',','').strip()
        match = re.fullmatch(r'(\d+(?:\.\d+)?)\s*([kKmM]?)', text)
        if not match:
            raise ValueError('Use a GBP amount; ranges and non-weekly wage units must be mapped explicitly')
        value = Decimal(match[1]) * {'':1,'k':1000,'m':1000000}[match[2].lower()]
    else:
        try:
            value = Decimal(text.replace(',',''))
        except InvalidOperation:
            raise ValueError('Use one whole number; masked attribute ranges remain unknown') from None
    if not value.is_finite() or value != value.to_integral_value():
        raise ValueError('A finite whole number is required')
    return int(value)

def validate(rows):
    ids = Counter(row.get('Player ID','').strip() for row in rows)
    output, issues = [], []
    for line,row in enumerate(rows,2):
        if not any(str(x).strip() for x in row.values()):
            continue
        clean = {}
        def issue(field,reason):
            issues.append({'csv_row':line,'player_id':row.get('Player ID',''),'field':field,'reason':reason})
        for field in HEADERS[:3]:
            clean[field] = row.get(field,'').strip()
            if clean[field].startswith(('=','+','-','@')):
                issue(field,'Formula-like text is not accepted')
                clean[field] = "'" + clean[field]
        if not clean['Player ID'] or not clean['Player']:
            issue('Player ID / Player','Missing identity')
        if clean['Player ID'] and ids[clean['Player ID']] > 1:
            issue('Player ID','Duplicate ID; all occurrences must be resolved')
        if clean['Position group'] not in ROLES:
            issue('Position group','Map to an explicit supported position group')
        for field in HEADERS[3:]:
            try:
                clean[field] = number(row.get(field,''),field in HEADERS[4:7])
                if clean[field] is None:
                    issue(field,'Missing value; excluded from the eligible shortlist')
            except ValueError as error:
                clean[field] = None
                issue(field,str(error))
        age = clean['Age']
        if age is not None and not 15 <= age <= 50:
            issue('Age','Outside supported 15–50 range')
        for field in HEADERS[4:8]:
            if clean[field] is not None and clean[field] < 0:
                issue(field,'Negative value')
        for field in HEADERS[8:]:
            if clean[field] is not None and not 1 <= clean[field] <= 20:
                issue(field,'Attribute must be 1–20')
        if clean['Fee low GBP'] is not None and clean['Fee high GBP'] is not None and clean['Fee low GBP'] > clean['Fee high GBP']:
            issue('Fee high GBP','Upper estimate is below lower estimate')
        output.append(clean)
    if len(output) > 60:
        raise ValueError('Workbook capacity is 60 players. Reduce the shortlist explicitly; no rows were silently truncated.')
    return output,issues

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    if len({args.source.resolve(),args.output.resolve(),args.report.resolve()}) != 3:
        parser.error('Source, output and report must be different paths')
    with args.source.open(encoding='utf-8-sig',newline='') as handle:
        reader=csv.DictReader(handle)
        if reader.fieldnames != HEADERS:
            parser.error('Map headers to data/demo_players.csv before validation; column order must match')
        rows=list(reader)
    try:
        prepared,issues=validate(rows)
    except ValueError as error:
        parser.error(str(error))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('w',encoding='utf-8',newline='') as handle:
        writer=csv.DictWriter(handle,fieldnames=HEADERS)
        writer.writeheader();writer.writerows(prepared)
    args.report.write_text(json.dumps({'records':len(prepared),'affected_records':len({x['csv_row'] for x in issues}),'issues':issues},indent=2)+'\n')
    print(f'{len(prepared)} records retained; {len(issues)} issues in {args.report}. Review before importing.')

if __name__ == '__main__':
    main()

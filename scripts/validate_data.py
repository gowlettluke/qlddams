#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def load(p):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'{p}: {e}');return {}
dams=load(ROOT/'data/dams.json').get('dams',[])
latest=load(ROOT/'data/latest.json').get('dams',[])
if len(dams)!=45:errors.append(f'expected 45 dams, got {len(dams)}')
if len({d.get('id') for d in dams})!=len(dams):errors.append('duplicate dam ids')
if len(latest)!=45:errors.append(f'expected 45 latest records, got {len(latest)}')
ids={d.get('id') for d in dams}
if {x.get('dam_id') for x in latest}!=ids:errors.append('latest dam ids do not match registry')
for d in dams:
    for k in ('latitude','longitude'):
        v=d.get(k)
        if not isinstance(v,(int,float)) or not math.isfinite(v):errors.append(f"{d.get('id')}: invalid {k}")
    hp=ROOT/'data/history'/f"{d.get('id')}.json"
    if not hp.exists():errors.append(f'{d.get("id")}: history file missing')
if errors:
    print('\n'.join('ERROR: '+x for x in errors));sys.exit(1)
print(f'Validated {len(dams)} dams, {len(latest)} latest records and all history files.')

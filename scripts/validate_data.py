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
documents=load(ROOT/'data/eap_documents.json').get('dams',{})
eap_status=load(ROOT/'data/eap_status.json').get('dams',[])
if len(dams)!=45:errors.append(f'expected 45 dams, got {len(dams)}')
if len({d.get('id') for d in dams})!=len(dams):errors.append('duplicate dam ids')
if len(latest)!=45:errors.append(f'expected 45 latest records, got {len(latest)}')
ids={d.get('id') for d in dams}
if {x.get('dam_id') for x in latest}!=ids:errors.append('latest dam ids do not match registry')
if set(documents)!=ids:errors.append(f'EAP document ids do not match registry ({len(documents)} records)')
if len(eap_status)!=45 or {x.get('dam_id') for x in eap_status}!=ids:errors.append('EAP status records do not match registry')
valid_indications={'below_alert','alert','lean_forward','stand_up','conditions_incomplete','unable_to_assess','not_applicable'}
valid_levels={'alert','lean_forward','stand_up'}
for d in dams:
    for k in ('latitude','longitude'):
        v=d.get(k)
        if not isinstance(v,(int,float)) or not math.isfinite(v):errors.append(f"{d.get('id')}: invalid {k}")
    hp=ROOT/'data/history'/f"{d.get('id')}.json"
    if not hp.exists():errors.append(f'{d.get("id")}: history file missing')
    doc=documents.get(d.get('id'),{})
    if doc.get('referable',True) and not isinstance(doc.get('rules',[]),list):errors.append(f'{d.get("id")}: EAP rules must be a list')
    for rule in doc.get('rules',[]):
        if rule.get('level') not in valid_levels:errors.append(f'{d.get("id")}: invalid EAP rule level {rule.get("level")}')
        if not isinstance(rule.get('conditions'),list):errors.append(f'{d.get("id")}: EAP rule conditions must be a list')
for row in eap_status:
    if row.get('indication') not in valid_indications:errors.append(f"{row.get('dam_id')}: invalid indication {row.get('indication')}")
    if row.get('formal_activation')!='not_confirmed':errors.append(f"{row.get('dam_id')}: formal activation must remain unconfirmed unless an authoritative source is integrated")
if errors:
    print('\n'.join('ERROR: '+x for x in errors));sys.exit(1)
print(f'Validated {len(dams)} dams, {len(latest)} latest records, {len(documents)} EAP documents, {len(eap_status)} EAP assessments and all history files.')

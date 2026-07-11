#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def load(p):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'{p}: {e}');return {}
def finite(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def official_bom_url(u):
    if not u: return True
    p=urlparse(str(u)); return p.scheme=='https' and p.netloc in {'www.bom.gov.au','hosting.wsapi.cloud.bom.gov.au'}
def walk(obj,path='root'):
    if isinstance(obj,float) and not math.isfinite(obj): errors.append(f'{path}: non-finite number')
    elif isinstance(obj,dict):
        for k,v in obj.items(): walk(v,f'{path}.{k}')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): walk(v,f'{path}[{i}]')

dams=load(ROOT/'data/dams.json').get('dams',[])
latest=load(ROOT/'data/latest.json').get('dams',[])
documents=load(ROOT/'data/eap_documents.json').get('dams',{})
eap_status=load(ROOT/'data/eap_status.json').get('dams',[])
gauges_payload=load(ROOT/'data/gauges.json')
walk(gauges_payload,'gauges.json')
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
        if not finite(v):errors.append(f"{d.get('id')}: invalid {k}")
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

statewide=gauges_payload.get('gauges', []) if isinstance(gauges_payload,dict) else []
gmap=gauges_payload.get('dams', {}) if isinstance(gauges_payload,dict) else {}
if not isinstance(statewide,list): errors.append('gauges.json: top-level gauges must be a list')
if not isinstance(gmap,dict): errors.append('gauges.json: top-level dams must be an object')
seen=set()
for i,g in enumerate(statewide if isinstance(statewide,list) else []):
    sid=g.get('id')
    label=f'gauge {sid or i} ({g.get("name")})'
    if not isinstance(sid,str) or not sid: errors.append(f'{label}: id must be a non-empty string')
    elif sid in seen: errors.append(f'{label}: duplicate statewide id')
    seen.add(sid)
    lat,lon=g.get('latitude'),g.get('longitude')
    if not finite(lat) or not finite(lon): errors.append(f'{label}: coordinates must be finite')
    elif not (-30.5 <= lat <= -9.0 and 137.0 <= lon <= 154.5): errors.append(f'{label}: coordinates outside plausible Queensland bounds ({lat},{lon})')
    cur=g.get('current') or {}; h=cur.get('height_m')
    if h is not None and not finite(h): errors.append(f'{label}: current.height_m must be finite or null')
    if cur.get('observed_at'):
        try: datetime.fromisoformat(str(cur['observed_at']).replace('Z','+00:00'))
        except Exception: errors.append(f'{label}: observed_at is not parseable: {cur.get("observed_at")}')
    for k in ('plot_url','table_url'):
        if g.get(k) and not official_bom_url(g.get(k)): errors.append(f'{label}: {k} is not an official HTTPS BOM URL')
    fs=cur.get('freshness_status')
    if fs not in {'current','stale','unavailable'}: errors.append(f'{label}: invalid freshness_status {fs}')
    if fs=='current' and cur.get('is_stale'): errors.append(f'{label}: current record cannot be stale')
    if fs=='unavailable' and (h is not None and cur.get('observed_at')): errors.append(f'{label}: unavailable record has both height and observed_at')
for dam_id, vals in (gmap.items() if isinstance(gmap,dict) else []):
    if dam_id not in ids: errors.append(f'gauges.json: dam key {dam_id} does not exist in data/dams.json')
    if not isinstance(vals,list): errors.append(f'gauges.json: dam {dam_id} value must be a list')
    for g in vals if isinstance(vals,list) else []:
        for k in ('plot_url','table_url','bulletin_url'):
            if g.get(k) and not official_bom_url(g.get(k)): errors.append(f'gauges.json: {dam_id}/{g.get("name")}: {k} is not official BOM HTTPS')
if errors:
    print('\n'.join('ERROR: '+x for x in errors));sys.exit(1)
print(f'Validated {len(dams)} dams, {len(latest)} latest records, {len(documents)} EAP documents, {len(eap_status)} EAP assessments, {len(statewide)} statewide BOM gauges and all history files.')

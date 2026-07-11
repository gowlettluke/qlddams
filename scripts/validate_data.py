#!/usr/bin/env python3
from __future__ import annotations
import json, math, sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]; errors=[]
def load(p):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception as e:errors.append(f'{p}: {e}');return {}
def finite(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def walk(obj,path='root'):
    if isinstance(obj,float) and not math.isfinite(obj): errors.append(f'{path}: non-finite number')
    elif isinstance(obj,dict):
        for k,v in obj.items(): walk(v,f'{path}.{k}')
    elif isinstance(obj,list):
        for i,v in enumerate(obj): walk(v,f'{path}[{i}]')
def official_https(u):
    p=urlparse(str(u or '')); return p.scheme=='https' and bool(p.netloc)
def official_bom_url(u):
    if not u: return True
    p=urlparse(str(u)); return p.scheme=='https' and p.netloc in {'www.bom.gov.au','hosting.wsapi.cloud.bom.gov.au'}
def valid_date(v):
    if not v: return True
    try:
        text=str(v)
        if len(text)==7: text += '-01'
        datetime.fromisoformat(text.replace('Z','+00:00')); return True
    except Exception: return False

dams=load(ROOT/'data/dams.json').get('dams',[]); latest=load(ROOT/'data/latest.json').get('dams',[])
documents=load(ROOT/'data/eap_documents.json').get('dams',{}); eap_status=load(ROOT/'data/eap_status.json').get('dams',[]); gauges_payload=load(ROOT/'data/gauges.json')
walk(gauges_payload,'gauges.json')
ids={d.get('id') for d in dams}
if len(dams)!=45:errors.append(f'expected 45 dams, got {len(dams)}')
if len(ids)!=len(dams):errors.append('duplicate dam ids')
if len(latest)!=45 or {x.get('dam_id') for x in latest}!=ids:errors.append('latest dam ids do not match registry')
if set(documents)!=ids or len(documents)!=45:errors.append(f'EAP document ids do not match registry ({len(documents)} records)')
if len(eap_status)!=45 or {x.get('dam_id') for x in eap_status}!=ids:errors.append('EAP status records do not match registry')
listed=[d for d in documents.values() if d.get('directory_status')=='listed']; notlisted=[d for d in documents.values() if d.get('directory_status')=='not_listed']
if len(listed)!=44 or len(notlisted)!=1 or notlisted[0].get('dam_id')!='nindooinbah-dam': errors.append('expected 44 listed EAPs and only Nindooinbah not_listed')
valid_results={'met','not_met','indeterminate','input_unavailable','document_conflict','document_expired','change_review_required','not_applicable'}
valid_states={'met','not_met','unknown','input_unavailable','datum_unverified','stale','document_conflict'}
valid_logic={'all'}
for dam_id,doc in documents.items():
    if doc.get('formal_activation_status')!='not_confirmed': errors.append(f'{dam_id}: formal activation must be not_confirmed')
    if doc.get('directory_status')=='listed' and not doc.get('rules'): errors.append(f'{dam_id}: listed record has no flood rules')
    if doc.get('directory_status')=='listed' and not official_https(doc.get('source_url') or doc.get('eap_url')): errors.append(f'{dam_id}: source URL must be official HTTPS')
    for k in ('issue_date','approved_date','expiry_date'):
        if not valid_date(doc.get(k)): errors.append(f'{dam_id}: invalid {k} {doc.get(k)}')
    for rule in doc.get('rules',[]):
        if rule.get('logic','all') not in valid_logic: errors.append(f'{dam_id}: invalid rule logic {rule.get("logic")}')
        if not rule.get('level'): errors.append(f'{dam_id}: missing activation level')
        for c in rule.get('conditions',[]):
            if isinstance(c.get('value'),(int,float)) and not isinstance(c.get('value'),bool) and not finite(c.get('value')): errors.append(f'{dam_id}: non-finite threshold')
for row in eap_status:
    dam_id=row.get('dam_id')
    if row.get('indicative_result') not in valid_results: errors.append(f'{dam_id}: invalid indicative_result {row.get("indicative_result")}')
    if row.get('formal_activation_status')!='not_confirmed' or row.get('formal_activation')!='not_confirmed': errors.append(f'{dam_id}: formal activation must remain not_confirmed')
    for rule in row.get('rules',[]):
        if rule.get('assessment')=='met' and any(c.get('state') in {'unknown','input_unavailable','datum_unverified','stale','document_conflict'} for c in rule.get('condition_results',[])): errors.append(f'{dam_id}: rule met with required unknown/unavailable condition')
        for c in rule.get('condition_results',[]):
            if c.get('state') not in valid_states: errors.append(f'{dam_id}: invalid condition state {c.get("state")}')
            if c.get('metric')=='storage_level_m' and c.get('actual') is not None and c.get('state')=='met' and row.get('observed_inputs',{}).get('storage_level_datum') not in {'AHD','m AHD'}: errors.append(f'{dam_id}: storage comparison without compatible datum')
    if row.get('document_status') in {'expired','document_conflict','change_review_required'} and row.get('confidence') in {'rules_verified_live_input_unavailable','public_pathway_supported','rules_verified_below_first_trigger'}: errors.append(f'{dam_id}: gated document presented as normal confidence')
if documents.get('callide-dam',{}).get('document_status')!='change_review_required': errors.append('Callide safeguard missing')
if not any(r.get('outflow_band_requires_review') for r in documents.get('callide-dam',{}).get('rules',[])): errors.append('Callide outflow band safeguard missing')
if documents.get('glenlyon-dam',{}).get('document_status')!='document_conflict': errors.append('Glenlyon conflict safeguard missing')
if not any(r.get('document_conflict') for r in documents.get('glenlyon-dam',{}).get('rules',[]) if r.get('level')=='alert'): errors.append('Glenlyon Alert conflict missing')
if documents.get('ewen-maddock-dam',{}).get('document_status')!='expired': errors.append('Ewen Maddock expiry missing')
# BOM gauges validation preserved
statewide=gauges_payload.get('gauges', []) if isinstance(gauges_payload,dict) else []; gmap=gauges_payload.get('dams', {}) if isinstance(gauges_payload,dict) else {}
if not isinstance(statewide,list): errors.append('gauges.json: top-level gauges must be a list')
if not isinstance(gmap,dict): errors.append('gauges.json: top-level dams must be an object')
seen=set()
for i,g in enumerate(statewide if isinstance(statewide,list) else []):
    sid=g.get('id'); label=f'gauge {sid or i} ({g.get("name")})'
    if not isinstance(sid,str) or not sid: errors.append(f'{label}: id must be a non-empty string')
    elif sid in seen: errors.append(f'{label}: duplicate statewide id')
    seen.add(sid); lat,lon=g.get('latitude'),g.get('longitude')
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
for dam_id, vals in (gmap.items() if isinstance(gmap,dict) else []):
    if dam_id not in ids: errors.append(f'gauges.json: dam key {dam_id} does not exist in data/dams.json')
    if not isinstance(vals,list): errors.append(f'gauges.json: dam {dam_id} value must be a list')
    for g in vals if isinstance(vals,list) else []:
        for k in ('plot_url','table_url','bulletin_url'):
            if g.get(k) and not official_bom_url(g.get(k)): errors.append(f'gauges.json: {dam_id}/{g.get("name")}: {k} is not official BOM HTTPS')
if errors:
    print('\n'.join('ERROR: '+x for x in errors)); sys.exit(1)
print(f'Validated {len(dams)} dams, {len(latest)} latest records, {len(documents)} EAP documents, {len(eap_status)} EAP assessments, {len(statewide)} statewide BOM gauges and all history files.')

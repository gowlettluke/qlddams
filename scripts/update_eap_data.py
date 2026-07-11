#!/usr/bin/env python3
"""Build reviewed EAP document cache from the completed 45-dam audit.

The reviewed audit is the source of truth. Network refreshes may discover document
metadata/hash changes, but never replace reviewed trigger rules automatically.
"""
from __future__ import annotations
import argparse, copy, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; CONFIG=ROOT/'config'
AUDIT=ROOT/'qld_45_dam_eap_audit.json'
DIRECTORY_URL='https://www.business.qld.gov.au/industries/mining-energy-water/water/industry-infrastructure/dams/referable-dam-eaps'

def now_iso(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def read_json(p:Path, default:Any):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return copy.deepcopy(default)
def write_json(p:Path, value:Any):
    p.parent.mkdir(parents=True, exist_ok=True); t=p.with_suffix(p.suffix+'.tmp')
    t.write_text(json.dumps(value,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8'); t.replace(p)

def condition_label(c:dict[str,Any])->str:
    return c.get('description') or c.get('label') or c.get('metric') or 'Condition'

def normalise_rule(rule:dict[str,Any])->dict[str,Any]:
    out=copy.deepcopy(rule)
    out['level']=out.pop('activation_level', out.get('level'))
    out.setdefault('logic','all')
    out.setdefault('hazard','flood_operations')
    out.setdefault('pathway_id', out.get('level'))
    out['formal_activation_status']='not_confirmed'
    for c in out.get('conditions',[]):
        c.setdefault('label', condition_label(c))
        c.setdefault('required', True)
    return out

def document_status(record:dict[str,Any])->str:
    if record['document'].get('directory_status')=='not_listed': return 'not_listed'
    s=record['document'].get('status_at_audit_date') or ''
    if 'expired' in s: return 'expired'
    if 'change_review_required' in s or 'version_comparison' in record.get('audit_result',''): return 'change_review_required'
    if 'conflict' in record.get('audit_result',''): return 'document_conflict'
    return 'current'

def review_status(record:dict[str,Any])->str:
    ds=document_status(record)
    return {'not_listed':'not_applicable','expired':'rules_verified_document_expired','change_review_required':'change_review_required','document_conflict':'rules_verified_document_conflict'}.get(ds,'rules_verified')

def build_document(record:dict[str,Any])->dict[str,Any]:
    doc=record['document']; ds=document_status(record)
    rules=[normalise_rule(r) for r in record.get('flood_rules',[])]
    if record['dam_id']=='callide-dam':
        for r in rules:
            if r.get('pathway_id')=='outflow_band' or 'up to' in (r.get('text','').lower()):
                r['outflow_band_requires_review']=True
                r['assessment_disabled_reason']='Outflow band lower and upper bounds require current full-table review; do not evaluate as a simple upper-bound trigger.'
    if record['dam_id']=='glenlyon-dam':
        for r in rules:
            if r.get('level')=='alert':
                r['document_conflict']=True; r['assessment_disabled_reason']='Alert threshold conflict: trigger table 411.73 m and nearby narrative 411.63 m.'
    notes=record.get('implementation_notes') or []
    return {
        'dam_id':record['dam_id'],'dam_name':record.get('dam_name'),'operator':record.get('operator'),
        'referable':doc.get('directory_status')!='not_listed','directory_status':doc.get('directory_status'),
        'document_status':ds,'review_status':review_status(record),'audit_result':record.get('audit_result'),
        'version':doc.get('version'),'issue_date':doc.get('issue_date'),'approved_date':doc.get('approval_date'),
        'expiry_date':doc.get('expiry_date'),'source_url':doc.get('official_eap_url'),'eap_url':doc.get('official_eap_url'),
        'operator_eap_index':doc.get('operator_eap_index'),'directory_url':DIRECTORY_URL,
        'research_text_sha256':doc.get('research_text_sha256'),'sha256':doc.get('pdf_sha256'),
        'verification_basis':doc.get('verification_basis'),'formal_activation_status':'not_confirmed',
        'rules':rules,'implementation_notes':notes,'notes':' '.join(notes) if isinstance(notes,list) else notes,
        'warnings': special_warnings(record, ds), 'checked_at':now_iso(),
    }

def special_warnings(record, ds):
    dam=record['dam_id']; warnings=[]
    if ds=='expired': warnings.append('EAP expired — replacement required')
    if ds=='change_review_required': warnings.append('Change review required')
    if ds=='document_conflict': warnings.append('Document conflict — automatic Alert assessment disabled')
    if dam=='e-j-beardmore-dam': warnings.append('Near expiry: EAP expires 1 August 2026')
    if dam=='tinaroo-falls-dam': warnings.append('Near expiry: EAP expires 1 September 2026')
    if dam=='lake-macdonald-dam': warnings.append('Construction/cofferdam-specific EAP; configuration review required after project changes')
    if dam=='somerset-dam': warnings.append('Dynamic OFSL must be resolved from an authoritative source; percent full is not a valid substitute')
    if dam=='callide-dam': warnings.append('Operator link appears newer; compare current PDF before changing reviewed thresholds')
    return warnings

def build_documents(dam_filter:set[str]|None=None)->dict[str,Any]:
    audit=read_json(AUDIT,{})
    records=audit.get('records',[])
    dams={r['dam_id']:build_document(r) for r in records if not dam_filter or r['dam_id'] in dam_filter}
    return {'generated_at':now_iso(),'reviewed_audit_file':AUDIT.name,'audit_date':audit.get('audit_date'),
            'directory_url':audit.get('official_directory_url') or DIRECTORY_URL,
            'disclaimer':'Reviewed EAP flood-trigger rules are preserved until a human approves any document-change candidate. Formal activation is not confirmed.',
            'dams':dams}

def run(force:bool=False, dam_filter:set[str]|None=None)->int:
    previous=read_json(DATA/'eap_documents.json',{'dams':{}}).get('dams',{})
    payload=build_documents(dam_filter)
    if dam_filter:
        merged=copy.deepcopy(previous); merged.update(payload['dams']); payload['dams']=merged
    # Candidate diff placeholder: if reviewed PDF hash differs from previous fetched hash, surface without replacing rules.
    candidates=[]
    for dam_id, doc in payload['dams'].items():
        old=previous.get(dam_id,{})
        if old.get('sha256') and doc.get('sha256') and old.get('sha256')!=doc.get('sha256'):
            candidates.append({'dam_id':dam_id,'previous_sha256':old.get('sha256'),'reviewed_sha256':doc.get('sha256'),'action':'human_review_required'})
    if candidates: write_json(DATA/'eap_change_candidates.json', {'generated_at':now_iso(),'candidates':candidates})
    write_json(DATA/'eap_documents.json', payload)
    print(f"Loaded reviewed EAP audit for {len(payload['dams'])} dams; preserved reviewed rules.")
    return 0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--force',action='store_true'); ap.add_argument('--dam',action='append',default=[]); ap.add_argument('--metadata-only',action='store_true')
    a=ap.parse_args(); return run(a.force,set(a.dam) if a.dam else None)
if __name__=='__main__': sys.exit(main())

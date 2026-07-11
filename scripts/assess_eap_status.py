#!/usr/bin/env python3
"""Assess reviewed EAP flood-trigger pathways against public live inputs.

This is an indicative public-data assessment only. Formal EAP activation is always
not_confirmed. Percentage full, BOM gauge heights, spilling flags and unverifed
datums are deliberately not used as reservoir-elevation substitutes.
"""
from __future__ import annotations
import copy,json,math,sys
from datetime import datetime,timezone,timedelta,date
from pathlib import Path
from typing import Any
from dateutil import parser as date_parser
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'
STAGE_ORDER={'alert':1,'lean_forward':2,'lean_forward_1':2,'stand_up':3,'stand_up_1':31,'stand_up_2':32,'stand_up_3':33,'stand_up_4':34,'stand_up_5':35}

def now_iso(): return datetime.now(timezone.utc).isoformat(timespec='seconds')
def load(p:Path,default:Any):
    try: return json.loads(p.read_text(encoding='utf-8'))
    except Exception: return copy.deepcopy(default)
def write(p:Path,v:Any):
    t=p.with_suffix(p.suffix+'.tmp'); t.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8'); t.replace(p)
def num(v):
    if v is None or isinstance(v,bool): return None
    try:
        f=float(v); return f if math.isfinite(f) else None
    except Exception: return None
def parse_time(v):
    if not v: return None
    try:
        d=date_parser.parse(str(v));
        if d.tzinfo is None: d=d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception: return None
def compare(a,op,e):
    if a is None: return None
    try:
        return {'>=':a>=e,'>':a>e,'<=':a<=e,'<':a<e,'==':a==e,'!=':a!=e}.get(op)
    except Exception: return None

def latest_history_level(history):
    vals=[]
    for r in history:
        v=num(r.get('storage_level_m')); dt=parse_time(r.get('storage_level_observed_at') or r.get('observed_at'))
        if v is not None and dt: vals.append((dt,v,r))
    return max(vals,default=(None,None,{}),key=lambda x:x[0] or datetime.min.replace(tzinfo=timezone.utc))

def storage_trend(history):
    vals=[]
    for r in history:
        v=num(r.get('storage_level_m')); dt=parse_time(r.get('storage_level_observed_at') or r.get('observed_at'))
        if v is not None and dt: vals.append((dt,v))
    vals.sort()
    if len(vals)<2: return None
    return 'rising' if vals[-1][1]>vals[0][1]+0.02 else 'falling' if vals[-1][1]<vals[0][1]-0.02 else 'steady'

def context_from_latest(latest, history):
    hdt,hlevel,hrow=latest_history_level(history)
    # Only current latest.json exact reservoir elevation may support comparison;
    # history is used for trend context, not as a live elevation substitute.
    lvl=num(latest.get('storage_level_m'))
    datum=latest.get('storage_level_datum')
    obs=latest.get('storage_level_observed_at') or latest.get('observed_at')
    quality=latest.get('storage_level_quality')
    return {'storage_level_m':lvl,'storage_trend':storage_trend(history),'storage_level_trend':storage_trend(history),
            'storage_level_datum':datum,'storage_level_observed_at':obs,'storage_level_quality':quality,
            'current_percent_full':num(latest.get('percent_full'))}

def metric_value(metric, ctx):
    # Explicitly refuse proxy substitutions.
    if metric in {'storage_level_m','storage_trend','storage_level_trend'}: return ctx.get(metric)
    if metric in {'distance_below_dynamic_ofsl_m','storage_level_relative_to_dynamic_ofsl'}: return None
    return ctx.get(metric)

def condition_state(c, ctx):
    metric=c.get('metric'); assess=c.get('assessability',''); label=c.get('label') or c.get('description') or metric
    if c.get('document_conflict') or assess=='document_conflict': state='document_conflict'; actual=None
    elif metric=='storage_level_m':
        actual=ctx.get('storage_level_m')
        datum=ctx.get('storage_level_datum')
        if actual is None: state='input_unavailable'
        elif datum not in {'AHD','m AHD'}: state='datum_unverified'
        else: state='met' if compare(actual,c.get('op','=='),c.get('value')) is True else 'not_met'
    elif metric in {'storage_trend','storage_level_trend'}:
        actual=ctx.get(metric)
        if actual is None: state='input_unavailable'
        else: state='met' if compare(actual,c.get('op','=='),c.get('value')) is True else 'not_met'
    elif assess.startswith('publicly_observable_if_sufficient_live_history'):
        actual=metric_value(metric,ctx); state='input_unavailable' if actual is None else ('met' if compare(actual,c.get('op','=='),c.get('value')) else 'not_met')
    elif assess.startswith('publicly_observable_only_if_official'):
        actual=metric_value(metric,ctx); state='input_unavailable' if actual is None else ('met' if compare(actual,c.get('op','=='),c.get('value')) else 'not_met')
    else:
        actual=metric_value(metric,ctx); state='unknown' if actual is None else ('met' if compare(actual,c.get('op','=='),c.get('value')) else 'not_met')
    return {'metric':metric,'label':label,'description':c.get('description'),'assessability':assess,'operator':c.get('op','=='),'expected':c.get('value'),'actual':actual,'unit':c.get('unit'),'state':state,'result':state}

def assess_rule(rule, ctx, doc):
    rr=copy.deepcopy(rule)
    if rr.get('document_conflict') or (doc.get('dam_id')=='glenlyon-dam' and rr.get('level')=='alert'):
        conds=[{**condition_state(c,ctx),'state':'document_conflict','result':'document_conflict'} for c in rr.get('conditions',[])]
        rr.update({'condition_results':conds,'assessment':'document_conflict','result':'document_conflict'}); return rr
    if rr.get('outflow_band_requires_review'):
        conds=[condition_state(c,ctx) for c in rr.get('conditions',[])]
        rr.update({'condition_results':conds,'assessment':'indeterminate','result':'indeterminate'}); return rr
    if doc.get('document_status')=='expired': gate='document_expired'
    elif doc.get('document_status')=='change_review_required': gate='change_review_required'
    else: gate=None
    conds=[condition_state(c,ctx) for c in rr.get('conditions',[])]
    states=[c['state'] for c in conds]
    if gate: res=gate
    elif states and all(s=='met' for s in states): res='met'
    elif 'document_conflict' in states: res='document_conflict'
    elif any(s in {'unknown','input_unavailable','datum_unverified','stale'} for s in states) and any(s=='met' for s in states): res='indeterminate'
    elif any(s in {'unknown','input_unavailable','datum_unverified','stale'} for s in states): res='input_unavailable' if any(s in {'input_unavailable','datum_unverified'} for s in states) else 'indeterminate'
    elif any(s=='not_met' for s in states): res='not_met'
    else: res='indeterminate'
    rr.update({'condition_results':conds,'assessment':res,'result':res}); return rr

def precise_reason(result, doc, unavailable):
    if result=='not_applicable': return 'No applicable EAP is listed for this dam in the current Queensland referable-dam EAP directory.'
    if result=='document_expired': return 'EAP expired — replacement required. Reviewed rules are preserved but not described as a current verified plan.'
    if result=='change_review_required': return 'Change review required. Reviewed rules are preserved until the replacement/current document is compared and approved.'
    if result=='document_conflict': return 'Document conflict — automatic Alert assessment disabled pending owner/regulator clarification.'
    if result=='input_unavailable': return 'Verified EAP rules are available, but official live reservoir elevation is unavailable.'
    if result=='indeterminate' and unavailable: return 'Indeterminate — level component met, '+unavailable[0]+' unavailable.'
    if result=='not_met': return 'Below the first public elevation trigger.'
    if result=='met': return 'A complete public trigger pathway is met; formal activation remains not confirmed.'
    return 'Verified EAP rules are available, but required public inputs are incomplete.'

def assess_one(dam, latest, history, doc):
    ctx=context_from_latest(latest,history); doc=copy.deepcopy(doc); rules=doc.get('rules',[])
    if not doc.get('referable',True) or doc.get('document_status')=='not_listed':
        return base(dam,doc,ctx,'not_applicable','not_applicable',[])
    assessed=[assess_rule(r,ctx,doc) for r in rules]
    unavailable=[]
    for r in assessed:
        for c in r.get('condition_results',[]):
            if c['state'] in {'unknown','input_unavailable','datum_unverified','stale'}: unavailable.append(c.get('label') or c.get('metric'))
    if doc.get('document_status')=='expired': res='document_expired'; highest=None; conf='rules_verified_document_expired'
    elif doc.get('document_status')=='change_review_required': res='change_review_required'; highest=None; conf='change_review_required'
    elif any(r['assessment']=='document_conflict' for r in assessed): res='document_conflict'; highest=None; conf='rules_verified_document_conflict'
    elif ctx.get('storage_level_m') is None and any(any(c.get('metric')=='storage_level_m' for c in r.get('conditions',[])) for r in rules): res='input_unavailable'; highest=None; conf='rules_verified_live_input_unavailable'
    else:
        met=[r for r in assessed if r['assessment']=='met']; ind=[r for r in assessed if r['assessment']=='indeterminate']; inp=[r for r in assessed if r['assessment']=='input_unavailable']
        if met: highest=max((r.get('level') for r in met), key=lambda x:STAGE_ORDER.get(x,0)); res='met'; conf='public_pathway_supported'
        elif ind: highest=None; res='indeterminate'; conf='required_condition_unavailable'
        elif inp: highest=None; res='input_unavailable'; conf='rules_verified_live_input_unavailable'
        else: highest=None; res='not_met'; conf='rules_verified_below_first_trigger'
    return base(dam,doc,ctx,res,conf,assessed,highest,unavailable)

def base(dam,doc,ctx,res,conf,rules=None,highest=None,unavailable=None):
    unavailable=list(dict.fromkeys(unavailable or []))
    return {'dam_id':dam['id'],'assessed_at':now_iso(),'document_status':doc.get('document_status'),'version':doc.get('version'),
            'expiry_date':doc.get('expiry_date'),'source_url':doc.get('source_url') or doc.get('eap_url'),
            'indicative_result':res,'indication':res,'highest_publicly_supported_level':highest,'potential_level':highest,
            'confidence':conf,'formal_activation_status':'not_confirmed','formal_activation':'not_confirmed',
            'observed_inputs':{'storage_level_m':ctx.get('storage_level_m'),'storage_level_datum':ctx.get('storage_level_datum'),
                               'storage_level_observed_at':ctx.get('storage_level_observed_at'),'storage_level_quality':ctx.get('storage_level_quality')},
            'current_percent_full':ctx.get('current_percent_full'),'storage_level_m':ctx.get('storage_level_m'),
            'storage_level_observed_at':ctx.get('storage_level_observed_at'),'storage_level_datum':ctx.get('storage_level_datum'),
            'rules':rules or [],'unavailable_required_inputs':unavailable,'missing_conditions':unavailable,
            'warnings':doc.get('warnings',[]),'reason':precise_reason(res,doc,unavailable),'eap':doc,
            'disclaimer':'Indicative public-data comparison with reviewed EAP flood rules only; formal activation is not confirmed.'}

def audit_report(statuses,docs):
    vals=list(docs.values())
    return {'generated_at':now_iso(),'total_dashboard_dams':len(statuses),'officially_listed_plans':sum(d.get('directory_status')=='listed' for d in vals),
            'reviewed_rules':sum(bool(d.get('rules')) for d in vals),'not_listed':sum(d.get('document_status')=='not_listed' for d in vals),
            'current':sum(d.get('document_status')=='current' for d in vals),'expired':sum(d.get('document_status')=='expired' for d in vals),
            'near_expiry':sum(any('Near expiry' in w for w in d.get('warnings',[])) for d in vals),
            'document_conflicts':sum(d.get('document_status')=='document_conflict' for d in vals),'change_review_required':sum(d.get('document_status')=='change_review_required' for d in vals),
            'records_with_exact_live_elevation':sum(s.get('observed_inputs',{}).get('storage_level_m') is not None and s.get('observed_inputs',{}).get('storage_level_datum') in {'AHD','m AHD'} for s in statuses),
            'records_missing_exact_live_elevation':sum(s.get('observed_inputs',{}).get('storage_level_m') is None for s in statuses),
            'rules_currently_assessable':sum(s.get('indicative_result')=='met' for s in statuses),
            'rules_indeterminate_due_non_public_conditions':sum(s.get('indicative_result')=='indeterminate' for s in statuses)}

def main():
    dams=load(DATA/'dams.json',{'dams':[]}).get('dams',[]); latest={x.get('dam_id'):x for x in load(DATA/'latest.json',{'dams':[]}).get('dams',[])}
    docs=load(DATA/'eap_documents.json',{'dams':{}}).get('dams',{})
    out=[]; counts={}
    for dam in dams:
        hist=load(DATA/'history'/f"{dam['id']}.json",{'observations':[]}).get('observations',[])
        st=assess_one(dam,latest.get(dam['id'],{}),hist,docs.get(dam['id'],{'dam_id':dam['id'],'rules':[]})); out.append(st); counts[st['indicative_result']]=counts.get(st['indicative_result'],0)+1
    write(DATA/'eap_status.json',{'generated_at':now_iso(),'counts':counts,'formal_activation_source':'not_integrated','public_warning_source':'not_integrated','disclaimer':'Indicative only; not formal EAP activation or public warning advice.','dams':out})
    write(DATA/'eap_audit_report.json',audit_report(out,docs)); print(f'Assessed {len(out)} dams: {counts}'); return 0
if __name__=='__main__': sys.exit(main())

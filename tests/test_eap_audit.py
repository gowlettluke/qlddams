from pathlib import Path
import copy, json, sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.assess_eap_status import assess_one
from scripts.update_eap_data import build_documents, run as update_run
DOCS=build_documents()['dams']
DAMS={d['id']:d for d in json.loads((ROOT/'data/dams.json').read_text(encoding='utf-8'))['dams']}

def latest(level=None, datum='AHD', percent=100):
    return {'dam_id':'x','percent_full':percent,'storage_level_m':level,'storage_level_datum':datum,'storage_level_observed_at':'2026-07-11T00:00:00+00:00','storage_level_quality':'official_exact'}

def assess(dam_id, level=None, datum='AHD', history=None, extra=None):
    l=latest(level,datum); 
    if extra: l.update(extra)
    return assess_one(DAMS[dam_id], l, history or [], DOCS[dam_id])

def test_all_45_audit_records_load(): assert len(DOCS)==45 and sum(d['directory_status']=='listed' for d in DOCS.values())==44

def test_nindooinbah_not_applicable():
    r=assess('nindooinbah-dam')
    assert r['indicative_result']=='not_applicable' and 'No applicable EAP' in r['reason']

def test_seqwater_alert_indeterminate_when_level_met_bom_unknown():
    r=assess('atkinson-dam',65.72)
    assert r['indicative_result']=='indeterminate' and any('BOM' in x or 'warning' in x.lower() for x in r['unavailable_required_inputs'])

def test_seqwater_lean_forward_supported_by_exact_level():
    r=assess('atkinson-dam',68.66)
    assert r['indicative_result']=='met' and r['highest_publicly_supported_level']=='lean_forward'

def test_seqwater_stand_up_indeterminate_without_failure_judgement():
    r=assess('atkinson-dam',74.5)
    assert any(rule['level'].startswith('stand_up') and rule['assessment']=='indeterminate' for rule in r['rules'])

def test_sunwater_rising_condition_not_met_without_history():
    r=assess('fairbairn-dam',204.13)
    alert=[x for x in r['rules'] if x['level']=='alert'][0]
    assert any(c['metric'] in {'storage_trend','storage_level_trend'} and c['state']=='input_unavailable' for c in alert['condition_results'])

def test_sunwater_final_wave_dst_dam_pathway_indeterminate_without_judgement():
    doc=DOCS['burdekin-falls-dam']
    assert any(any('operator' in c.get('assessability','') or 'judgement' in c.get('assessability','') or 'DSTDM' in c.get('description','') for c in r.get('conditions',[])) for r in doc['rules'])
    r=assess('burdekin-falls-dam',999)
    assert any(x['assessment']=='indeterminate' for x in r['rules'])

def test_fairbairn_stage_thresholds_preserved():
    vals=[c['value'] for rule in DOCS['fairbairn-dam']['rules'] for c in rule['conditions'] if c.get('metric')=='storage_level_m']
    for v in [204.13,204.23,207.73,209.80,217.39]: assert v in vals

def test_callide_outflow_bands_not_simple_upper_bound():
    assert DOCS['callide-dam']['document_status']=='change_review_required'
    assert any(r.get('outflow_band_requires_review') for r in DOCS['callide-dam']['rules'])

def test_glenlyon_alert_document_conflict():
    r=assess('glenlyon-dam',412)
    assert r['indicative_result']=='document_conflict'
    assert any(x['level']=='alert' and x['assessment']=='document_conflict' for x in r['rules'])

def test_ewen_maddock_document_expired(): assert assess('ewen-maddock-dam',30)['indicative_result']=='document_expired'

def test_somerset_refuses_percent_full_comparison():
    r=assess('somerset-dam',None, extra={'percent_full':200})
    assert r['indicative_result']=='input_unavailable' and r['observed_inputs']['storage_level_m'] is None

def test_lake_macdonald_construction_context(): assert 'Construction/cofferdam' in ' '.join(DOCS['lake-macdonald-dam']['warnings'])

def test_gate_and_flood_manual_conditions_non_public():
    for dam in ['wivenhoe-dam','north-pine-dam','somerset-dam']:
        assert any(any('gate' in c.get('assessability','').lower() or 'operator' in c.get('assessability','').lower() or 'manual' in c.get('description','').lower() for c in r.get('conditions',[])) for r in DOCS[dam]['rules'])

def test_null_live_elevation_confidence(): assert assess('atkinson-dam')['confidence']=='rules_verified_live_input_unavailable'

def test_datum_mismatch_blocks_comparison():
    r=assess('atkinson-dam',99,datum='unknown')
    assert any(c['state']=='datum_unverified' for rule in r['rules'] for c in rule['condition_results'])

def test_formal_activation_always_not_confirmed(): assert all(assess(d)['formal_activation_status']=='not_confirmed' for d in ['atkinson-dam','callide-dam','nindooinbah-dam'])

def test_reviewed_rules_survive_failed_pdf_refresh():
    before=len(DOCS['fairbairn-dam']['rules'])
    assert before>0
    assert update_run(False, {'fairbairn-dam'})==0
    after=json.loads((ROOT/'data/eap_documents.json').read_text(encoding='utf-8'))['dams']['fairbairn-dam']
    assert len(after['rules'])==before and after['review_status'].startswith('rules_verified')


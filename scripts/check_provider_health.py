#!/usr/bin/env python3
"""Fail only when a required current provider is completely unavailable.

Partial coverage remains visible in provider_health.json and the dashboard, but does
not turn every scheduled deployment red when the last-good records are retained.
"""
import json, sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/provider_health.json'
h=json.loads(p.read_text())
required=('seqwater_current','sunwater_current')
failed=[]
partial=[]
for name in required:
    status=h.get('providers',{}).get(name,{}).get('status','missing')
    if status in {'failed','missing'}: failed.append(f'{name}: {status}')
    elif status != 'ok': partial.append(f'{name}: {status}')
if partial: print('Required current feed coverage warning: '+', '.join(partial))
if failed:
    print('Required current feed failure: '+', '.join(failed));sys.exit(1)
print('Required current providers supplied usable current data.')

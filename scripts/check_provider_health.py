#!/usr/bin/env python3
"""Fail the workflow after data is committed when required current feeds fail."""
import json, sys
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/provider_health.json'
h=json.loads(p.read_text())
required=('seqwater_current','sunwater_current')
bad=[f"{name}: {h.get('providers',{}).get(name,{}).get('status','missing')}" for name in required if h.get('providers',{}).get(name,{}).get('status') not in {'ok'}]
if bad:
    print('Required current feed warning: '+', '.join(bad));sys.exit(1)
print('Required current feeds are healthy.')

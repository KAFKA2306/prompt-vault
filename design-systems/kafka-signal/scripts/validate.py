#!/usr/bin/env python3
from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];errors=[]
for rel in ['DESIGN.md','USAGE.md','tokens.json','tokens.css','tokens.schema.json','components.html','voice.md','anti-patterns.md','icons/index.json','icons/sprite.svg','characters/kafka-character.json','assets/provenance.json']:
 if not (R/rel).is_file():errors.append('missing '+rel)
t=json.loads((R/'tokens.json').read_text())
if t['meta']['version']!='1.0.0':errors.append('version')
for p in R.rglob('*.svg'):
 s=p.read_text().lower()
 if '<script' in s or 'onload=' in s:errors.append('unsafe svg '+str(p))
if errors:print('\n'.join(errors),file=sys.stderr);raise SystemExit(1)
print('KAFKA SIGNAL validation passed')

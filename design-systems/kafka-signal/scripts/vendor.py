#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,shutil
FILES=['tokens.css','tokens.json','icons/index.json','icons/sprite.svg','characters/kafka-character.json','assets/provenance.json']
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--commit',required=True);a=p.parse_args();records=[]
for rel in FILES:
 s=a.source/rel;d=a.destination/rel;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,d);records.append({'path':rel,'sha256':hashlib.sha256(d.read_bytes()).hexdigest()})
(a.destination/'kafka-signal.lock.json').write_text(json.dumps({'release':'kafka-signal-v1.0.0','commit':a.commit,'files':records},indent=2)+'\n')

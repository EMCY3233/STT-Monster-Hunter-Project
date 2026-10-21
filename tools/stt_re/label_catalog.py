"""Read-only DTI name hints; labels from a supplied public dictionary are not validation."""
import argparse
import json
from pathlib import Path
import sqlite3

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bank',type=Path,required=True)
    p.add_argument('--dictionary',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    labels=json.loads(a.dictionary.read_text(encoding='utf-8'))
    db=sqlite3.connect(a.bank.resolve().as_uri()+'?mode=ro',uri=True)
    rows=[dict(type_id=i,dictionary_label=labels.get(i.upper().removeprefix('0X'),'UNKNOWN'),entries=n)
          for i,n in db.execute('SELECT type_id,count(*) FROM entries GROUP BY type_id ORDER BY count(*) DESC')]
    db.close()
    with a.output.open('x',encoding='utf-8') as f:
        f.write(json.dumps(rows,indent=2)+'\n')

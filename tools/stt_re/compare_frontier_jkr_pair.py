"""Compare two bounded derived samples without exporting bytes or strings."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

def stats(data):
    lengths=[len(x) for x in data.split(b'\0') if x]
    return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),nul_bytes=data.count(0),nonempty_nul_spans=len(lengths),nonempty_span_length_histogram=dict(sorted(Counter(lengths).items())),maximum_nonempty_span=max(lengths,default=0),ends_with_nul=data.endswith(b'\0'))

def compare(a,b,regions):
    if not 0<len(a)<=4096 or not 0<len(b)<=4096: raise ValueError('pair budget exceeded')
    prefix=0
    for x,y in zip(a,b):
        if x!=y: break
        prefix+=1
    previous=0; windows=[]
    for r in regions:
        at=r['offset']; end=at+r['bytes']
        if at<previous or end>=len(a) or a[end]!=0: raise ValueError('control anchor bounds')
        if at-previous>=11: windows.append(a[at-11:at])
        previous=end+1
    constants={i:windows[0][i] for i in range(11) if windows and len(set(w[i] for w in windows))==1}
    matches=[at for at in range(len(b)-10) if constants and all(b[at+i]==value for i,value in constants.items())]
    return dict(control=stats(a),contrast=stats(b),common_prefix_bytes=prefix,control_prefix_windows=len(windows),invariant_prefix_columns=sorted(constants),contrast_partial_pattern_matches=matches,pattern_is_not_grammar=True,semantics_verified=False,scope='one pair only; NUL span statistics and control-derived byte-pattern hypothesis, no strings')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--control',type=Path,required=True)
    p.add_argument('--contrast',type=Path,required=True)
    p.add_argument('--control-regions',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    for source in (a.control,a.contrast):
        if source.stat().st_size>4096: raise ValueError('source outside pair budget')
    original=a.control.read_bytes(); contrast=a.contrast.read_bytes(); regions=json.loads(a.control_regions.read_text())
    if hashlib.sha256(original).hexdigest()!=regions['source_sha256']: raise ValueError('control report mismatch')
    report=compare(original,contrast,regions['regions'])
    report['inputs_unchanged']=original==a.control.read_bytes() and contrast==a.contrast.read_bytes()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

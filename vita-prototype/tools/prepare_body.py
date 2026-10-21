"""Remove only the original sample's blade mesh; preserve its socket and poses."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]/'assets'
raw=(root/'practice.pose.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='a6648b5901bf6282457062911946399aa3019cc7fb23a661bfc5aa81550dfcdc'
data=json.loads(raw)
assert data['parents']==[-1,0,1,2] and len(data['triangles'])==72
retained=[]
for triangle in data['triangles']:
    if max(triangle)<40:retained.append(triangle)
    else:assert min(triangle)>=40
assert len(retained)==60
data['triangles']=retained
for clip in data['clips']:
    for frame in clip['frames']:
        assert len(frame['vertices'])==48 and len(frame['joints'])==4
        frame['vertices']=frame['vertices'][:40]
output=json.dumps(data,separators=(',',':')).encode()
assert len(output)<=163840
(root/'hunter-body.pose.json').write_bytes(output)
print('body:',len(output),'bytes; SHA256:',hashlib.sha256(output).hexdigest())

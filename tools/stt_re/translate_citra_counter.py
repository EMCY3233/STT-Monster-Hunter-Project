"""Translate verified observations into qualified counter hypotheses, not field identities."""
import argparse
import hashlib,json,struct
from collections import Counter
from pathlib import Path


def summarize(samples, times):
    if len(samples)<2 or len(samples)!=len(times) or any(len(x)!=32 for x in samples):
        raise ValueError('at least two paired 32-byte samples required')
    if any(b<=a for a,b in zip(times,times[1:])):
        raise ValueError('strictly increasing sample times required')
    fields={}
    for offset in (4,8):
        v=[struct.unpack_from('<I',s,offset)[0] for s in samples]
        deltas=[(b-a)&0xffffffff for a,b in zip(v,v[1:])]
        total=sum(deltas)
        fields[str(offset)]=dict(changed_pairs=sum(d!=0 for d in deltas),observed_units=total,
            units_per_host_second=total/(times[-1]-times[0]),
            small_forward_deltas_only=all(d<1000 for d in deltas))
    differences=Counter((struct.unpack_from('<I',s,8)[0]-struct.unpack_from('<I',s,4)[0])&0xffffffff for s in samples)
    return dict(samples=len(samples),fields=fields,paired_fields_equal=all(s[4:8]==s[8:12] for s in samples),
        paired_difference_u32_counts=[dict(delta=d,count=n) for d,n in sorted(differences.items())],
        interpretation='periodic progress candidates; equality reported separately; field meaning and frame identity unverified',
        semantic_identity_verified=False)


def load_summary(folder):
    folder=Path(folder);receipt=json.loads((folder/'receipt.json').read_text())
    sha=lambda x:hashlib.sha256(x).hexdigest()
    binary=(folder/'samples.bin').read_bytes();index=(folder/'reads.jsonl').read_bytes()
    if sha(binary)!=receipt['samples_sha256'] or sha(index)!=receipt['reads_sha256'] or sha((folder/'protocol.json').read_bytes())!=receipt['protocol_sha256']:
        raise ValueError('capture identity mismatch')
    if not receipt['control_before_matches'] or not receipt['control_after_matches'] or receipt['errors']:
        raise ValueError('capture controls/errors unacceptable')
    rows=[json.loads(x) for x in index.splitlines()];samples=[]
    if len(binary)!=len(rows)*32:
        raise ValueError('capture length mismatch')
    for i,row in enumerate(rows):
        value=binary[i*32:(i+1)*32]
        if row['binary_offset']!=i*32 or sha(value)!=row['sha256']:
            raise ValueError('sample identity mismatch')
        samples.append(value)
    return summarize(samples,[r['utc_start'] for r in rows])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folder',type=Path)
    print(json.dumps(load_summary(p.parse_args().folder),indent=2))

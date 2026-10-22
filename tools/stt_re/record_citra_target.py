"""Record one verified BSS window; field statistics do not establish field types."""
import argparse
from collections import Counter
import hashlib,json,math,struct,time
from pathlib import Path
from observe_citra_session import read_memory
from sample_citra_data_windows import plan_bss_windows


def sha(data):return hashlib.sha256(data).hexdigest()


def field_stats(samples):
    if not samples:return dict(samples=0,changed_byte_indices=[],u32_le=[])
    size=len(samples[0])
    if size!=32 or any(len(s)!=size for s in samples):raise ValueError('32-byte samples required')
    changed=sorted({i for a,b in zip(samples,samples[1:]) for i,(x,y) in enumerate(zip(a,b)) if x!=y})
    fields=[]
    for offset in range(0,32,4):
        values=[struct.unpack_from('<I',s,offset)[0] for s in samples]
        deltas=[(y-x)&0xffffffff for x,y in zip(values,values[1:])]
        fields.append(dict(byte_offset=offset,distinct_bit_patterns=len(set(values)),
            changed_pairs=sum(d!=0 for d in deltas),comparable_pairs=len(deltas),
            modular_delta_counts=[dict(delta=d,count=n) for d,n in sorted(Counter(deltas).items())],
            interpretation='aligned unsigned little-endian bit view; actual type unknown'))
    return dict(samples=len(samples),changed_byte_indices=changed,u32_le=fields)


def record(prior,image_path,mapping_path,out,condition,window=139,seconds=12,interval=0.1):
    if condition not in ('user-declared-idle','user-declared-action','assistant-issued-action','uncontrolled'):
        raise ValueError('invalid condition label')
    if not math.isfinite(seconds) or not 0<seconds<=60 or not math.isfinite(interval) or not 0.1<=interval<=1:
        raise ValueError('duration <=60 seconds; interval 0.1..1')
    prior=Path(prior);image=Path(image_path).read_bytes();mapping_bytes=Path(mapping_path).read_bytes();mapping=json.loads(mapping_bytes)
    plan_bytes=(prior/'protocol.json').read_bytes();plan=json.loads(plan_bytes);receipt=json.loads((prior/'receipt.json').read_bytes())
    if sha(plan_bytes)!=receipt['protocol_sha256'] or sha(image)!=plan['static_image_sha256'] or sha(image)!=mapping['output_sha256'] or sha(mapping_bytes)!=plan['mapping_sha256']:
        raise ValueError('source identity mismatch')
    expected=plan_bss_windows(mapping,len(image),plan['stride'])
    if plan['region']!='bss' or expected!=plan['windows'] or type(window) is not int or not 0<=window<len(expected):
        raise ValueError('window outside verified BSS plan')
    target=expected[window]
    if target['size']!=32:raise ValueError('target must be exactly 32 bytes')
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    control=plan['control'];control_bytes=image[control['file_offset']:control['file_offset']+4]
    protocol=dict(condition=condition,condition_independently_observed=False,window=window,address=target['address'],size=32,seconds=seconds,interval=interval,prior_protocol_sha256=sha(plan_bytes),image_sha256=sha(image),atomic_snapshot=False,raw_bytes_private=True)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n',encoding='utf-8')
    before=read_memory(control['address'],4)
    if before!=control_bytes:
        (out/'failure.json').write_text(json.dumps(dict(stop_reason='control_mismatch_before',target_reads=0))+'\n',encoding='utf-8')
        raise ValueError('control mismatch before capture')
    start=time.perf_counter();deadline=start+seconds;samples=[];attempts=errors=consecutive=0;reason='complete'
    with (out/'samples.bin').open('xb') as binary,(out/'reads.jsonl').open('x',encoding='utf-8') as records:
        while time.perf_counter()<deadline:
            begun=time.perf_counter();attempts+=1
            row=dict(start_seconds=begun-start,utc_start=time.time())
            try:
                value=read_memory(target['address'],32,timeout=min(0.25,deadline-begun))
                row.update(binary_offset=len(samples)*32,sha256=sha(value));samples.append(value);binary.write(value);consecutive=0
            except (OSError,ValueError) as exc:
                errors+=1;consecutive+=1;row['error_type']=type(exc).__name__
            row['end_seconds']=time.perf_counter()-start;records.write(json.dumps(row)+'\n');records.flush()
            if consecutive>=4:reason='four_consecutive_errors';break
            time.sleep(min(max(0,interval-(time.perf_counter()-begun)),max(0,deadline-time.perf_counter())))
    elapsed=time.perf_counter()-start;after_ok=False
    try:after_ok=read_memory(control['address'],4)==control_bytes
    except (OSError,ValueError):pass
    result=dict(condition=condition,address=target['address'],attempts=attempts,successes=len(samples),errors=errors,elapsed_seconds=elapsed,stop_reason=reason,control_before_matches=True,control_after_matches=after_ok,extracted_bytes=len(samples)*32,stats=field_stats(samples),samples_sha256=sha((out/'samples.bin').read_bytes()),reads_sha256=sha((out/'reads.jsonl').read_bytes()),protocol_sha256=sha((out/'protocol.json').read_bytes()),semantic_identity_verified=False,action_effect_verified=False,memory_writes=False)
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('prior','image','mapping','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--condition',choices=['user-declared-idle','user-declared-action','assistant-issued-action','uncontrolled'],required=True)
    p.add_argument('--window',type=int,default=139);p.add_argument('--seconds',type=float,default=12);p.add_argument('--interval',type=float,default=0.1)
    a=p.parse_args();print(json.dumps(record(a.prior,a.image,a.mapping,a.out,a.condition,a.window,a.seconds,a.interval)))

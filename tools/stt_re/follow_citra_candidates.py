"""Follow previously observed static mismatches; never infer gameplay semantics."""
import argparse
from collections import defaultdict
import hashlib,json,math
from pathlib import Path
import time
from observe_citra_session import read_memory


def digest(data):return hashlib.sha256(data).hexdigest()


def select_candidates(analysis, protocol):
    result=[];seen=set()
    for row in analysis['static_mismatches']:
        index=row['window']
        if type(index) is not int or not 0 <= index < len(protocol['windows']):
            raise ValueError('candidate outside prior plan')
        w=protocol['windows'][index]
        if row['address']!=w['address'] or row['file_offset']!=w['file_offset'] or index in seen:
            raise ValueError('candidate does not match prior plan')
        if not 1<=w['size']<=32 or not 0<=w['address']<=2**32-w['size']:
            raise ValueError('invalid RPC range')
        seen.add(index);result.append(dict(window=index,**w))
    if not 1<=len(result)<=32:raise ValueError('one to 32 candidates required')
    return result


def literal_hits(image, segments, candidates):
    """Aligned u32 constants pointing into windows, not decoded instruction references."""
    hits=[]
    import struct
    for segment in segments:
        start=segment['file_offset'];end=start+segment['code_bytes']
        if start<0 or end>len(image):raise ValueError('segment outside static image')
        for off in range(start,end-3,4):
            value=struct.unpack_from('<I',image,off)[0]
            for c in candidates:
                if c['address']<=value<c['address']+c['size']:
                    hits.append(dict(segment=segment['name'],file_offset=off,
                        source_address=segment['address']+off-start,
                        candidate_window=c['window'],target_byte_offset=value-c['address']))
    return hits


def follow(prior,image_path,mapping_path,out,cycles=40,rate=20,seconds=40):
    if type(cycles) is not int or not 2<=cycles<=100 or not math.isfinite(rate) or not 1<=rate<=20 or not math.isfinite(seconds) or not 0<seconds<=60:
        raise ValueError('invalid bounded sampling parameters')
    prior=Path(prior);image=Path(image_path).read_bytes();mapping=json.loads(Path(mapping_path).read_bytes())
    protocol=json.loads((prior/'protocol.json').read_bytes());analysis=json.loads((prior/'analysis.json').read_bytes())
    if digest(image)!=protocol['static_image_sha256'] or digest(image)!=mapping['output_sha256']:
        raise ValueError('static image identity mismatch')
    if digest(Path(mapping_path).read_bytes())!=protocol['mapping_sha256']:
        raise ValueError('static mapping identity mismatch')
    previous_receipt=json.loads((prior/'receipt.json').read_bytes())
    if digest((prior/'protocol.json').read_bytes())!=previous_receipt['protocol_sha256'] or analysis['receipt']!=previous_receipt:
        raise ValueError('prior metadata mismatch')
    for filename,key in [('windows.bin','binary_sha256'),('reads.jsonl','reads_sha256')]:
        if digest((prior/filename).read_bytes())!=previous_receipt[key]:
            raise ValueError('prior artifact hash mismatch')
    candidates=select_candidates(analysis,protocol)
    data=next(s for s in mapping['segments'] if s['name']=='data')
    for c in candidates:
        delta=c['address']-data['address']
        if not 0<=delta<=data['code_bytes']-c['size'] or c['file_offset']!=data['file_offset']+delta:
            raise ValueError('candidate outside verified data backing')
    if cycles*(4+sum(c['size'] for c in candidates))>128*1024:
        raise ValueError('extraction budget exceeded')
    control=protocol['control'];out=Path(out);out.mkdir(parents=True,exist_ok=False)
    plan=dict(candidates=candidates,cycles=cycles,rate=rate,seconds=seconds,
        prior_analysis_sha256=digest((prior/'analysis.json').read_bytes()),
        image_sha256=digest(image),control=control,atomic=False,actions_timed=False)
    (out/'protocol.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    hits=literal_hits(image,mapping['segments'],candidates)
    (out/'literal-hits.json').write_text(json.dumps(dict(hits=hits,decoded_instructions=False),indent=2)+'\n',encoding='utf-8')
    started=time.perf_counter();deadline=started+seconds
    previous={};unique=defaultdict(set);changes=defaultdict(int);indices=defaultdict(set);counts=defaultdict(int)
    attempts=errors=written=consecutive=completed=0;reason='complete'
    with (out/'reads.jsonl').open('x',encoding='utf-8') as records,(out/'windows.bin').open('xb') as binary:
        for cycle in range(cycles):
            successful=0
            for w in [dict(window=-1,**control)]+candidates:
                begin=time.perf_counter()
                if begin>=deadline:reason='deadline';break
                attempts+=1;index=w['window']
                row=dict(cycle=cycle,window=index,address=w['address'],bytes=w['size'],start_seconds=begin-started,utc_start=time.time())
                try:
                    value=read_memory(w['address'],w['size'],timeout=min(0.25,deadline-begin))
                    row.update(sha256=digest(value),binary_offset=written,
                        matches_static=value==image[w['file_offset']:w['file_offset']+w['size']])
                    binary.write(value);written+=len(value);consecutive=0;successful+=1
                    if index==-1 and not row['matches_static']:reason='control_mismatch'
                    if index>=0:
                        delta=[] if index not in previous else [i for i,(x,y) in enumerate(zip(previous[index],value)) if x!=y]
                        row['changed_byte_indices']=delta;row['previous_successful_sample_exists']=index in previous
                        changes[index]+=bool(delta);indices[index].update(delta);counts[index]+=1;unique[index].add(row['sha256']);previous[index]=value
                except (OSError,ValueError) as exc:
                    errors+=1;consecutive+=1;row['error_type']=type(exc).__name__
                row['end_seconds']=time.perf_counter()-started;records.write(json.dumps(row)+'\n');records.flush()
                if consecutive>=4:reason='four_consecutive_errors'
                if reason!='complete':break
                time.sleep(min(max(0,1/rate-(time.perf_counter()-begin)),max(0,deadline-time.perf_counter())))
            if successful==len(candidates)+1:completed+=1
            if reason!='complete':break
    result=dict(attempts=attempts,successes=attempts-errors,errors=errors,completed_cycles=completed,
        elapsed_seconds=time.perf_counter()-started,stop_reason=reason,extracted_bytes=written,
        candidates=[dict(window=c['window'],address=c['address'],successful_samples=counts[c['window']],distinct_digests=len(unique[c['window']]),changed_samples=changes[c['window']],changed_byte_indices=sorted(indices[c['window']])) for c in candidates],
        literal_hits=len(hits),literal_hits_are_instruction_references=False,
        binary_sha256=digest((out/'windows.bin').read_bytes()),reads_sha256=digest((out/'reads.jsonl').read_bytes()),protocol_sha256=digest((out/'protocol.json').read_bytes()),memory_writes=False,actions_timed=False,semantic_identity_verified=False)
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['prior','image','mapping','out']:p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--cycles',type=int,default=40);p.add_argument('--rate',type=float,default=20);p.add_argument('--seconds',type=float,default=40)
    a=p.parse_args();print(json.dumps(follow(a.prior,a.image,a.mapping,a.out,a.cycles,a.rate,a.seconds)))

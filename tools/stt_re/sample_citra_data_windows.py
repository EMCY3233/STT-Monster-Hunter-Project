"""Sparse, bounded Citra v1 data sampling; extracted bytes are private artifacts."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import time
from observe_citra_session import read_memory


def sha(data):
    return hashlib.sha256(data).hexdigest()


def plan_windows(segment, stride=4096, size=32):
    start, length, offset = (segment[k] for k in ('address', 'code_bytes', 'file_offset'))
    if any(type(x) is not int for x in (start, length, offset, stride, size)):
        raise ValueError('integer ranges required')
    if not (0 <= start < 2**32 and 0 < length <= 4*1024*1024 and
            start + length <= 2**32 and offset >= 0 and
            4096 <= stride <= 65536 and 1 <= size <= 32):
        raise ValueError('range exceeds sparse sampling bounds')
    return [dict(address=start+i, size=min(size, length-i), file_offset=offset+i)
            for i in range(0, length, stride)]


def compare_windows(first, last):
    """Only paired successful windows; missing reads cannot imply stability."""
    result = []
    for index in sorted(first.keys() & last.keys()):
        a, b = first[index], last[index]
        if len(a) != len(b):
            raise ValueError('inconsistent paired window size')
        changed = [i for i, (x,y) in enumerate(zip(a,b)) if x != y]
        if changed:
            result.append(dict(window=index, changed_byte_indices=changed))
    return dict(paired_windows=len(first.keys() & last.keys()),
                unpaired_windows=len(first.keys() ^ last.keys()), changed_windows=result)


def plan_bss_windows(mapping, image_size, stride=4096):
    """Citra 0ff3440 loader appends page-rounded BSS after page-rounded data."""
    data=next(s for s in mapping['segments'] if s['name']=='data')
    mapped=data['mapped_bytes'];length=mapping['bss_bytes']
    if type(mapped) is not int or mapped%4096 or mapped<data['code_bytes'] or data['file_offset']+mapped!=image_size:
        raise ValueError('BSS layout does not match loader backing')
    planned=plan_windows(dict(address=data['address']+mapped,code_bytes=length,file_offset=0),stride)
    return [dict(address=w['address'],size=w['size'],file_offset=None) for w in planned]


def capture(mapping_path, image_path, out, sweeps=2, stride=4096, rate=20, seconds=60, region='data'):
    if type(sweeps) is not int or not 2 <= sweeps <= 3:
        raise ValueError('two or three sweeps required')
    if not math.isfinite(rate) or not 1 <= rate <= 20:
        raise ValueError('rate must be 1..20 requests per second')
    if not math.isfinite(seconds) or not 0 < seconds <= 60:
        raise ValueError('duration must be 0..60 seconds')
    mapping_bytes = Path(mapping_path).read_bytes()
    mapping = json.loads(mapping_bytes)
    image = Path(image_path).read_bytes()
    if sha(image) != mapping['output_sha256']:
        raise ValueError('static image hash mismatch')
    data = next(s for s in mapping['segments'] if s['name']=='data')
    text = next(s for s in mapping['segments'] if s['name']=='text')
    if region not in ('data','bss'):raise ValueError('unknown region')
    windows = plan_windows(data, stride) if region=='data' else plan_bss_windows(mapping,len(image),stride)
    if any(w['file_offset'] is not None and w['file_offset']+w['size'] > len(image) for w in windows):
        raise ValueError('static backing outside image')
    control = dict(address=text['address'], size=4, file_offset=text['file_offset'])
    if not 0 <= control['address'] <= 2**32-4 or not 0 <= control['file_offset'] <= len(image)-4:
        raise ValueError('invalid control backing')
    budget = sweeps*(sum(w['size'] for w in windows)+4)
    if budget > 128*1024:
        raise ValueError('extraction budget exceeds 128 KiB')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    protocol = dict(schema=1, protocol='Citra RPC v1 ReadMemory only',
        mapping_sha256=sha(mapping_bytes), static_image_sha256=sha(image),
        windows=windows, sweeps=sweeps, control=control, stride=stride,
        maximum_requests_per_second=rate, maximum_seconds=seconds,
        maximum_extracted_bytes=budget, atomic_snapshot=False,
        region=region,scope='sparse '+region+' only; no heap, VRAM or process scan',
        bss_loader_reference='Citra 0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/loader/ncch.cpp' if region=='bss' else None)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n',encoding='utf-8')
    started=time.monotonic(); deadline=started+seconds
    first={}; last={}; attempts=successes=errors=consecutive=0
    bytes_saved=0; completed_sweeps=0; reason='complete';latencies=[]
    with (out/'reads.jsonl').open('x',encoding='utf-8') as records, (out/'windows.bin').open('xb') as binary:
        for sweep in range(sweeps):
            current={}
            for index,w in [(-1,control)]+list(enumerate(windows)):
                if time.monotonic() >= deadline:
                    reason='deadline';break
                begun=time.monotonic();attempts+=1
                record=dict(sweep=sweep,window=index,address=w['address'],bytes=w['size'],
                            read_start_seconds=begun-started,utc_start=time.time())
                try:
                    value=read_memory(w['address'],w['size'],timeout=min(0.25,deadline-begun))
                    latency=time.monotonic()-begun;latencies.append(latency)
                    record.update(sha256=sha(value),binary_offset=bytes_saved,
                        matches_static=None if w['file_offset'] is None else value==image[w['file_offset']:w['file_offset']+w['size']])
                    binary.write(value);bytes_saved+=len(value);successes+=1;consecutive=0
                    if index==-1 and not record['matches_static']:
                        reason='control_mismatch'
                    if index>=0:current[index]=value
                except (OSError,ValueError) as exc:
                    errors+=1;consecutive+=1;record['error_type']=type(exc).__name__
                record['read_end_seconds']=time.monotonic()-started
                records.write(json.dumps(record)+'\n');records.flush()
                if reason!='complete' or consecutive>=4:
                    if consecutive>=4:reason='four_consecutive_errors'
                    break
                time.sleep(min(max(0,1/rate-(time.monotonic()-begun)),max(0,deadline-time.monotonic())))
            if sweep==0:first=current
            if sweep==sweeps-1:last=current
            if len(current)==len(windows):completed_sweeps+=1
            if reason!='complete':break
    comparison=compare_windows(first,last)
    receipt=dict(schema=1,stop_reason=reason,elapsed_seconds=time.monotonic()-started,
        region=region,requested_sweeps=sweeps,completed_sweeps=completed_sweeps,
        attempts=attempts,successes=successes,errors=errors,extracted_bytes=bytes_saved,
        windows_per_sweep=len(windows),comparison=comparison,
        mean_request_seconds=sum(latencies)/len(latencies) if latencies else None,
        max_request_seconds=max(latencies) if latencies else None,
        binary_sha256=sha((out/'windows.bin').read_bytes()),
        reads_sha256=sha((out/'reads.jsonl').read_bytes()),
        protocol_sha256=sha((out/'protocol.json').read_bytes()),
        memory_writes=False,semantic_identity_verified=False,game_actions_timed=False)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mapping',type=Path,required=True)
    p.add_argument('--image',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--sweeps',type=int,default=2)
    p.add_argument('--stride',type=int,default=4096)
    p.add_argument('--rate',type=float,default=20)
    p.add_argument('--seconds',type=float,default=60)
    p.add_argument('--region',choices=['data','bss'],default='data')
    a=p.parse_args()
    print(json.dumps(capture(a.mapping,a.image,a.out,a.sweeps,a.stride,a.rate,a.seconds,a.region)))

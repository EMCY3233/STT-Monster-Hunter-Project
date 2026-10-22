"""Read-only BSS session archive, content-addressed chunks and verified local export.

Export is sampled memory, not recovery of an original game file. No heap/VRAM.
"""
import argparse,hashlib,json,re,time
from pathlib import Path
from capture_citra_bss_block import plan
from observe_citra_session import read_memory


def sha(data):return hashlib.sha256(data).hexdigest()


def put_object(directory,data):
    if len(data)!=32:raise ValueError('exactly 32 bytes per object required')
    digest=sha(data);path=Path(directory)/(digest+'.bin')
    if path.exists():
        if path.is_symlink() or path.read_bytes()!=data:raise ValueError('existing object integrity failure')
        return digest,False
    with path.open('xb') as f:f.write(data)
    return digest,True


def assemble(directory,rows,address,size):
    if size<32 or size>8192 or size%32:raise ValueError('export size bounds')
    if len(rows)!=size//32:raise ValueError('missing or duplicate chunks')
    ordered=sorted(rows,key=lambda r:r['address']);chunks=[]
    for i,row in enumerate(ordered):
        digest=row.get('sha256','')
        if row['address']!=address+32*i or not re.fullmatch('[0-9a-f]{64}',digest):
            raise ValueError('noncontiguous export or invalid object identity')
        p=Path(directory)/(digest+'.bin')
        if p.is_symlink():raise ValueError('symlink object rejected')
        data=p.read_bytes()
        if len(data)!=32 or sha(data)!=digest:raise ValueError('object hash/length mismatch')
        chunks.append(data)
    return b''.join(chunks)


def capture(image_path,mapping_path,out,address,size=8192,sweeps=3,probes=()):
    if type(sweeps) is not int or not 1<=sweeps<=3:raise ValueError('one to three sweeps')
    image=Path(image_path).read_bytes();mb=Path(mapping_path).read_bytes();mapping=json.loads(mb)
    if sha(image)!=mapping['output_sha256']:raise ValueError('image identity mismatch')
    ranges=plan(mapping,len(image),address,size)
    if len(probes)>2 or len(set(probes))!=len(probes):raise ValueError('up to two distinct priority probes')
    for probe in probes:plan(mapping,len(image),probe,32)
    out=Path(out);out.mkdir(parents=True,exist_ok=False);objects=out/'objects';objects.mkdir()
    protocol=dict(schema=2,source='Citra RPC v1 ReadMemory',address=address,size=size,sweeps=sweeps,
        image_sha256=sha(image),mapping_sha256=sha(mb),maximum_requests_per_second=20,
        maximum_seconds=60,maximum_sampled_bytes=(size+len(ranges)//16*len(probes)*32)*sweeps,atomic_snapshot=False,
        priority_probes=list(probes),probe_every_dense_chunks=16,
        region='verified BSS only',original_game_file_recovery=False,raw_bytes_private=True)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n',encoding='utf-8')
    code=next(s for s in mapping['segments'] if s['name']=='text');expected=image[code['file_offset']:code['file_offset']+4]
    controls=[];rows=[];new=0;start=time.monotonic();last=[start-.05]
    receipt=dict(status='started',errors=0,utc_start=time.time())
    def read(a,n):
        time.sleep(max(0,.05-(time.monotonic()-last[0])))
        if time.monotonic()-start>59:raise TimeoutError('capture deadline')
        last[0]=time.monotonic();return read_memory(a,n)
    def control(sweep,phase):
        value=read(code['address'],4);ok=value==expected
        controls.append(dict(sweep=sweep,phase=phase,matches=ok,utc=time.time()))
        if not ok:raise ValueError('static code control mismatch')
    try:
        with (out/'reads.jsonl').open('x',encoding='utf-8') as index:
            for sweep in range(sweeps):
                control(sweep,'before')
                for chunk,(a,n) in enumerate(ranges):
                    requests=[('dense',a)]
                    if (chunk+1)%16==0:requests.extend(('priority',probe) for probe in probes)
                    for kind,target in requests:
                        utc=time.time();value=read(target,32);end=time.time()
                        digest,created=put_object(objects,value);new+=created
                        row=dict(kind=kind,sweep=sweep,address=target,bytes=32,utc_start=utc,utc_end=end,sha256=digest)
                        rows.append(row);index.write(json.dumps(row)+'\n');index.flush()
                control(sweep,'after')
        receipt['status']='complete'
    except BaseException as exc:
        receipt.update(status='failed',errors=1,error=str(exc));raise
    finally:
        receipt.update(utc_end=time.time(),elapsed_seconds=time.monotonic()-start,
            successful_reads=len(rows),sampled_bytes=len(rows)*32,unique_objects=new,stored_bytes=new*32,
            deduplicated_bytes=(len(rows)-new)*32,controls=controls,
            protocol_sha256=sha((out/'protocol.json').read_bytes()),
            index_sha256=sha((out/'reads.jsonl').read_bytes()) if (out/'reads.jsonl').exists() else None,
            memory_writes=False,semantic_identity_verified=False)
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt


def load_session(folder):
    folder=Path(folder);pb=(folder/'protocol.json').read_bytes();rb=(folder/'reads.jsonl').read_bytes()
    protocol=json.loads(pb);receipt=json.loads((folder/'receipt.json').read_text())
    if receipt['status']!='complete' or receipt['errors'] or not all(x['matches'] for x in receipt['controls']):
        raise ValueError('incomplete/failed session rejected')
    if sha(pb)!=receipt['protocol_sha256'] or sha(rb)!=receipt['index_sha256']:raise ValueError('manifest identity mismatch')
    rows=[json.loads(x) for x in rb.splitlines()]
    probes=protocol.get('priority_probes',[])
    expected=protocol['sweeps']*(protocol['size']//32+protocol['size']//512*len(probes))
    if len(rows)!=expected or len(rows)!=receipt['successful_reads']:
        raise ValueError('session row count mismatch')
    if len(receipt['controls'])!=protocol['sweeps']*2:raise ValueError('missing controls')
    if {(x['sweep'],x['phase']) for x in receipt['controls']}!={(i,p) for i in range(protocol['sweeps']) for p in ('before','after')}:
        raise ValueError('duplicate or missing control phases')
    unique=len({r['sha256'] for r in rows})
    if receipt['unique_objects']!=unique or receipt['stored_bytes']!=unique*32 or receipt['sampled_bytes']!=len(rows)*32 or receipt['deduplicated_bytes']!=(len(rows)-unique)*32:
        raise ValueError('archive accounting mismatch')
    groups=[]
    for sweep in range(protocol['sweeps']):
        group=[r for r in rows if r['sweep']==sweep and r.get('kind','dense')=='dense']
        groups.append(assemble(folder/'objects',group,protocol['address'],protocol['size']))
    for probe in probes:
        selected=[r for r in rows if r.get('kind')=='priority' and r['address']==probe]
        if len(selected)!=protocol['sweeps']*(protocol['size']//512):raise ValueError('priority probe count mismatch')
        for row in selected:assemble(folder/'objects',[row],probe,32)
    return protocol,receipt,rows,groups


def analyze(folder):
    protocol,receipt,rows,groups=load_session(folder);changes=[]
    for i in range(0,protocol['size'],4):
        values=[b[i:i+4] for b in groups]
        if len(set(values))>1:changes.append(dict(address=protocol['address']+i,distinct_patterns=len(set(values))))
    from record_citra_target import field_stats
    priority=[]
    for probe in protocol.get('priority_probes',[]):
        selected=[r for r in rows if r.get('kind')=='priority' and r['address']==probe]
        samples=[assemble(Path(folder)/'objects',[row],probe,32) for row in selected]
        priority.append(dict(address=probe,stats=field_stats(samples),
            first_utc=selected[0]['utc_start'],last_utc=selected[-1]['utc_end']))
    return dict(sweeps=protocol['sweeps'],sampled_bytes=receipt['sampled_bytes'],stored_bytes=receipt['stored_bytes'],
        deduplicated_bytes=receipt['deduplicated_bytes'],changed_aligned_words=changes,
        exported_sweep_hashes=[sha(x) for x in groups],atomic_snapshot=False,
        priority_probe_summaries=priority,semantic_identity_verified=False,original_game_files_identified=0)


def export(folder,sweep,out):
    protocol,receipt,rows,groups=load_session(folder)
    if type(sweep) is not int or not 0<=sweep<len(groups):raise ValueError('invalid sweep')
    data=groups[sweep]
    with Path(out).open('xb') as f:f.write(data)
    return dict(bytes=len(data),sha256=sha(data),sweep=sweep,address=protocol['address'],
                content='non-atomic sampled BSS memory; not an original game file')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('capture')
    for name in ('image','mapping','out'):c.add_argument('--'+name,type=Path,required=True)
    c.add_argument('--address',type=lambda x:int(x,0),required=True);c.add_argument('--size',type=int,default=8192);c.add_argument('--sweeps',type=int,default=3)
    c.add_argument('--probes',nargs='*',type=lambda x:int(x,0),default=[])
    a=sub.add_parser('analyze');a.add_argument('folder',type=Path)
    e=sub.add_parser('export');e.add_argument('folder',type=Path);e.add_argument('--sweep',type=int,required=True);e.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.command=='capture':result=capture(a.image,a.mapping,a.out,a.address,a.size,a.sweeps,a.probes)
    elif a.command=='analyze':result=analyze(a.folder)
    else:result=export(a.folder,a.sweep,a.out)
    print(json.dumps(result))

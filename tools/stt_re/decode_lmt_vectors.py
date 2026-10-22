"""Independent limited LMT67 LE32 reader. Vector values stay local; public output is counts only.

Format references: RevilLib animation.inl, bone_track.inl, internal.hpp and codecs.hpp.
Does not decrypt anything or decode quaternion tracks, events or skeleton bindings.
"""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import struct

def finite(values):
    if not all(math.isfinite(v) for v in values):
        raise ValueError('non-finite vector data')

def vector_keys(data,codec,offset,length,extremes):
    stride={4:8,5:4}.get(codec)
    if stride is None or not length or length%stride or not 0<offset<=len(data)-length:
        raise ValueError('unsupported codec or invalid vector buffer')
    if not 0<extremes<=len(data)-32:
        raise ValueError('quantized vector bounds missing/outside file')
    bounds=struct.unpack_from('<8f',data,extremes)
    finite(bounds)
    scale,base=bounds[:3],bounds[4:7]
    frame=0
    keys=[]
    for at in range(offset,offset+length,stride):
        x,y,z,delta=struct.unpack_from('<4H' if codec==4 else '<4B',data,at)
        divisor=65535 if codec==4 else 255
        values=[base[i]+scale[i]*v/divisor for i,v in enumerate((x,y,z))]
        finite(values)
        keys.append({'frame_index_without_reference':frame,'xyz':values})
        frame+=delta
    return keys

def inspect(data):
    if len(data)<8 or data[:4]!=b'LMT\0' or struct.unpack_from('<H',data,4)[0]!=67:
        raise ValueError('only LMT67 supported')
    count=struct.unpack_from('<H',data,6)[0]
    first=(8+count*4+15)&~15
    if first>len(data):
        raise ValueError('lookup table outside file')
    records=[]
    for slot in range(count):
        at=struct.unpack_from('<I',data,8+slot*4)[0]
        if not at:
            continue
        if not first<=at<=len(data)-64:
            raise ValueError('animation header outside file')
        ptr,n,frames,loop=struct.unpack_from('<IIIi',data,at)
        if n>10000 or not first<=ptr<=len(data)-n*36:
            raise ValueError('track table outside file')
        for i in range(n):
            start=ptr+i*36
            codec,kind,btype,bone,weight,size,buffer=struct.unpack_from('<4BfII',data,start)
            ref=struct.unpack_from('<4f',data,start+16)
            extremes=struct.unpack_from('<I',data,start+32)[0]
            finite((weight,*ref))
            if size and not first<=buffer<=len(data)-size:
                raise ValueError('track payload outside file')
            if extremes and not first<=extremes<=len(data)-32:
                raise ValueError('extremes outside file')
            row=dict(slot=slot,track=i,codec=codec,track_type=kind,bone_id=bone,
                     clip_frames_declared=frames,payload_bytes=size,status='codec_not_decoded')
            if kind in (1,2,4):
                row['reference_xyz']=list(ref[:3])
                if size==0:
                    row.update(status='reference_vector_read',keys=[])
                elif codec in (4,5):
                    row.update(status='vector_keys_decoded',keys=vector_keys(data,codec,buffer,size,extremes))
            records.append(row)
    return records

def summarize(records):
    return dict(tracks=len(records),status=dict(Counter(r['status'] for r in records)),
                codecs=dict(Counter(str(r['codec']) for r in records)),
                vector_keys=sum(len(r.get('keys',[])) for r in records),
                dynamic_vector_tracks=sum(len(r.get('keys',[]))>1 and any(k['xyz']!=r['keys'][0]['xyz'] for k in r['keys'][1:]) for r in records),
                skeleton_binding=False,quaternion_decoding=False,fps=None,gameplay_events=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--samples',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    out=a.out.resolve()
    if any((q/'.git').exists() for q in (out,*out.parents)) or out.is_relative_to(a.samples.resolve()):
        raise ValueError('local decoded values must stay outside Git and inputs')
    out.mkdir(parents=True,exist_ok=False)
    summaries=[]
    for source in sorted(a.samples.glob('*.lmt')):
        data=source.read_bytes()
        sha=hashlib.sha256(data).hexdigest()
        records=inspect(data)
        if hashlib.sha256(source.read_bytes()).hexdigest()!=sha:
            raise ValueError('source changed')
        result=dict(name=source.name,sha256=sha,bytes=len(data),**summarize(records))
        summaries.append(result)
        with (out/(source.stem+'.vectors.json')).open('x',encoding='utf-8') as f:
            f.write(json.dumps(dict(source_sha256=sha,records=records),indent=2)+'\n')
    with (out/'summary.json').open('x',encoding='utf-8') as f:
        f.write(json.dumps(summaries,indent=2)+'\n')
    print(json.dumps(summaries))

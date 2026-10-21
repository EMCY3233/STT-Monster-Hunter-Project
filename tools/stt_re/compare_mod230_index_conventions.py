"""Compare two documented MOD230 index read lengths on one unchanged sample."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def window(total,offset,count,extra_bytes=0):
    size=count*2+extra_bytes
    return dict(offset=offset,bytes=size,u16_count=size//2,end=offset+size,in_file=0<=offset<=offset+size<=total)

def inspect(data):
    if not 64<=len(data)<=1024*1024 or data[:6]!=b'MOD\0\xe6\0': raise ValueError('expected bounded LE MOD230')
    common=struct.unpack_from('<4s4H13I',data)
    if common[3]!=1: raise ValueError('single mesh only')
    mesh_at=common[15]
    if mesh_at<64 or mesh_at+48>len(data): raise ValueError('mesh header bounds')
    mesh=struct.unpack_from('<HHIHBB9I',data,mesh_at)
    at=common[17]+mesh[9]*2
    declared=window(len(data),at,mesh[10])
    plus_one=window(len(data),at,mesh[10],2)
    global_range=window(len(data),common[17],common[6])
    result=dict(source_bytes=len(data),version=common[1],mesh_count=common[3],mesh_offset=mesh_at,global_index_count=common[6],mesh_index_count=mesh[10],revil_global_read=global_range,revil_mesh_read=declared,mhff_mesh_read_plus_two_bytes=plus_one,mesh_tail_word_at_relative_40=mesh[13],tail_semantics='RevilLib splits into min/max u16; MH4U reader leaves this word unused',geometry_validated=False)
    for label,span in (('mesh_declared',declared),('mesh_plus_one',plus_one)):
        if span['in_file']:
            values=struct.unpack_from('<'+str(span['u16_count'])+'H',data,at)
            valid=[x for x in values if x!=65535]
            result[label+'_checks']=dict(indices_in_vertex_range=all(0<=x-mesh[6]<mesh[1] for x in valid),restart_count=len(values)-len(valid),consecutive_triplets=max(0,len(values)-2),distinct_index_triplets=sum(len(set(values[i-2:i+1]))==3 for i in range(2,len(values))),not_a_geometric_area_or_winding_check=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.input.stat().st_size>1024*1024: raise ValueError('input budget')
    data=a.input.read_bytes(); digest=hashlib.sha256(data).hexdigest()
    if digest!=a.expected_sha256: raise ValueError('hash mismatch')
    report=inspect(data); report.update(source_sha256=digest,source_unchanged=hashlib.sha256(a.input.read_bytes()).hexdigest()==digest)
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

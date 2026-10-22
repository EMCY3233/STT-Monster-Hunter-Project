"""Bounded MRL32 structural reader; descriptor semantics remain hypotheses.

Reference: https://raw.githubusercontent.com/wiki/svanheulen/mhff/MH4U-rMaterial-Format.md
Layouts independently checked on local MHXX samples. No game code execution.
"""
import struct

def parse(data):
    def span(at,size):
        if at < 0 or size < 0 or at+size > len(data):
            raise ValueError('MRL span outside file')
    if not 28 <= len(data) <= 32*1024*1024 or data[:4] != b'MRL\0':
        raise ValueError('MRL signature/size')
    _,version,nmat,nres,unknown,res_at,mat_at=struct.unpack_from('<7I',data)
    if version!=32 or max(nmat,nres)>4096:
        raise ValueError('MRL version/count')
    span(res_at,nres*76);span(mat_at,nmat*60)
    if res_at<28 or res_at+nres*76!=mat_at:
        raise ValueError('unsupported resource/material table layout')
    resources=[]
    for i in range(nres):
        at=res_at+i*76
        typ=struct.unpack_from('<I',data,at)[0]
        r=dict(index_1based=i+1,offset=at,type_hex=f'{typ:08x}')
        if typ:
            raw=data[at+12:at+76]
            if b'\0' not in raw:raise ValueError('resource path unterminated')
            r['path']=raw.split(b'\0',1)[0].decode('ascii')
        resources.append(r)
    materials=[]
    active=[]
    table_end=mat_at+nmat*60
    for i in range(nmat):
        at=mat_at+i*60
        w=struct.unpack_from('<15I',data,at)
        size=w[2];count=w[6]&4095;ptr=w[13]
        span(ptr,size)
        if ptr<table_end or count*12>size:raise ValueError('descriptor block range')
        active.append((ptr,ptr+size))
        descriptors=[]
        for k in range(count):
            pos=ptr+k*12;tag,value,namehash=struct.unpack_from('<3I',data,pos)
            kind=tag&15
            item=dict(offset=pos,tag=f'{tag:08x}',kind_low_nibble=kind,
                      value=value,parameter_hash=f'{namehash:08x}')
            if kind==3:
                if value>nres:raise ValueError('candidate resource index out of range')
                item['candidate_resource']=resources[value-1] if value else None
                item['semantics']='hypothesis: one-based resource index, zero null'
            descriptors.append(item)
        materials.append(dict(index=i,offset=at,name_hash=f'{w[1]:08x}',
            block_offset=ptr,block_bytes=size,descriptors=descriptors))
    active.sort()
    if any(a[1]>b[0] for a,b in zip(active,active[1:])):
        raise ValueError('overlapping descriptor blocks')
    return dict(version=version,resources=resources,materials=materials,
                semantic_slot_names_verified=False)

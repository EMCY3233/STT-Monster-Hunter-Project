"""One MOD230/XE5 skeleton, metadata only; no geometry, skinning or animation.

Layouts documented in RevilLib e17f9718 bones.hpp/traits.hpp/serialize.cpp;
Spike e83f3855 vector/matrix types establish 24-byte bones and 64-byte matrices.
This independently written probe runs no external library code.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct


def sha_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def forest(parents):
    count=len(parents)
    if any(p!=255 and not 0<=p<count for p in parents):raise ValueError('parent outside bone slots')
    depths=[]
    for start in range(count):
        seen=set();cur=start;depth=0
        while parents[cur]!=255:
            if cur in seen:raise ValueError('parent cycle')
            seen.add(cur);cur=parents[cur];depth+=1
        depths.append(depth)
    roots=[i for i,p in enumerate(parents) if p==255]
    if not roots:raise ValueError('no root')
    return dict(parent_reference_domain='bone record slots, as used by primary converter',
                parent_indices_in_range=True,root_count=len(roots),root_slots=roots,
                nonroot_edges=count-len(roots),acyclic=True,max_depth=max(depths,default=0))


def inspect(read_at,total):
    if not 64<=total<=1024*1024:raise ValueError('file size budget')
    ranges=[];used=0
    def read(at,n,label):
        nonlocal used
        if at<0 or n<0 or at+n>total or used+n>65536:raise ValueError('skeleton range/budget')
        data=read_at(at,n)
        if len(data)!=n:raise ValueError('short skeleton read')
        used+=n
        ranges.append(dict(label=label,offset=at,bytes=n,sha256=hashlib.sha256(data).hexdigest()))
        return data
    h=read(0,64,'extended header')
    if h[:4]!=b'MOD\0':raise ValueError('MOD signature')
    version,bones,meshes,materials=struct.unpack_from('<4H',h,4)
    if version!=230 or not 0<bones<=255:raise ValueError('requires MOD230 with 1..255 bones')
    vb_size,textures,groups,skins,bones_at,groups_at,materials_at,meshes_at,vb_at,indices_at=struct.unpack_from('<10I',h,24)
    if skins>256 or bones_at<64:raise ValueError('skeleton counts/start')
    sizes=[('bones',bones*24),('ref_poses',bones*64),('transforms',bones*64),('remaps',256),('skin_remaps',skins*28)]
    end=bones_at+sum(n for _,n in sizes)
    if end>total:raise ValueError('skeleton tables exceed file')
    following=[p for p in [groups_at,materials_at,meshes_at,vb_at,indices_at] if p]
    if any(p<end or p>total for p in following):raise ValueError('skeleton overlaps another declared region')
    blocks={};at=bones_at
    for label,n in sizes:
        blocks[label]=read(at,n,label);at+=n
    records=blocks['bones'];parents=[];ids=[];finite_bone=0
    for i in range(bones):
        at=i*24;ids.append(records[at]);parents.append(records[at+1])
        finite_bone+=all(math.isfinite(v) for v in struct.unpack_from('<5f',records,at+4))
    hierarchy=forest(parents)
    if finite_bone!=bones:raise ValueError('nonfinite bone scalar/position')
    matrices={}
    for label in ['ref_poses','transforms']:
        values=struct.unpack('<'+str(bones*16)+'f',blocks[label])
        if not all(math.isfinite(v) for v in values):raise ValueError('nonfinite matrix')
        matrices[label]=dict(count=bones,float_count=bones*16,all_finite=True)
    skin_counts=[struct.unpack_from('<I',blocks['skin_remaps'],i*28)[0] for i in range(skins)]
    if any(n>24 for n in skin_counts):raise ValueError('skin remap count exceeds fixed capacity')
    return dict(version=version,bone_count=bones,bone_record_stride=24,matrix_stride=64,
                header_counts=dict(meshes=meshes,materials=materials,groups=groups,skins=skins),
                ranges=ranges,skeleton_table_bytes=end-bones_at,parsed_read_bytes=used,
                skeleton_end=end,next_declared_region=min(following,default=None),
                tables_in_file_nonoverlapping=True,hierarchy=hierarchy,
                bone_records_all_finite=True,index_field_unique_count=len(set(ids)),
                index_field_duplicate_records=bones-len(set(ids)),index_equals_slot=all(v==i for i,v in enumerate(ids)),
                index_field_used_for_parent_resolution=False,matrices=matrices,
                skin_remap_counts=skin_counts,skin_remap_indices_interpreted=False,
                remaps_semantics_verified=False,matrices_exported=False,
                coordinate_system_verified=False,matrix_inverses_verified=False,
                functional_rig_verified=False,skinning_performed=False,lmt_association=False,
                geometry_parsed_or_validated=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();before=sha_file(a.input)
    if before!=a.expected_sha256:raise ValueError('object hash mismatch')
    with a.input.open('rb') as f:
        def read_at(at,n):f.seek(at);return f.read(n)
        r=inspect(read_at,a.input.stat().st_size)
    after=sha_file(a.input)
    if before!=after:raise ValueError('source changed')
    r.update(source_bytes=a.input.stat().st_size,source_sha256_before=before,
             source_sha256_after=after,source_unchanged=True,full_file_hash_passes=2)
    with a.out.open('x',encoding='utf-8') as f:f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))

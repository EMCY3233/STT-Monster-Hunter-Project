"""Metadata-only bounded MOD230/XE5-layout probe of one local sample.

Field references: RevilLib header.hpp, mesh.hpp, common.cpp at e17f9718.
No RevilLib code is imported/executed, no geometry arrays are exported.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

LIMIT=1024*1024

def bounded(total,at,size): return at>=0 and size>=0 and at+size<=total

def inspect(data):
    if not 64<=len(data)<=LIMIT or data[:4]!=b'MOD\0': raise ValueError('invalid MOD size/signature')
    version,bones,meshes,materials,vertices,indices,edges=struct.unpack_from('<4H3I',data,4)
    if version!=230 or max(bones,meshes,materials,vertices,indices)>100000: raise ValueError('unsupported version/count budget')
    vb_size,textures,groups,skins,bones_at,groups_at,materials_at,meshes_at,vb_at,indices_at=struct.unpack_from('<10I',data,24)
    tables={name:dict(offset=at,bytes=size,in_bounds=bounded(len(data),at,size)) for name,at,size in (('header',0,64),('groups',groups_at,groups*32),('materials',materials_at,materials*128),('meshes',meshes_at,meshes*48),('vertex_buffer',vb_at,vb_size),('global_index_buffer_declared',indices_at,indices*2))}
    if any(not tables[k]['in_bounds'] for k in ('groups','materials','meshes','vertex_buffer')): raise ValueError('structural table outside file')
    active=sorted((v['offset'],v['offset']+v['bytes']) for k,v in tables.items() if v['bytes'] and k!='global_index_buffer_declared')
    if any(a[1]>b[0] for a,b in zip(active,active[1:])): raise ValueError('structural tables overlap')
    results=[]
    for i in range(meshes):
        at=meshes_at+i*48
        draw,nv,d0,d1,start,stream,fmt,istart,ni,value_off,skin_begin,envelopes,mesh_id,vmin,vmax,boundary=struct.unpack_from('<HH8IBBHHHI',data,at)
        stride=(d1>>16)&255; primitive=(d1>>24)&63; weights=(d1>>3)&31
        vertex_offset=vb_at+(start+value_off)*stride+stream
        vertex_end=vertex_offset+nv*stride
        v_ok=stride>0 and vb_at<=vertex_offset<=vertex_end<=vb_at+vb_size
        index_offset=indices_at+istart*2; i_ok=bounded(len(data),index_offset,ni*2)
        r=dict(mesh=i,table_offset=at,vertices=nv,indices=ni,stride=stride,vertex_format=f'0x{fmt:08X}',primitive_code=primitive,weight_count_field=weights,material_index=(d0>>12)&4095,group_index=d0&4095,vertex_span=dict(offset=vertex_offset,bytes=nv*stride,in_buffer=v_ok),index_span=dict(offset=index_offset,bytes=ni*2,in_file=i_ok),declared_min_vertex=vmin,declared_max_vertex=vmax,skin_bone_begin=skin_begin,envelopes=envelopes)
        r.update(material_index_in_range=r['material_index']<materials,group_index_in_range=r['group_index']<groups)
        if v_ok and fmt==0x59dc400b and stride==28:
            finite_positions=finite_uv=0
            for vertex in range(nv):
                p=vertex_offset+vertex*stride
                finite_positions+=all(math.isfinite(v) for v in struct.unpack_from('<3f',data,p))
                finite_uv+=all(math.isfinite(v) for v in struct.unpack_from('<2f',data,p+16))
            r['attributes']=dict(layout='f32x3 position @0, snorm8x4 normal @12, f32x2 UV @16, snorm8x4 tangent @24',stride_matches_layout=True,finite_position_records=finite_positions,finite_uv_records=finite_uv,bone_index_attribute=False,bone_weight_attribute=False,coordinate_system_verified=False)
        if i_ok:
            raw=struct.unpack_from('<'+str(ni)+'H',data,index_offset)
            usable=[v for v in raw if v!=65535]
            local=[v-start for v in usable]
            r['index_values']=dict(restarts=ni-len(usable),minimum=min(usable,default=None),maximum=max(usable,default=None),all_after_vertex_start_in_range=all(0<=v<nv for v in local),matches_declared_mesh_minmax=bool(usable) and min(usable)==vmin and max(usable)==vmax)
            if primitive==4 and len(usable)==ni:
                triplets=[raw[n-2:n+1] for n in range(2,ni)]
                r['strip_triplets']=dict(total=len(triplets),distinct_index_triplets=sum(len(set(t))==3 for t in triplets),duplicate_index_triplets=sum(len(set(t))<3 for t in triplets),geometric_area_and_winding_verified=False)
        results.append(r)
    return dict(version=version,declared=dict(bones=bones,meshes=meshes,materials=materials,vertices=vertices,indices=indices,edges=edges,groups=groups,skins=skins,textures=textures),tables=tables,structural_table_ranges_nonoverlapping=True,available_index_u16_from_pointer=max(0,(len(data)-indices_at)//2),global_index_shortfall_bytes=max(0,indices_at+indices*2-len(data)),meshes=results,geometry_validated=False,skeleton_validated=False,unparsed_regions_remain=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.input.stat().st_size>LIMIT: raise ValueError('input budget')
    data=a.input.read_bytes(); digest=hashlib.sha256(data).hexdigest()
    if digest!=a.expected_sha256: raise ValueError('source hash mismatch')
    report=inspect(data)
    report.update(source_sha256=digest,source_bytes=len(data),source_unchanged=hashlib.sha256(a.input.read_bytes()).hexdigest()==digest)
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

"""Static unskinned MOD230, format 59DC400B/28, triangle-strip -> OBJ.

Coordinates/UVs preserved; no skeleton, material association or animation conversion.
"""
import argparse,hashlib,json,math,struct
from pathlib import Path
from inspect_mod230_mesh import inspect
from extract_arc import private_destination


def strip_triangles(indices,count):
    result=[];run=[]
    for value in indices:
        if value==65535:run=[];continue
        if not 0<=value<count:raise ValueError('index outside mesh')
        run.append(value)
        if len(run)>=3:
            a,b,c=run[-3:]
            if len(run)%2==0:a,b=b,a
            if len({a,b,c})==3:result.append((a,b,c))
    return result


def convert(data):
    info=inspect(data)
    if info['declared']['bones']!=0:raise ValueError('only unskinned static models supported')
    lines=['# MOD230 static geometry; native coordinates/UVs; no material association'];summary=[];base=1
    for mesh in info['meshes']:
        if mesh['vertex_format']!='0x59DC400B' or mesh['stride']!=28 or mesh['primitive_code']!=4 or mesh['weight_count_field'] or not mesh['vertex_span']['in_buffer'] or not mesh['index_span']['in_file']:
            raise ValueError('unsupported vertex layout, skinning or primitive')
        vertices=[];uv=[];normals=[]
        for i in range(mesh['vertices']):
            at=mesh['vertex_span']['offset']+28*i
            p=struct.unpack_from('<3f',data,at);t=struct.unpack_from('<2f',data,at+16)
            n=tuple(max(-1,x/127) for x in struct.unpack_from('<3b',data,at+12))
            if not all(math.isfinite(x) for x in (*p,*t)):raise ValueError('nonfinite attributes')
            vertices.append(p);uv.append(t);normals.append(n)
        start=struct.unpack_from('<I',data,mesh['table_offset']+12)[0]
        raw=struct.unpack_from('<'+'H'*mesh['indices'],data,mesh['index_span']['offset'])
        local=[x-start if x!=65535 else 65535 for x in raw]
        triangles=strip_triangles(local,len(vertices));faces=[];zero=0
        for a,b,c in triangles:
            p,q,r=vertices[a],vertices[b],vertices[c]
            u=[q[i]-p[i] for i in range(3)];v=[r[i]-p[i] for i in range(3)]
            cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            if all(x==0 for x in cross):zero+=1
            else:faces.append((a,b,c))
        lines.append(f'o mesh_{mesh["mesh"]}')
        lines.extend('v '+' '.join(format(x,'.9g') for x in p) for p in vertices)
        lines.extend('vt '+' '.join(format(x,'.9g') for x in p) for p in uv)
        lines.extend('vn '+' '.join(format(x,'.9g') for x in p) for p in normals)
        lines.extend('f '+' '.join(f'{i+base}/{i+base}/{i+base}' for i in tri) for tri in faces)
        summary.append(dict(mesh=mesh['mesh'],vertices=len(vertices),triangles=len(faces),zero_area_removed=zero,
            bbox_min=[min(p[i] for p in vertices) for i in range(3)],bbox_max=[max(p[i] for p in vertices) for i in range(3)]))
        base+=len(vertices)
    return ('\n'.join(lines)+'\n').encode(),dict(meshes=summary,global_index_shortfall_bytes=info['global_index_shortfall_bytes'],
        index_policy='mesh-declared spans only; no invented bytes; native winding of standard strip',
        coordinate_system_verified=False,materials_converted=False,skeleton_converted=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--expect-sha256',required=True)
    a=p.parse_args();data=a.source.read_bytes();digest=hashlib.sha256(data).hexdigest()
    if digest!=a.expect_sha256:raise ValueError('source hash mismatch')
    obj,report=convert(data);out=private_destination(a.out);out.mkdir(parents=True)
    (out/'model.obj').write_bytes(obj)
    report.update(source_sha256=digest,obj_sha256=hashlib.sha256(obj).hexdigest(),source_unchanged=hashlib.sha256(a.source.read_bytes()).hexdigest()==digest)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))

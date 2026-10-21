"""Offline inspection and explicitly approximate CC0 OBJ adaptation; no asset code execution."""
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import struct
import sys
import zipfile

ROOT=Path(os.environ.get('STT_MODEL_INPUT_DIR',Path.cwd()))
PROJECT=Path(os.environ.get('STT_PROJECT_ROOT',Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(PROJECT/'asset-lab'))
from stt_asset_lab import bridge,model

def require(ok,message):
    if not ok: raise ValueError(message)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def sub(a,b): return [a[i]-b[i] for i in range(3)]
def cross(a,b): return [a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def normal(vertices,tri): return cross(sub(vertices[tri[1]],vertices[tri[0]]),sub(vertices[tri[2]],vertices[tri[0]]))

def obj(raw):
    require(len(raw)<=2_097_152,'OBJ byte budget')
    vertices=[];faces=[]
    for line in raw.decode('utf-8').splitlines():
        fields=line.split('#',1)[0].split()
        if not fields: continue
        if fields[0]=='v':
            require(len(fields)==4 and len(vertices)<8192,'position shape/budget')
            p=list(map(float,fields[1:]));require(all(math.isfinite(x) and abs(x)<=10000 for x in p),'finite position bounds')
            vertices.append(p)
        elif fields[0]=='f':
            require(4<=len(fields)<=5,'only triangles and quads in this adapter')
            ids=[]
            for field in fields[1:]:
                i=int(field.split('/')[0]);require(i!=0,'zero OBJ index')
                i=i-1 if i>0 else len(vertices)+i
                require(0<=i<len(vertices),'OBJ index outside preceding positions');ids.append(i)
            require(len(set(ids))==len(ids),'repeated polygon index')
            if len(ids)==4:
                ns=[cross(sub(vertices[ids[(i+1)%4]],vertices[ids[i]]),sub(vertices[ids[(i+2)%4]],vertices[ids[(i+1)%4]])) for i in range(4)]
                require(all(dot(ns[0],n)>0 for n in ns),'quad must be convex with consistent winding')
            for i in range(1,len(ids)-1):
                tri=[ids[0],ids[i],ids[i+1]]
                require(dot(normal(vertices,tri),normal(vertices,tri))>1e-20,'degenerate triangle')
                faces.append(tri)
            require(len(faces)<=16384,'triangle budget')
        else:
            require(fields[0] in ['o','g','s','mtllib','usemtl','vn','vt'],'unsupported OBJ directive')
    require(vertices and faces,'empty mesh')
    return vertices,faces

def cluster(vertices,faces,grid):
    lo=[min(p[i] for p in vertices) for i in range(3)];hi=[max(p[i] for p in vertices) for i in range(3)]
    groups={};keys=[]
    for p in vertices:
        key=tuple(round((p[i]-lo[i])/(hi[i]-lo[i])*grid[i]) if hi[i]>lo[i] else 0 for i in range(3))
        keys.append(key);groups.setdefault(key,[]).append(p)
    lookup={key:i for i,key in enumerate(sorted(groups))}
    out=[[sum(p[i] for p in groups[key])/len(groups[key]) for i in range(3)] for key in sorted(groups)]
    mapping=[lookup[key] for key in keys];triangles=[];seen=set();collapsed=0;duplicates=0
    for tri in faces:
        ids=[mapping[i] for i in tri]
        if len(set(ids))<3: collapsed+=1;continue
        n=normal(out,ids)
        if dot(n,n)<1e-20: collapsed+=1;continue
        require(dot(n,normal(vertices,tri))>0,'cluster would flip a retained face')
        key=tuple(sorted(ids))
        if key in seen: duplicates+=1;continue
        seen.add(key);triangles.append(ids)
    error=max(math.sqrt(dot(sub(p,out[mapping[i]]),sub(p,out[mapping[i]]))) for i,p in enumerate(vertices))
    return out,triangles,dict(grid=grid,collapsed_triangles=collapsed,duplicate_triangles=duplicates,max_source_vertex_displacement=error)

def glb(raw):
    require(len(raw)>=20 and raw[:4]==b'glTF','GLB header')
    _,version,size=struct.unpack_from('<4sII',raw)
    require(version==2 and size==len(raw),'GLB version/length')
    pos=12;chunks=[]
    while pos<len(raw):
        require(pos+8<=len(raw),'chunk header')
        n,kind=struct.unpack_from('<II',raw,pos);pos+=8
        require(pos+n<=len(raw),'chunk range');chunks.append((kind,raw[pos:pos+n]));pos+=n
    require(chunks[0][0]==0x4e4f534a,'JSON first')
    d=json.loads(chunks[0][1]);binary=next(v for k,v in chunks if k==0x004e4942)
    counts=[]
    for mesh in d['meshes']:
        for primitive in mesh['primitives']:
            require(primitive.get('mode',4)==4,'triangle mode')
            a=d['accessors'][primitive['attributes']['POSITION']];indices=d['accessors'][primitive['indices']]
            require(indices['count']%3==0,'triangle count')
            view=d['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0);stride=view.get('byteStride',12)
            require(a['type']=='VEC3' and a['componentType']==5126 and stride>=12 and offset+(a['count']-1)*stride+12<=len(binary),'position accessor bounds')
            points=[struct.unpack_from('<3f',binary,offset+i*stride) for i in range(a['count'])]
            require(all(math.isfinite(x) for p in points for x in p),'finite GLB positions')
            counts.append(dict(name=mesh['name'],position_entries=a['count'],triangles=indices['count']//3,
                               distinct_positions=len(set(points))))
    return dict(bytes=len(raw),sha256=sha(raw),meshes=counts,skin_joint_counts=[len(s['joints']) for s in d.get('skins',[])],
                clips=[dict(name=a.get('name'),channels=len(a['channels']),duration=max(d['accessors'][s['input']]['max'][0] for s in a['samplers'])) for a in d.get('animations',[])],
                limits='Structural inspection only; no animation evaluation, skinning, or Vita import')

def preview(meshes,path):
    from PIL import Image,ImageDraw
    image=Image.new('RGB',(900,600),'#14212c');draw=ImageDraw.Draw(image)
    for panel,(name,vertices,triangles) in enumerate(meshes):
        transformed=[]
        for x,y,z in vertices:
            transformed.append((.94*x+.342*z, y, -.342*x+.94*z))
        order=sorted(triangles,key=lambda t:sum(transformed[i][2] for i in t)/3)
        for tri in order:
            pts=[(panel*450+225+transformed[i][0]*330,550-transformed[i][1]*330) for i in tri]
            n=normal(transformed,tri);length=math.sqrt(dot(n,n))
            shade=int(110+110*abs(n[2])/length) if length else 110
            draw.polygon(pts,fill=(shade,shade,min(255,shade+12)),outline=(55,75,88))
        draw.text((panel*450+16,16),name,fill='white')
    image.save(path)

def main():
    out=ROOT/'prepared';out.mkdir(exist_ok=True)
    kz=zipfile.ZipFile(ROOT/'kenney_mini-characters.zip');wz=zipfile.ZipFile(ROOT/'quaternius-medieval-weapons.zip')
    # Read known members only. No extractall, paths, scripts or Blend execution.
    (out/'KENNEY-LICENSE.txt').write_bytes(kz.read('License.txt'))
    character=glb(kz.read('Models/GLB format/character-male-a.glb'))
    raw=wz.read('OBJ/Sword.obj');vertices,faces=obj(raw)
    lo=min(p[1] for p in vertices);height=max(p[1] for p in vertices)-lo
    scale=1.4/height
    normalized=[[p[0]*scale,(p[1]-lo)*scale,p[2]*scale] for p in vertices]
    candidates=[]
    for grid in itertools.product([6,8,10,12,16],[12,16,20,24,32],[2,3,4]):
        try: v,t,metrics=cluster(normalized,faces,grid)
        except ValueError: continue
        if 3<=len(v)<=256 and 1<=len(t)<=512:
            candidates.append((metrics['max_source_vertex_displacement'],v,t,metrics))
    require(candidates,'no safe cluster fits; no implicit limit increase')
    _,v,t,metrics=min(candidates,key=lambda a:(a[0],-len(a[2])))
    asset=dict(format='STT Asset',version=1,name='Quaternius Sword CC0 clustered study',bones=[dict(name='root',parent=-1,offset=[0,0,0])],
               vertices=[dict(position=p,bone=0) for p in v],triangles=t,clips=[dict(name='Static',duration=1/60,tracks=[])])
    model.export(asset,out/'quaternius-sword-study.stt.json')
    pose=bridge.runtime_dumps(bridge.bake(asset));(out/'quaternius-sword-study.pose.json').write_bytes(pose)
    preview([('Original sword - normalized',normalized,faces),('Clustered study - not game-tested',v,t)],out/'sword-comparison.png')
    report=dict(date='2026-10-22',kenney_pack_sha256=sha((ROOT/'kenney_mini-characters.zip').read_bytes()),
        weapons_pack_sha256=sha((ROOT/'quaternius-medieval-weapons.zip').read_bytes()),character=character,
        sword=dict(source='OBJ/Sword.obj',source_sha256=sha(raw),source_vertices=len(vertices),source_triangles=len(faces),
            output_vertices=len(v),output_triangles=len(t),scale_to_height_m=1.4,pivot='minimum source Y, not verified hand grip',
            conversion='Identity axes, uniform scale, no textures/materials; centroid vertex clustering, collapsed faces removed',
            pose_bytes=len(pose),pose_sha256=sha(pose),**metrics),
        license_evidence=dict(kenney='License.txt inside archive: CC0',weapons='Official author page states CC0; archive has no license file',
            urls=['https://kenney.nl/assets/mini-characters','https://quaternius.itch.io/lowpoly-medieval-weapons']),
        validation='PC Python bridge roundtrip; comparison preview inspected locally; no C renderer/VPK/hardware/FTP')
    (out/'inspection.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(character=character,sword=report['sword']),indent=2))

if __name__=='__main__':main()

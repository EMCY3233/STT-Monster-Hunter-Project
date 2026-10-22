"""Derive narrowly scoped read-only probes from MH4U EUR cheat references.

Never interprets or executes cheats. A source label is not field verification.
"""
import argparse,hashlib,json,re,struct,time
from pathlib import Path
from observe_citra_session import read_memory


def parse(text):
    blocks={};current=None
    for line in text.splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('[') and line.endswith(']'):
            current=line[1:-1]
            if current in blocks:raise ValueError('duplicate section')
            blocks[current]=[]
        elif current is not None and re.fullmatch('[0-9A-Fa-f]{8} [0-9A-Fa-f]{8}',line):
            blocks[current].append(tuple(int(x,16) for x in line.split()))
        else:raise ValueError('unrecognized reference text')
    return blocks


def derive(text):
    blocks=parse(text);versions=[]
    for version in ('1.0','1.1'):
        direct={}
        for label in ('Max Money','Max Caravan'):
            code=blocks[f'{label} v{version}']
            if len(code)!=1 or code[0][0]>>28!=0:raise ValueError('unexpected direct reference')
            direct[label]=code[0][0]&0x0fffffff
        health=blocks[f'Infinite Health v{version}'];stamina=blocks[f'Infinite Stamina v{version}']
        roots=[a&0x0fffffff for a,v in health if a>>28==11]
        if len(roots)!=1:raise ValueError('unique root required')
        root=roots[0]
        lower=next(v for a,v in health if a>>28==4 and a&0x0fffffff==root)
        upper=next(v for a,v in health if a>>28==3 and a&0x0fffffff==root)
        if (lower,upper)!=(0x08800000,0x08d00000):raise ValueError('unexpected guarded interval')
        if [a&0x0fffffff for a,v in stamina if a>>28==11]!=[root]:raise ValueError('stamina root differs')
        inventory=blocks[f'Inventory Items 255x v{version}']
        inv=next(a&0x0fffffff for a,v in inventory if a>>28==10)
        box=blocks[f'1st Item Box Slot Item 99x v{version}'][0][0]&0x0fffffff
        versions.append(dict(version=version,direct=direct,player_root=root,lower_exclusive=lower,
            upper_exclusive=upper,inventory_candidate=inv,box_quantity_candidate=box,
            health_offsets=[a&0x0fffffff for a,v in health if a>>28 in (0,1)],
            stamina_offsets=[a&0x0fffffff for a,v in stamina if a>>28==0]))
    alternate=sorted({a&0x0fffffff for a,v in blocks['Better Cycle First Item (Y + L/R) v1.1'] if a>>28==11})
    return dict(versions=versions,alternate_v11_roots=alternate,source_sections=len(blocks),cheats_executed=False)


def guarded(root,version):
    return type(root) is int and root%4==0 and version['lower_exclusive']<root and root+0x11a0<version['upper_exclusive']


def probe(source,out,image_path,mapping_path,follow=False):
    source=Path(source).read_bytes();plan=derive(source.decode('utf-8'))
    image=Path(image_path).read_bytes();mapping=json.loads(Path(mapping_path).read_bytes())
    sha=lambda b:hashlib.sha256(b).hexdigest()
    if sha(image)!=mapping['output_sha256']:raise ValueError('image identity mismatch')
    text=next(s for s in mapping['segments'] if s['name']=='text');expected=image[text['file_offset']:text['file_offset']+4]
    out=Path(out);out.mkdir(parents=True,exist_ok=False);rows=[];raw=bytearray();roots={};decoded=[]
    def read(address,size,label):
        if not 0x08000000<=address<address+size<=0x10000000 or not 1<=size<=32:
            raise ValueError('probe outside normal heap interval')
        value=read_memory(address,size);rows.append(dict(label=label,address=address,size=size,sha256=sha(value),binary_offset=len(raw),utc=time.time()));raw.extend(value);time.sleep(.05);return value
    if read_memory(text['address'],4)!=expected:raise ValueError('code control before mismatch')
    for sweep in range(2):
        for version in plan['versions']:
            label=version['version'];r=struct.unpack('<I',read(version['player_root'],4,f'{label}:root:{sweep}'))[0]
            roots.setdefault(label,[]).append(r)
            for kind,address in version['direct'].items():read(address,4,f'{label}:{kind}:{sweep}')
            read(version['inventory_candidate'],32,f'{label}:inventory:{sweep}')
            read(version['box_quantity_candidate']-2,8,f'{label}:box:{sweep}')
    for version in plan['versions']:
        values=roots[version['version']];root=values[0];stable=len(set(values))==1;valid=stable and guarded(root,version)
        item=dict(version=version['version'],root_stable=stable,root_within_source_guard=valid,player_identity_verified=False)
        if valid and follow:
            # A bounded experiment justified by the source's explicit guarded root.
            # This does not establish allocation ownership or semantic identity.
            again=struct.unpack('<I',read(version['player_root'],4,'root_recheck'))[0]
            if again!=root:raise ValueError('root changed before bounded follow')
            value=read(root+0x1180,32,version['version']+':player_offsets')
            item.update(followed_bytes=32,health_u16_candidates=[struct.unpack_from('<H',value,o)[0] for o in (4,6,8,20)],stamina_float_candidates=[struct.unpack_from('<f',value,o)[0] for o in (12,16)])
        decoded.append(item)
    if read_memory(text['address'],4)!=expected:raise ValueError('code control after mismatch')
    (out/'samples.bin').write_bytes(raw);(out/'reads.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
    receipt=dict(plan=plan,source_sha256=sha(source),image_sha256=sha(image),reads=len(rows),bytes=len(raw),
        samples_sha256=sha(raw),reads_sha256=sha((out/'reads.json').read_bytes()),results=decoded,
        control_before_matches=True,control_after_matches=True,cheats_executed=False,memory_writes=False,
        heap_allocation_ownership_verified=False,semantic_identity_verified=False)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for n in ('source','out','image','mapping'):p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--follow-guarded-player',action='store_true')
    a=p.parse_args();r=probe(a.source,a.out,a.image,a.mapping,a.follow_guarded_player)
    print(json.dumps(dict(reads=r['reads'],bytes=r['bytes'],results=r['results'],memory_writes=False)))

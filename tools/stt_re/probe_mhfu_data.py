"""Bounded read-only MHFU DATA.BIN TOC pilot using locally reviewed upstream mhef.

External GPL module remains outside Git. Only DataCipher and game identifiers
are loaded; obsolete array.tostring calls are adapted in memory to tobytes.
No savedata, quest or AES functionality is imported or invoked.
"""
import argparse
import array
import ast
import hashlib
import json
from pathlib import Path
import struct
import sys
import time

def load_cipher(source):
    if sys.byteorder!='little': raise ValueError('upstream DataCipher requires little endian host')
    tree=ast.parse(source.read_text(encoding='utf-8'))
    selected=[]
    ids={'MHP2G_JP','MHP2G_NA','MHP2G_EU','MHP3_JP'}
    for node in tree.body:
        if isinstance(node,ast.ClassDef) and node.name=='DataCipher': selected.append(node)
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ids for t in node.targets): selected.append(node)
    class Compat(ast.NodeTransformer):
        def visit_Attribute(self,node):
            self.generic_visit(node)
            if node.attr=='tostring': node.attr='tobytes'
            return node
    code=ast.fix_missing_locations(Compat().visit(ast.Module(body=selected,type_ignores=[])))
    scope={'array':array,'__builtins__':__builtins__}
    exec(compile(code,str(source),'exec'),scope)
    return scope['DataCipher'](scope['MHP2G_EU'])

def validate_toc(plain,total):
    if total%2048 or len(plain)<4 or len(plain)%4: raise ValueError('unaligned DATA/TOC')
    toc=list(struct.unpack('<'+str(len(plain)//4)+'I',plain))
    if toc[0]*2048!=len(plain): raise ValueError('TOC length differs from first sector')
    try: count=toc.index(total//2048)
    except ValueError: raise ValueError('TOC missing end sentinel')
    if not 0<count<=100000: raise ValueError('invalid file count')
    offsets=toc[:count+1]
    if offsets!=sorted(offsets) or offsets[-1]*2048!=total: raise ValueError('nonmonotonic/outside TOC')
    entries=[dict(index=i,lba=offsets[i],allocated_bytes=(offsets[i+1]-offsets[i])*2048) for i in range(count)]
    if any(e['allocated_bytes']>64*1024*1024 for e in entries): raise ValueError('entry exceeds pilot budget')
    return entries

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--upstream',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--all',action='store_true',help='process all bounded entries instead of five')
    a=p.parse_args()
    out=a.out.resolve()
    if any((q/'.git').exists() for q in (out,*out.parents)): raise ValueError('pilot plaintext must stay outside Git')
    out.mkdir(parents=True,exist_ok=False)
    row=next(r for r in json.loads(a.manifest.read_text()) if r['path']=='PSP_GAME/USRDIR/DATA.BIN')
    cipher=load_cipher(a.upstream)
    with a.iso.open('rb') as f:
        f.seek(row['offset']); digest=hashlib.sha256(); remaining=row['bytes']
        while remaining:
            chunk=f.read(min(1024*1024,remaining))
            if not chunk: raise ValueError('truncated DATA source')
            digest.update(chunk); remaining-=len(chunk)
        if digest.hexdigest()!=row['sha256']: raise ValueError('DATA hash differs from manifest')
        f.seek(row['offset'])
        first=f.read(4)
        table_size=struct.unpack('<I',cipher.decrypt(first,0))[0]*2048
        if not 2048<=table_size<=8*1024*1024 or table_size>row['bytes']: raise ValueError('decrypted TOC outside budget')
        f.seek(row['offset'])
        encrypted=f.read(table_size)
        plain=cipher.decrypt(encrypted,0)
        entries=validate_toc(plain,row['bytes'])
        if cipher.encrypt(plain,0)!=encrypted: raise ValueError('TOC roundtrip mismatch')
        results=[]
        selected=entries if a.all else [x for x in entries if 0<x['allocated_bytes']<=4*1024*1024][:5]
        for e in selected:
            f.seek(row['offset']+e['lba']*2048)
            data=f.read(e['allocated_bytes'])
            if len(data)!=e['allocated_bytes']: raise ValueError('truncated entry')
            started=time.monotonic()
            decoded=data if e['index'] in cipher._exceptions else cipher.decrypt(data,e['lba'])
            elapsed=time.monotonic()-started
            if e['index'] not in cipher._exceptions and cipher.encrypt(decoded,e['lba'])!=data: raise ValueError('entry roundtrip mismatch')
            target=out/('entry_'+str(e['index']).zfill(5)+'.bin')
            with target.open('xb') as dst: dst.write(decoded)
            results.append(dict(**e,plaintext_bytes=len(decoded),sha256=hashlib.sha256(decoded).hexdigest(),seconds=elapsed,roundtrip=True))
            if a.all and len(results)%500==0: print(json.dumps(dict(processed=len(results),total=len(entries))),flush=True)
    with (out/'toc-plain.bin').open('xb') as f: f.write(plain)
    report=dict(data_source_sha256=row['sha256'],data_bytes=row['bytes'],upstream_sha256=hashlib.sha256(a.upstream.read_bytes()).hexdigest(),toc_bytes=table_size,file_count=len(entries),toc_roundtrip=True,pilot=results,entries=entries,scope=('All allocated entries processed' if a.all else 'TOC and five payloads processed')+'; roundtrip verified; payload semantics and unpadded lengths not validated')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('entries','pilot')}))

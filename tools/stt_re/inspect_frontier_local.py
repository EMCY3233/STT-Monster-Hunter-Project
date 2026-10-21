"""Local-only Frontier inventory. No network, decryption, writes to input or game execution."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import struct

def signature(head):
    known={b'\x00PSF':'SFO',b'SCE\x00':'SCE_wrapper',b'\x7fELF':'ELF',b'\x89PNG':'PNG',
           b'DDS ':'DDS',b'OggS':'Ogg',b'RIFF':'RIFF',b'FMOD':'FMOD_candidate',b'FSKL':'FSKL_candidate',
           b'ecd\x1a':'ECD_candidate',b'exf\x1a':'EXF_candidate',b'JKR\x1a':'JKR_candidate'}
    if head[:4] in known:
        return known[head[:4]]
    if head.startswith(b'\xff\xd8\xff'):
        return 'JPEG'
    if head.lstrip().lower().startswith((b'<!doctype',b'<html')):
        return 'HTML_candidate'
    return 'unclassified'

def sfo_metadata(data):
    if len(data)<20 or data[:4]!=b'\x00PSF':
        raise ValueError('not SFO')
    ver,keys,values,count=struct.unpack_from('<4I',data,4)
    if count>1024 or 20+16*count>len(data):
        raise ValueError('SFO table bounds')
    allowed={'TITLE','TITLE_ID','APP_VER','VERSION','CATEGORY','CONTENT_ID'}
    fields={}
    for i in range(count):
        keyoff,fmt,length,maxlen,at=struct.unpack_from('<HHIII',data,20+16*i)
        start=keys+keyoff
        end=data.find(b'\0',start)
        if not 0<=start<len(data) or end<start or values+at+length>len(data) or length>maxlen:
            raise ValueError('SFO field bounds')
        key=data[start:end].decode('ascii')
        if key in allowed and fmt in (0x204,4):
            fields[key]=data[values+at:values+at+length].rstrip(b'\0').decode('utf-8','replace')
    return fields

def inspect(root,out):
    root=root.resolve(strict=True)
    out=out.resolve()
    if out.is_relative_to(root):
        raise ValueError('output must stay outside inputs')
    out.mkdir(parents=True,exist_ok=False)
    paths=sorted(p for p in root.rglob('*') if p.is_file())
    records=[]
    for path in paths:
        row={'path':path.relative_to(root).as_posix()}
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(root):
                raise ValueError('link/outside source refused')
            if path.suffix.lower()=='.partial':
                row['status']='excluded_in_progress'
                records.append(row)
                continue
            if path.suffix.lower() in ('.rif','.rap') or 'license' in path.parts or path.parent.name=='package':
                row['status']='excluded_license'
                records.append(row)
                continue
            before=path.stat()
            sha=hashlib.sha256()
            head=b''
            with path.open('rb') as stream:
                while chunk:=stream.read(8*1024*1024):
                    if not head:
                        head=chunk[:512]
                    sha.update(chunk)
            after=path.stat()
            stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
            row.update(bytes=before.st_size,sha256=sha.hexdigest(),signature=signature(head),
                       status='read_ok' if stable else 'changed_during_read')
            if row['signature']=='SFO' and before.st_size<65536:
                data=path.read_bytes()
                if hashlib.sha256(data).hexdigest()!=row['sha256']:
                    raise ValueError('SFO changed on second read')
                row['metadata']=sfo_metadata(data)
            elif row['signature']=='PNG' and len(head)>=24 and head[12:16]==b'IHDR':
                row['dimensions_declared']=list(struct.unpack_from('>II',head,16))
        except (ValueError,OSError,struct.error) as e:
            row.update(status='failed',error=str(e))
        records.append(row)
    paths_after={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    initial={p.relative_to(root).as_posix() for p in paths}
    summary={'generated_utc':datetime.now(timezone.utc).isoformat(),
             'input_label':'Juegos/MHF-Vita/PCSG00350','scope':'local files at enumeration time only; no decryption or recursive container decoding',
             'files_enumerated':len(paths),'bytes_read_files':sum(r.get('bytes',0) for r in records),
             'status':dict(Counter(r['status'] for r in records)),
             'signatures':dict(Counter(r.get('signature','excluded_or_failed') for r in records)),
             'extensions':dict(Counter(Path(r['path']).suffix.lower() for r in records)),
             'added_during_scan':sorted(paths_after-initial),'removed_during_scan':sorted(initial-paths_after),
             'complete_game_dump_verified':False,'switch_excluded':True,
             'records':records}
    with (out/'inventory.json').open('x',encoding='utf-8') as f:
        json.dump(summary,f,indent=2,ensure_ascii=False)
        f.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='records'},ensure_ascii=False))
    if any(r['status'] in ('failed','changed_during_read') for r in records):
        raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    inspect(a.root,a.out)

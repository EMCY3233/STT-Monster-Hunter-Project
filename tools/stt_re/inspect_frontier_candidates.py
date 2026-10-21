"""Hash and structurally inspect explicitly enumerated local Frontier candidates."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

def header(data,total):
    if len(data)<16: raise ValueError('header shorter than 16 bytes')
    if data[:4]==b'JKR\x1a':
        version,codec,start,size=struct.unpack_from('<HHII',data,4)
        if not 16<=start<=total: raise ValueError('JKR data offset outside file')
        if not 0<size<=128*1024*1024: raise ValueError('JKR declared output outside budget')
        if codec not in (0,1,2,3,4): raise ValueError('unknown JKR codec')
        return dict(kind='JKR',version=version,codec=codec,data_offset=start,declared_output_bytes=size,payload_bytes=total-start,header_bounds_valid=True)
    if data[:4]==b'ecd\x1a':
        key_index=struct.unpack_from('<H',data,4)[0]
        size=struct.unpack_from('<I',data,8)[0]
        if key_index>5: raise ValueError('unknown ECD parameter index')
        if size!=total-16: raise ValueError('ECD declared payload differs from file length')
        return dict(kind='ECD',declared_payload_bytes=size,payload_length_matches=True,parameter_index_supported=True)
    if data[:4]==b'SCE\0':
        return dict(kind='SCE_wrapper',interpretation='signature only; not ELF or executable validation')
    raise ValueError('candidate signature no longer matches')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--candidates',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); root=a.root.resolve(strict=True); out=a.out.resolve()
    if out.is_relative_to(root): raise ValueError('output inside inputs')
    out.mkdir(parents=True,exist_ok=False)
    rows=[]
    for source in json.loads(a.candidates.read_text())['candidate_containers']:
        path=(root/source['path']).resolve(strict=True)
        if not path.is_relative_to(root): raise ValueError('path outside root')
        before=path.stat(); digest=hashlib.sha256(); prefix=b''
        with path.open('rb') as f:
            while chunk:=f.read(1024*1024):
                if not prefix: prefix=chunk[:16]
                digest.update(chunk)
        after=path.stat()
        if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns): raise ValueError('input changed')
        if before.st_size!=source['bytes'] or digest.hexdigest()!=source['sha256']: raise ValueError('candidate hash or size mismatch')
        row=dict(path=source['path'],bytes=before.st_size,sha256=digest.hexdigest(),matches_census=True)
        try: row.update(header(prefix,before.st_size))
        except ValueError as e: row.update(kind='rejected',error=str(e))
        rows.append(row)
    report=dict(scope='50 census candidates only; complete hashes, bounded headers; no decryption/decompression/execution',candidate_manifest_sha256=hashlib.sha256(a.candidates.read_bytes()).hexdigest(),counts=dict(Counter(r['kind'] for r in rows)),rows=rows)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'}))

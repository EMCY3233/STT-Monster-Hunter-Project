"""Bounded metadata for already plain PSP ELF and MHXX ExeFS; never writes code."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def probe(root):
    audit=root/'analysis-local/stt-re-audit-20261021'
    rows=json.loads((audit/'psp-files.json').read_text())
    boot=next(r for r in rows if r['path']=='PSP_GAME/SYSDIR/BOOT.BIN')
    with (root/'Juegos/MHFU/Monster Hunter Freedom Unite.iso').open('rb') as f:
        f.seek(boot['offset'])
        data=f.read(boot['bytes'])
    if hashlib.sha256(data).hexdigest()!=boot['sha256'] or data[:7]!=b'\x7fELF\x01\x01\x01':
        raise ValueError('ELF identity mismatch')
    typ,machine,ver,entry,phoff,shoff,flags,ehsize,phsize,phnum,shsize,shnum,shstr=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
    if ehsize!=52 or phsize!=32 or phnum>1024 or phoff+phnum*phsize>len(data):
        raise ValueError('ELF header/program table bounds')
    segments=[]
    for i in range(phnum):
        pt,offset,va,pa,filesz,memsz,pflags,align=struct.unpack_from('<8I',data,phoff+i*phsize)
        if offset+filesz>len(data) or (pt==1 and filesz>memsz):
            raise ValueError('ELF segment bounds')
        segments.append(dict(type=pt,offset=offset,vaddr=va,filesz=filesz,memsz=memsz,flags=pflags,alignment=align))
    elf=dict(source='MHFU ISO / '+boot['path'],sha256=boot['sha256'],bytes=len(data),elf_class=32,endian='little',type=typ,machine=machine,entry=entry,flags=flags,segments=segments,section_headers=shnum,code_executed=False,functions_identified=False)
    p=root/'analysis-local/containers/MHXX-patch-content.0000.00000000'
    with p.open('rb') as f:
        header=f.read(512)
        if header[256:260]!=b'NCCH' or not header[0x18f]&4:
            raise ValueError('not explicitly plain NCCH')
        # Only current CTR media unit flag zero is supported here.
        if header[0x18e]!=0:
            raise ValueError('unsupported media unit')
        off,size=struct.unpack_from('<II',header,0x1a0)
        off*=512
        size*=512
        if off+size>p.stat().st_size or size<512:
            raise ValueError('ExeFS bounds')
        f.seek(off)
        table=f.read(512)
        files=[]
        for i in range(10):
            name,at,n=struct.unpack_from('<8sII',table,i*16)
            if not name.strip(b'\0'):
                continue
            if at+n>size-512:
                raise ValueError('ExeFS file bounds')
            f.seek(off+512+at)
            h=hashlib.sha256(f.read(n)).hexdigest()
            files.append(dict(name=name.rstrip(b'\0').decode('ascii'),bytes=n,offset=at,sha256=h,hash_matches_table=h==table[0xc0+(9-i)*32:0xc0+(10-i)*32].hex()))
    return dict(psp_elf=elf,exefs=dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),offset=off,bytes=size,header_hash_matches_ncch=hashlib.sha256(table).digest()==header[0x1c0:0x1e0],files=files,code_decompression='not_attempted',disassembly='not_attempted'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    r=probe(a.root.resolve())
    with a.output.open('x',encoding='utf-8') as f:
        f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))

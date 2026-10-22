"""Bounded ELF32 LE section/symbol metadata, without executing or exporting code."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

def inspect(data):
    if len(data)<52 or data[:7]!=b'\x7fELF\x01\x01\x01':
        raise ValueError('expected ELF32 little endian')
    typ,machine,version,entry,phoff,shoff,flags,ehsize,phsize,phnum,shsize,shnum,shstr=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
    if ehsize!=52 or phsize!=32 or shsize!=40 or phnum>1024 or not 0<shnum<=8192 or shstr>=shnum:
        raise ValueError('unsupported ELF header/table dimensions')
    if phoff+phsize*phnum>len(data) or shoff+shsize*shnum>len(data):
        raise ValueError('ELF tables outside file')
    programs=[struct.unpack_from('<8I',data,phoff+i*phsize) for i in range(phnum)]
    loads=[]
    for pt,offset,va,pa,filesz,memsz,pflags,align in programs:
        if offset+filesz>len(data) or (pt==1 and filesz>memsz):
            raise ValueError('program payload outside file/memory')
        if pt==1:
            loads.append(dict(vaddr=va,offset=offset,filesz=filesz,memsz=memsz,flags=pflags,alignment=align))
    sections=[struct.unpack_from('<10I',data,shoff+i*shsize) for i in range(shnum)]
    strings=sections[shstr]
    if strings[1]!=3 or strings[4]+strings[5]>len(data):
        raise ValueError('section-name string table invalid')
    table=data[strings[4]:strings[4]+strings[5]]
    records=[]
    symcounts=Counter()
    for i,(name,st,fl,addr,off,size,link,info,align,entsize) in enumerate(sections):
        if st!=8 and off+size>len(data):
            raise ValueError('section payload outside file')
        if name>=len(table) or table.find(b'\0',name)<0:
            raise ValueError('section name out of bounds')
        label=table[name:table.index(b'\0',name)].decode('ascii','replace')
        row=dict(index=i,name=label,type=st,flags=fl,address=addr,offset=off,bytes=size,entry_bytes=entsize)
        if st in (2,11):
            if entsize!=16 or size%16 or link>=shnum or sections[link][1]!=3:
                raise ValueError('invalid symbol table shape/link')
            for at in range(off,off+size,16):
                sn,value,ss,si,other,section=struct.unpack_from('<IIIBBH',data,at)
                linked=sections[link]
                if sn>=linked[5]:
                    raise ValueError('symbol name outside linked strings')
                symcounts[str(si&15)]+=1
            row['symbols']=size//16
        records.append(row)
    executable=[p for p in loads if p['flags']&1 and p['vaddr']<=entry<p['vaddr']+p['filesz']]
    return dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),elf_type=typ,machine=machine,
                entry=entry,entry_in_file_backed_executable_load=bool(executable),
                entry_file_offsets=[p['offset']+entry-p['vaddr'] for p in executable],
                program_types=dict(Counter(str(p[0]) for p in programs)),load_segments=loads,
                section_count=shnum,section_types=dict(Counter(str(s[1]) for s in sections)),
                symbol_types=dict(symcounts),sections=records,semantic_function_validation=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    row=next(r for r in json.loads(a.manifest.read_text()) if r['path']=='PSP_GAME/SYSDIR/BOOT.BIN')
    with a.iso.open('rb') as f:
        f.seek(row['offset'])
        data=f.read(row['bytes'])
    if hashlib.sha256(data).hexdigest()!=row['sha256']:
        raise ValueError('source hash differs from manifest')
    result=inspect(data)
    with a.output.open('x',encoding='utf-8') as f:
        f.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='sections'}))

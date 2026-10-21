"""Map one PSP import-table NID pointer; no execution, code or NID export."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def map_file_backed(va,size,load):
    delta=va-load['vaddr']
    if va%4 or size<=0 or delta<0 or delta+size>load['filesz']: raise ValueError('target not aligned/file-backed in selected PT_LOAD')
    return load['offset']+delta

def inspect(data,baseline):
    if data[:7]!=b'\x7fELF\x01\x01\x01' or len(data)<52: raise ValueError('expected ELF32 LE')
    typ,machine,version,entry,phoff,shoff,flags,ehsize,phsize,phnum,shsize,shnum,shstr=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
    if typ!=2 or machine!=8 or ehsize!=52 or phsize!=32 or shsize!=40 or phnum<1: raise ValueError('unsupported ELF layout')
    if baseline['program_types'].get('1')!=1: raise ValueError('baseline must establish one PT_LOAD')
    if phoff+32>len(data): raise ValueError('selected program header bounds')
    kind,off,va,pa,filesz,memsz,pflags,alignment=struct.unpack_from('<8I',data,phoff)
    load=dict(vaddr=va,offset=off,filesz=filesz,memsz=memsz,flags=pflags,alignment=alignment)
    if kind!=1 or load!=baseline['load_segments'][0] or off+filesz>len(data) or filesz>memsz: raise ValueError('selected PT_LOAD differs from prior evidence')
    def selected(name):
        row=next(r for r in baseline['sections'] if r['name']==name)
        at=shoff+row['index']*40
        if row['index']>=shnum or at+40>len(data): raise ValueError('selected section header bounds')
        raw=struct.unpack_from('<10I',data,at)
        values=dict(type=raw[1],flags=raw[2],address=raw[3],offset=raw[4],bytes=raw[5],entry_bytes=raw[9])
        if any(values[k]!=row[k] for k in values) or row['type']!=1 or not row['flags']&2 or row['offset']+row['bytes']>len(data): raise ValueError('selected section differs from prior evidence')
        return row
    source=selected('.lib.stub'); target=selected('.rodata.sceNid')
    at=source['offset']
    if source['bytes']<20: raise ValueError('import record truncated')
    length=data[at+8]; variables=data[at+9]; functions=struct.unpack_from('<H',data,at+10)[0]
    if length!=5 or variables!=0 or not 0<functions<=4096: raise ValueError('outside single five-word function-import scope')
    pointer=struct.unpack_from('<I',data,at+12)[0]; size=functions*4
    if map_file_backed(source['address'],20,load)!=at: raise ValueError('source section/segment mapping mismatch')
    file_offset=map_file_backed(pointer,size,load)
    relative=pointer-target['address']
    if relative<0 or relative+size>target['bytes'] or target['offset']+relative!=file_offset: raise ValueError('target section/segment mapping mismatch')
    return dict(elf_type=typ,machine=machine,source_section=dict(index=source['index'],name=source['name'],address=source['address'],offset=at,bytes=source['bytes']),first_record=dict(length_words=length,bytes=length*4,functions=functions,variables=variables),reference=dict(field_relative_offset=12,field_vaddr=source['address']+12,field_file_offset=at+12,target_vaddr=pointer,target_file_offset=file_offset,target_section_index=target['index'],target_section_name=target['name'],target_relative_offset=relative,referenced_nid_array_bytes=size),mapping_agrees_between_section_and_pt_load=True,target_in_file_backed_range=True,selected_program_header_index=0,selected_section_headers_checked=2,prior_complete_section_check_repeated=False,confidence='high structural confidence for this single import-table pointer; no function identity or runtime resolution asserted',semantics_verified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--elf',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--dump-receipt',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.elf.stat().st_size>4*1024*1024: raise ValueError('artifact budget')
    full=a.elf.read_bytes(); baseline=json.loads(a.baseline.read_text()); dump=json.loads(a.dump_receipt.read_text())
    digest=hashlib.sha256(full).hexdigest()
    if digest!=dump['sha256'] or len(full)!=dump['bytes']: raise ValueError('dump differs from receipt')
    prefix=full[:baseline['bytes']]
    if hashlib.sha256(prefix).hexdigest()!=baseline['sha256']: raise ValueError('canonical BOOT prefix differs from baseline')
    report=inspect(prefix,baseline)
    report.update(artifact_sha256=digest,artifact_bytes=len(full),canonical_prefix_sha256=baseline['sha256'],canonical_prefix_bytes=len(prefix),excluded_uninterpreted_tail_bytes=len(full)-len(prefix),baseline_receipt_sha256=hashlib.sha256(a.baseline.read_bytes()).hexdigest(),source_unchanged=hashlib.sha256(a.elf.read_bytes()).hexdigest()==digest)
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

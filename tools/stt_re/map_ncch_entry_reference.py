"""Map one source-derived NCCH entry reference without decoding instructions.

Reference: Azahar 2126.2 commit219d743a1e698101fe1ab8bef43e6563126c3c27,
loader/ncch.cpp, kernel/process.cpp and kernel/thread.cpp. This tool implements
metadata/range checks; it never decompresses or executes the input.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct


def digest(data):
    return hashlib.sha256(data).hexdigest()


def map_reference(segments, file_bytes, va, width):
    if width <= 0 or va < 0 or va+width > 2**32:
        raise ValueError('reference bounds')
    matches=[]
    previous_end=0
    expected_offset=0
    permissions={'text':'r-x','ro':'r--','data':'rw-'}
    if [s['name'] for s in segments] != ['text','ro','data']:
        raise ValueError('requires ordered text/ro/data')
    for segment in segments:
        base=segment['address']; capacity=segment['mapped_bytes']; size=segment['code_bytes']
        off=segment['file_offset']
        if base%4096 or capacity%4096 or not 0<=size<=capacity or base<previous_end:
            raise ValueError('segment layout bounds or overlap')
        if off!=expected_offset or off+capacity>file_bytes or base+capacity>2**32:
            raise ValueError('segment file coverage')
        delta=va-base
        if 0<=delta and delta+width<=size:
            matches.append(dict(virtual_address=va,bytes=width,file_offset=off+delta,
                                segment=segment['name'],segment_delta=delta,
                                file_backed=True,within_declared_code_bytes=True,
                                permissions_from_azahar=permissions[segment['name']]))
        previous_end=base+capacity;expected_offset+=capacity
    if expected_offset!=file_bytes or len(matches)!=1:
        raise ValueError('reference is not uniquely backed by declared code/data')
    return matches[0]


def inspect(ncch,code,receipt):
    if len(ncch)<1536 or len(ncch)>128*1024*1024 or ncch[256:260]!=b'NCCH':
        raise ValueError('NCCH bounds or signature')
    if digest(ncch)!=receipt['source_sha256'] or digest(code)!=receipt['output_sha256']:
        raise ValueError('source identity differs from BLZ receipt')
    if len(code)!=receipt['output_bytes'] or len(code)>64*1024*1024:
        raise ValueError('code output length differs')
    if not ncch[399]&4 or struct.unpack_from('<I',ncch,384)[0]!=1024:
        raise ValueError('requires plain NCCH with accepted ExHeader size')
    ex=ncch[512:1536]
    if hashlib.sha256(ex).digest()!=ncch[352:384] or digest(ex)!=receipt['exheader_sha256']:
        raise ValueError('ExHeader identity mismatch')
    segments=[];offset=0
    for name,at in [('text',16),('ro',32),('data',48)]:
        address,pages,size=struct.unpack_from('<III',ex,at)
        segment=dict(name=name,address=address,pages=pages,code_bytes=size,
                     mapped_bytes=pages*4096,file_offset=offset,padding_bytes=pages*4096-size)
        segments.append(segment);offset+=pages*4096
    if segments!=receipt['segments']:
        raise ValueError('segment metadata differs from verified BLZ receipt')
    # The entry assignment is documented in the pinned loader, not an ExHeader entry field.
    entry=segments[0]['address']
    mapping=map_reference(segments,len(code),entry,4)
    if entry%4:
        raise ValueError('outside demonstrated aligned A32 startup scope')
    return dict(source_ncch_sha256=digest(ncch),code_sha256=digest(code),
                code_bytes=len(code),exheader_sha256=digest(ex),
                loader_derived_entry=entry,explicit_exheader_entry_field=False,
                mapping=mapping,initial_t_bit_from_loader=entry&1,
                expected_initial_instruction_state='ARM/A32',
                state_evidence='Azahar ResetThreadContext sets CPSR.T from entry_point bit0',
                instruction_decoding_performed=False,instruction_bytes_exported=False,
                actual_execution_observed=False,hardware_entry_verified=False,
                game_function_identified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ncch',type=Path,required=True)
    p.add_argument('--code',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.ncch.stat().st_size>128*1024*1024 or a.code.stat().st_size>64*1024*1024:
        raise ValueError('input budgets')
    ncch=a.ncch.read_bytes();code=a.code.read_bytes()
    r=inspect(ncch,code,json.loads(a.receipt.read_text(encoding='utf-8')))
    r['ncch_unchanged']=digest(a.ncch.read_bytes())==digest(ncch)
    r['code_unchanged']=digest(a.code.read_bytes())==digest(code)
    if not r['ncch_unchanged'] or not r['code_unchanged']:
        raise ValueError('input changed')
    with a.out.open('x',encoding='utf-8') as f:f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))

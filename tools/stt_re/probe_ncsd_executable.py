"""Probe partition zero of one plain NCSD without extraction or decompression.

Layouts: Azahar2126.2, commit219d743a1e698101fe1ab8bef43e6563126c3c27,
src/core/file_sys/ncch_container.h. Reuses the existing BLZ footer and segment
range validators; a declared decompressed layout is not a produced code.bin.
Distributed under GPL-2.0-or-later with the reused BLZ component; license at
docs/research/stt-re-20261021/azahar-gpl2-license.md.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from inspect_ncch_code import blz_footer
from map_ncch_entry_reference import map_reference

READ_BUDGET=64*1024*1024


def sha(data):return hashlib.sha256(data).hexdigest()


def sha_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()


def probe(read_at,file_bytes):
    ranges=[];used=0
    def read(at,n,label):
        nonlocal used
        if at<0 or n<0 or at+n>file_bytes or used+n>READ_BUDGET:
            raise ValueError('read bounds or structural budget')
        data=read_at(at,n)
        if len(data)!=n:raise ValueError('short read')
        ranges.append(dict(label=label,offset=at,bytes=n,sha256=sha(data)))
        used+=n
        return data
    outer=read(0,512,'NCSD header')
    if outer[256:260]!=b'NCSD':raise ValueError('NCSD signature')
    po,ps=struct.unpack_from('<II',outer,0x120);po*=512;ps*=512
    if po<512 or ps<1536 or po+ps>file_bytes:raise ValueError('partition zero bounds')
    h=read(po,512,'NCCH header')
    if h[256:260]!=b'NCCH' or not h[0x18f]&4 or h[0x18e]!=0:
        raise ValueError('requires plain NCCH with 512-byte units')
    if not h[0x18d]&2:raise ValueError('selected NCCH is not executable')
    declared=struct.unpack_from('<I',h,0x104)[0]*512
    if not 1536<=declared<=ps:raise ValueError('NCCH declared length')
    ex_size=struct.unpack_from('<I',h,0x180)[0]
    if ex_size!=1024:raise ValueError('ExHeader outside current scope')
    ex=read(po+512,ex_size,'ExHeader hashed region')
    if hashlib.sha256(ex).digest()!=h[0x160:0x180]:raise ValueError('ExHeader hash')
    pid=int.from_bytes(h[0x118:0x120],'little')
    if int.from_bytes(ex[0x200:0x208],'little')!=pid:
        raise ValueError('ExHeader program ID mismatch')
    segments=[];offset=0
    for name,at in [('text',16),('ro',32),('data',48)]:
        address,pages,size=struct.unpack_from('<III',ex,at)
        segments.append(dict(name=name,address=address,pages=pages,code_bytes=size,
                             mapped_bytes=pages*4096,file_offset=offset,padding_bytes=pages*4096-size))
        offset+=pages*4096
    if not 0<offset<=READ_BUDGET:raise ValueError('declared code set budget')
    # Validates the declared destination layout, not the compressed file mapping.
    map_reference(segments,offset,segments[0]['address'],4)
    start,units,hash_units=struct.unpack_from('<III',h,0x1a0)
    start*=512;size=units*512
    if start<512+ex_size or size<512 or start+size>declared or hash_units!=1:
        raise ValueError('ExeFS bounds or hash-region scope')
    table=read(po+start,512,'ExeFS table')
    if hashlib.sha256(table).digest()!=h[0x1c0:0x1e0]:raise ValueError('ExeFS table hash')
    entries=[];intervals=[];code=None
    for i in range(8):
        raw,at,n=struct.unpack_from('<8sII',table,i*16)
        if not raw.rstrip(b'\0'):continue
        if not n or at+n>size-512:raise ValueError('ExeFS entry bounds')
        if any(at<end and begin<at+n for begin,end in intervals):raise ValueError('ExeFS entries overlap')
        intervals.append((at,at+n))
        name=raw.rstrip(b'\0').decode('ascii')
        # Entry names are identifiers; never use them as output paths.
        data=read(po+start+512+at,n,'ExeFS entry '+str(i))
        actual=sha(data);expected=table[512-(i+1)*32:512-i*32].hex()
        if actual!=expected:raise ValueError('ExeFS entry hash')
        entries.append(dict(index=i,name=name,relative_data_offset=at,
                            file_offset=po+start+512+at,bytes=n,sha256=actual,hash_verified=True))
        if name=='.code':
            if code is not None:raise ValueError('duplicate .code')
            code=data
    if code is None:raise ValueError('missing .code')
    compressed=bool(ex[13]&1)
    footer=blz_footer(code) if compressed else None
    expected_output=footer['output_bytes'] if footer else len(code)
    if expected_output!=offset:raise ValueError('code size differs from declared pages')
    flags=ex[0x20c];mode=ex[0x20e]
    return dict(partition_index=0,partition_offset=po,partition_bytes=ps,
                ncch_declared_bytes=declared,program_id=f'{pid:016X}',
                no_crypto=True,executable_content_flag=True,exheader_hash_verified=True,
                exheader_sha256=sha(ex),segments=segments,declared_code_pages_bytes=offset,
                stack_bytes=struct.unpack_from('<I',ex,28)[0],bss_bytes=struct.unpack_from('<I',ex,60)[0],
                compression_flag_byte=ex[13],code_compressed=compressed,blz_footer=footer,
                exefs_offset_in_partition=start,exefs_bytes=size,exefs_table_hash_verified=True,
                exefs_entries=entries,
                arm11_caps=dict(core_version=struct.unpack_from('<I',ex,0x208)[0],
                                n3ds_cpu_flags_raw=flags,enable_l2_cache_requested=bool(flags&1),
                                enable_804mhz_requested=bool(flags&2),n3ds_mode_raw=ex[0x20d],
                                system_mode_raw=(mode>>4)&15,ideal_processor_raw=mode&3,
                                affinity_mask_raw=(mode>>2)&3,actual_clock_verified=False,
                                arm_thumb_instruction_state_verified=False),
                read_ranges=ranges,structural_read_bytes=used,read_budget_bytes=READ_BUDGET,
                reused_validators=['inspect_ncch_code.blz_footer','map_ncch_entry_reference.map_reference'],
                declared_layout_only=True,code_decompressed=False,romfs_parsed_or_extracted=False,
                binary_output_written=False,game_functions_identified=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    before=sha_file(a.input)
    if before!=a.expected_sha256:raise ValueError('original hash mismatch')
    size=a.input.stat().st_size
    with a.input.open('rb') as f:
        def read_at(at,n):f.seek(at);return f.read(n)
        r=probe(read_at,size)
    after=sha_file(a.input)
    if before!=after:raise ValueError('original changed')
    r.update(original_bytes=size,original_sha256_before=before,original_sha256_after=after,
             original_unchanged=True,full_file_hash_passes=2)
    with a.out.open('x',encoding='utf-8') as f:f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))

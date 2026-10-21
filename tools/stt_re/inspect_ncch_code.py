"""Validate one plain NCCH code set and decompress BLZ only when its flag requests it.

LZSS algorithm adapted from Citra/Azahar ncch_container.cpp, commit
219d743a1e698101fe1ab8bef43e6563126c3c27 (Copyright 2014-2026
Citra Emulator Project / Azahar Emulator Project), GPL-2.0-or-later.
This program is free software under GPL version 2 or, at your option, any
later version, without any warranty; see the included license at
docs/research/stt-re-20261021/azahar-gpl2-license.md and
https://www.gnu.org/licenses/old-licenses/gpl-2.0.html.
Extra range checks and exact-prefix accounting intentionally fail closed.
No disassembly, execution, keys, or semantic classification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

LIMIT = 64 * 1024 * 1024
PAGE = 4096


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blz_footer(data):
    if len(data) < 8:
        raise ValueError('BLZ footer truncated')
    packed, extra = struct.unpack_from('<II', data, len(data)-8)
    top, bottom = packed >> 24, packed & 0xffffff
    size = len(data) + extra
    if not 8 <= top <= bottom <= len(data):
        raise ValueError('BLZ footer top/bottom bounds')
    if size > LIMIT:
        raise ValueError('BLZ output budget')
    return dict(top=top, bottom=bottom, additional_bytes=extra,
                output_bytes=size, prefix_bytes=len(data)-bottom,
                compressed_stream_bytes=bottom-top)


def decompress_blz(data):
    meta = blz_footer(data)
    result = bytearray(meta['output_bytes'])
    result[:len(data)] = data
    cursor = len(data)-meta['top']
    stop = meta['prefix_bytes']
    output = len(result)
    literal_count = reference_count = reference_bytes = controls = 0
    while cursor > stop:
        cursor -= 1
        control = data[cursor]
        controls += 1
        for bit in range(8):
            if cursor == stop:
                break
            if control & (0x80 >> bit):
                if cursor-stop < 2:
                    raise ValueError('BLZ token crosses prefix')
                cursor -= 2
                token = int.from_bytes(data[cursor:cursor+2], 'little')
                count, distance = (token >> 12)+3, (token & 4095)+2
                if output-count < stop:
                    raise ValueError('BLZ output crosses prefix')
                for _ in range(count):
                    if output+distance >= len(result):
                        raise ValueError('BLZ reference beyond output')
                    value = result[output+distance]
                    output -= 1
                    result[output] = value
                reference_count += 1
                reference_bytes += count
            else:
                if output <= stop:
                    raise ValueError('BLZ literal crosses prefix')
                cursor -= 1
                output -= 1
                result[output] = data[cursor]
                literal_count += 1
    if cursor != stop or output != stop:
        raise ValueError('BLZ output/prefix coverage mismatch')
    if result[:stop] != data[:stop]:
        raise ValueError('BLZ preserved prefix mismatch')
    meta.update(input_stream_consumed=True, output_complete=True,
                prefix_unchanged=True, literals=literal_count,
                backreferences=reference_count, backreference_bytes=reference_bytes,
                control_bytes=controls, output_sha256=sha(result))
    return bytes(result), meta


def inspect_ncch(data):
    if not 0x600 <= len(data) <= 128*1024*1024 or data[0x100:0x104] != b'NCCH':
        raise ValueError('NCCH signature or budget')
    if not data[0x18f] & 4 or data[0x18e] != 0:
        raise ValueError('requires plain NCCH with 512-byte units')
    ex_size = struct.unpack_from('<I', data, 0x180)[0]
    if ex_size != 0x400 or 0x200+ex_size > len(data):
        raise ValueError('ExHeader scope/bounds')
    ex = data[0x200:0x600]
    if hashlib.sha256(ex).digest() != data[0x160:0x180]:
        raise ValueError('ExHeader hash mismatch')
    segments=[]
    offset=0
    previous_end=0
    for name,at in [('text',0x10),('ro',0x20),('data',0x30)]:
        address,pages,size=struct.unpack_from('<III',ex,at)
        capacity=pages*PAGE
        if address%PAGE or size>capacity or capacity>LIMIT or address+capacity>2**32:
            raise ValueError('segment address/capacity bounds')
        if segments and address<previous_end:
            raise ValueError('segments overlap')
        segments.append(dict(name=name,address=address,pages=pages,code_bytes=size,
                             mapped_bytes=capacity,file_offset=offset,padding_bytes=capacity-size))
        offset+=capacity
        previous_end=address+capacity
    if offset>LIMIT:
        raise ValueError('code set budget')
    bss=struct.unpack_from('<I',ex,0x3c)[0]
    if previous_end+((bss+PAGE-1)//PAGE)*PAGE>2**32:
        raise ValueError('BSS address bounds')
    start,units=struct.unpack_from('<II',data,0x1a0)
    start*=512; size=units*512
    if size<512 or start<0x600 or start+size>len(data):
        raise ValueError('ExeFS bounds')
    table=data[start:start+512]
    if hashlib.sha256(table).digest()!=data[0x1c0:0x1e0]:
        raise ValueError('ExeFS header hash mismatch')
    sections=[]
    for i in range(8):
        name,at,n=struct.unpack_from('<8sII',table,i*16)
        if name.rstrip(b'\0')!=b'.code':
            continue
        if at+n>size-512:
            raise ValueError('.code range exceeds ExeFS')
        code=data[start+512+at:start+512+at+n]
        if hashlib.sha256(code).digest()!=table[512-(i+1)*32:512-i*32]:
            raise ValueError('.code hash mismatch')
        sections.append((code,start+512+at))
    if len(sections)!=1:
        raise ValueError('requires exactly one .code section')
    code,code_at=sections[0]
    compressed=bool(ex[0xd]&1)
    result=dict(source_bytes=len(data),source_sha256=sha(data),exheader_sha256=sha(ex),
                exheader_hash_verified=True,compression_flag_byte=ex[0xd],compressed=compressed,
                code_offset=code_at,code_bytes=len(code),code_sha256=sha(code),
                code_hash_verified=True,segments=segments,expected_code_pages_bytes=offset,
                stack_bytes=struct.unpack_from('<I',ex,0x1c)[0],bss_bytes=bss,
                bss_page_bytes=((bss+PAGE-1)//PAGE)*PAGE)
    if compressed:
        footer=blz_footer(code)
        if footer['output_bytes']!=offset:
            raise ValueError('BLZ output differs from declared segment pages')
        output,meta=decompress_blz(code)
        result.update(decompression=meta,decompressed=True)
    else:
        if len(code)!=offset:
            raise ValueError('plain .code differs from declared segment pages')
        output=code
        result.update(decompression=None,decompressed=False)
    result.update(output_bytes=len(output),output_sha256=sha(output),
                  code_executed=False,disassembly_performed=False,semantics_verified=False)
    return result,output


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ncch',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    if a.ncch.stat().st_size>128*1024*1024:
        raise ValueError('input budget')
    data=a.ncch.read_bytes()
    if sha(data)!=a.expected_sha256:
        raise ValueError('input hash mismatch')
    report,output=inspect_ncch(data)
    report['source_unchanged']=sha(a.ncch.read_bytes())==sha(data)
    if not report['source_unchanged']:
        raise ValueError('source changed during read')
    a.out_dir.mkdir(exist_ok=False)
    (a.out_dir/'code.bin').write_bytes(output)
    (a.out_dir/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

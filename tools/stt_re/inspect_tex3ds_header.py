"""One TEX A6/3DS header and compressed-range probe; never decodes pixels.

References: Kuriimu2 MT TEX N3DS loader and mhff n3ds texture reader.
Restricted to one image/mip, swizzle field zero and dimensions multiple of 8.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

def inspect(data):
    if not 20<=len(data)<=1024*1024 or data[:4]!=b'TEX\0': raise ValueError('TEX signature or header/table bounds')
    word0,word1,word2=struct.unpack_from('<3I',data,4)
    version=word0&4095; swizzle=(word0>>12)&4095; size_shift=(word0>>24)&15; high=(word0>>28)&15
    mips=word1&63; width=(word1>>6)&8191; height=(word1>>19)&8191
    images=word2&255; fmt=(word2>>8)&255
    if version!=0xa6 or swizzle!=0 or images!=1 or mips!=1: raise ValueError('outside single-image/single-mip A6 layout scope')
    if not width or not height or width%8 or height%8: raise ValueError('dimensions outside demonstrated tiled-block scope')
    if fmt not in (11,12): raise ValueError('unsupported 3DS color format')
    relative=struct.unpack_from('<I',data,16)[0]
    payload_start=20+relative
    bytes_per_block=8 if fmt==11 else 16
    payload_bytes=(width//4)*(height//4)*bytes_per_block
    payload_end=payload_start+payload_bytes
    if payload_start<20 or payload_end>len(data): raise ValueError('compressed image range exceeds file')
    return dict(signature='TEX',version=version,version_hex=f'0x{version:03X}',width=width,height=height,images_declared=images,mips_declared=mips,color_format=fmt,color_format_name='ETC1' if fmt==11 else 'ETC1A4',swizzle_field=swizzle,size_shift_field=size_shift,high_flag_nibble=high,high_flag_semantics_verified=False,unknown_u16=(word2>>16)&65535,header_bytes=16,mip_table_bytes=4,mip_offset_relative_to_data_base=relative,data_base_offset=20,compressed_range=dict(offset=payload_start,bytes=payload_bytes,end=payload_end,in_file=True),block_formula=dict(width=4,height=4,bytes_per_block=bytes_per_block,blocks=(width//4)*(height//4)),trailing_bytes=len(data)-payload_end,exact_header_table_payload_fit=payload_end==len(data),pixel_decoding_performed=False,swizzle_visual_validation=False,functional_texture_validation=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.input.stat().st_size>1024*1024: raise ValueError('input budget')
    data=a.input.read_bytes(); digest=hashlib.sha256(data).hexdigest()
    if digest!=a.expected_sha256: raise ValueError('source hash mismatch')
    report=inspect(data); report.update(source_bytes=len(data),source_sha256=digest,source_unchanged=hashlib.sha256(a.input.read_bytes()).hexdigest()==digest)
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

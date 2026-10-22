"""Single-mip TEX A6 ETC1/ETC1A4 -> RGBA PNG, preserving 3DS A4 alpha.

Native texture row order, no in-game orientation/material association asserted.
ETC1 backend: pinned texture2ddecoder 1.0.6, BGRA output.
"""
import argparse,hashlib,json,struct,sys,zlib
from pathlib import Path
from inspect_tex3ds_header import inspect
from extract_arc import private_destination


def decode(data,backend):
    info=inspect(data);w,h=info['width'],info['height'];alpha=info['color_format']==12
    if w*h>4*1024*1024 or not info['exact_header_table_payload_fit']:raise ValueError('pixel budget or trailing bytes')
    out=bytearray(w*h*4);at=info['compressed_range']['offset']
    for ty in range(0,h,8):
        for tx in range(0,w,8):
            for sub in range(4):
                packed_alpha=int.from_bytes(data[at:at+8],'little') if alpha else (1<<64)-1
                if alpha:at+=8
                color=data[at:at+8];at+=8
                # Nintendo stores ETC1 u64 little-endian; standard ETC1 is big-endian.
                pixels=backend.decode_etc1(color[::-1],4,4)
                if len(pixels)!=64:raise ValueError('unexpected backend block size')
                for y in range(4):
                    for x in range(4):
                        j=(y*4+x)*4;bx=tx+(sub&1)*4+x;by=ty+(sub>>1)*4+y;k=(by*w+bx)*4
                        b,g,r,_=pixels[j:j+4];a=((packed_alpha>>(4*(x*4+y)))&15)*17
                        out[k:k+4]=bytes((r,g,b,a))
    return bytes(out),info


def png_rgba(rgba,w,h):
    if len(rgba)!=w*h*4 or not w or not h:raise ValueError('RGBA dimensions mismatch')
    def chunk(kind,body):return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
    rows=b''.join(b'\0'+rgba[y*w*4:(y+1)*w*4] for y in range(h))
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>2I5B',w,h,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(rows))+chunk(b'IEND',b'')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('--out',type=Path,required=True);p.add_argument('--expect-sha256',required=True);p.add_argument('--decoder-path',type=Path,required=True)
    a=p.parse_args();sys.path.insert(0,str(a.decoder_path));import texture2ddecoder as backend
    if backend.__version__!='1.0.6':raise ValueError('requires texture2ddecoder 1.0.6')
    data=a.source.read_bytes();digest=hashlib.sha256(data).hexdigest()
    if digest!=a.expect_sha256:raise ValueError('source hash mismatch')
    rgba,info=decode(data,backend);png=png_rgba(rgba,info['width'],info['height']);out=private_destination(a.out);out.mkdir(parents=True)
    (out/'texture.png').write_bytes(png);(out/'texture.rgba8').write_bytes(rgba)
    report=dict(source_sha256=digest,png_sha256=hashlib.sha256(png).hexdigest(),rgba_sha256=hashlib.sha256(rgba).hexdigest(),width=info['width'],height=info['height'],alpha_distinct_values=len(set(rgba[3::4])),backend_version=backend.__version__,native_row_order=True,in_game_orientation_verified=False,material_association_verified=False,source_unchanged=hashlib.sha256(a.source.read_bytes()).hexdigest()==digest)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))

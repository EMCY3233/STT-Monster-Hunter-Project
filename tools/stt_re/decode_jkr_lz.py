"""Bounded JKR type-3 sample decoder; private derived output, never game execution.

LZ algorithm adapted from ReFrontier/Jpk/JPKDecodeLz.cs, blob
469390222071858749a42556b12809820123718f (Houmgaor/ReFrontier).

MIT License
Copyright (c) 2020 mhvuze
Copyright (c) 2024 Houmgaor
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import time

LIMIT=64*1024*1024

def decode_payload(data,size):
    if not 0<size<=LIMIT: raise ValueError('output budget exceeded')
    at=0; bits_left=0; flag=0; out=bytearray(); cases=Counter()
    def byte():
        nonlocal at
        if at>=len(data): raise ValueError('truncated compressed stream')
        value=data[at]; at+=1; return value
    def bit():
        nonlocal bits_left,flag
        if bits_left==0: flag=byte(); bits_left=8
        bits_left-=1
        return (flag>>bits_left)&1
    def room(n):
        if len(out)+n>size: raise ValueError('operation exceeds declared output')
    def copy(offset,n):
        room(n)
        if offset>=len(out): raise ValueError('backreference before output start')
        for _ in range(n): out.append(out[-offset-1])
    while len(out)<size:
        if not bit():
            room(1); out.append(byte()); cases['literal']+=1; continue
        if not bit():
            length=(bit()<<1)|bit(); offset=byte()
            copy(offset,length+3); cases['short']+=1; continue
        hi=byte(); lo=byte(); length=hi>>5; offset=((hi&31)<<8)|lo
        if length:
            copy(offset,length+2); cases['medium']+=1; continue
        if not bit():
            length=0
            for _ in range(4): length=(length<<1)|bit()
            copy(offset,length+10); cases['long_a']+=1; continue
        extra=byte()
        if extra==255:
            room(offset+27)
            for _ in range(offset+27): out.append(byte())
            cases['raw_block']+=1
        else:
            copy(offset,extra+26); cases['long_b']+=1
    return bytes(out),dict(consumed_payload_bytes=at,trailing_payload_bytes=len(data)-at,unused_control_bits=bits_left,termination='declared output size reached; no end marker asserted',operations=dict(cases))

def decode_container(data):
    if len(data)>LIMIT or len(data)<16 or data[:4]!=b'JKR\x1a': raise ValueError('invalid/oversized JKR input')
    version,codec,start,size=struct.unpack_from('<HHII',data,4)
    if version!=0x108 or codec!=3 or not 16<=start<=len(data): raise ValueError('unsupported JKR header')
    output,receipt=decode_payload(data[start:],size)
    return output,dict(version=version,codec=codec,data_offset=start,declared_output_bytes=size,actual_output_bytes=len(output),**receipt)

def classify(data):
    known={b'\x7fELF':'ELF_signature',b'SCE\0':'SCE_signature',b'JKR\x1a':'JKR_signature',b'ecd\x1a':'ECD_signature',b'MOMO':'MOMO_signature',b'DDS ':'DDS_signature',b'RIFF':'RIFF_signature',b'\x89PNG':'PNG_signature'}
    if data[:4] in known: return dict(signature=known[data[:4]])
    if len(data)>=4:
        count=struct.unpack_from('<I',data)[0]
        if 0<count<=10000 and 4+count*8<=len(data):
            spans=[struct.unpack_from('<II',data,4+i*8) for i in range(count)]
            nonempty=sorted((at,at+size) for at,size in spans if size)
            valid=all(at>=4+count*8 and end<=len(data) for at,end in nonempty)
            valid=valid and all(a[1]<=b[0] for a,b in zip(nonempty,nonempty[1:]))
            if valid and nonempty: return dict(signature='headerless_offset_size_table_candidate',entry_count=count,nonempty_entries=len(nonempty),bounds_valid=True)
    return dict(signature='unclassified',semantics_verified=False)

def select_candidate(rows,excluded=None,max_declared=LIMIT):
    if not 0<max_declared<=LIMIT: raise ValueError('selection budget outside decoder limit')
    eligible=[r for r in rows if r.get('kind')=='JKR' and r.get('version')==0x108 and r.get('codec')==3 and r.get('sha256')!=excluded and 0<r['declared_output_bytes']<=max_declared]
    if not eligible: raise ValueError('no verified JKR within selection budget')
    return min(eligible,key=lambda r:(r['declared_output_bytes'],r['path']))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--candidates',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--exclude-sha256')
    p.add_argument('--max-declared',type=int,default=LIMIT)
    a=p.parse_args(); root=a.root.resolve(strict=True); out=a.out.resolve()
    if out.is_relative_to(root) or any((q/'.git').exists() for q in (out,*out.parents)): raise ValueError('derived output must stay outside sources and Git')
    candidates=json.loads(a.candidates.read_text())['rows']
    row=select_candidate(candidates,a.exclude_sha256,a.max_declared)
    source=(root/row['path']).resolve(strict=True)
    if not source.is_relative_to(root) or source.stat().st_size>LIMIT: raise ValueError('input outside root/budget')
    original=source.read_bytes(); digest=hashlib.sha256(original).hexdigest()
    if digest!=row['sha256'] or len(original)!=row['bytes']: raise ValueError('source differs from census')
    out.mkdir(parents=True,exist_ok=False)
    (out/'source.jkr').write_bytes(original)
    started=time.monotonic(); decoded,details=decode_container((out/'source.jkr').read_bytes())
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest: raise ValueError('source changed during decode')
    (out/'decoded.bin').write_bytes(decoded)
    report=dict(source_path=row['path'],source_bytes=len(original),source_sha256=digest,source_unchanged=True,output_sha256=hashlib.sha256(decoded).hexdigest(),seconds=time.monotonic()-started,classification=classify(decoded),selection_excluded_sha256=a.exclude_sha256,selection_max_declared_bytes=a.max_declared,**details)
    (out/'receipt.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

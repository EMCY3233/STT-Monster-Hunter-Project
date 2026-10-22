"""Verify portable C visual datagrams with the independent Python decoder."""
from pathlib import Path
import struct
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stt_monitor.visual_protocol import Assembler, png_rgb565
raw=Path(sys.argv[1]).read_bytes();packets=[];offset=0
while offset<len(raw):
    n=struct.unpack_from('!H',raw,offset)[0];offset+=2
    packets.append(raw[offset:offset+n]);offset+=n
assert offset==len(raw)
a=Assembler();result=None
for packet in reversed(packets): result=a.feed(packet,'127.0.0.1',0)
stream,frame,meta,pixels=result
gpu=len(sys.argv)>3 and sys.argv[3]=="gpu"
assert (stream,frame)==(0x1234,1 if gpu else 0)
assert meta['scene']['source']=='simulator'
if gpu:
    assert meta['version']==2 and meta['scene']['tick']==42
    assert meta['scene']['camera']['right_ppm']==[1000000,0,0]
else:
    assert meta['version']==1
assert pixels[:2]==b'\x00\xf8' and pixels[240:242]==b'\xe0\x07'
Path(sys.argv[2]).write_bytes(png_rgb565(pixels))
print('PASS: C -> Python image and STT/3 scene, synthetic source, RGB565 channels')

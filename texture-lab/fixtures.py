"""Original checkerboard fixture; never imports external game resources."""
from pathlib import Path
import struct
import sys
p=Path(sys.argv[1]);p.mkdir(parents=True,exist_ok=True)
rgba=bytes(c for y in range(8) for x in range(8) for c in ((255,255,255,255) if (x+y)%2 else (40,80,120,255)))
header=b'STTTEX01'+struct.pack('<4I',1,1,8,8)+rgba
mesh=struct.pack('<5I',0,3,3,0,1)
vertices=struct.pack('<15f',-1,0,4,0,0,1,0,4,1,0,0,1,4,.5,1)
raw=header+mesh+vertices+struct.pack('<3H',0,1,2)
(p/'valid.bin').write_bytes(raw)
bad={'truncated':raw[:-1],'trailing':raw+b'x','count':raw[:8]+struct.pack('<I',97)+raw[12:],
     'index':raw[:-2]+struct.pack('<H',3),
     'nonfinite':header+mesh+struct.pack('<f',float('nan'))+vertices[4:]+raw[-6:],
     'uv':header+mesh+vertices[:12]+struct.pack('<f',float('inf'))+vertices[16:]+raw[-6:],
     'dimension':raw[:16]+struct.pack('<I',513)+raw[20:]}
for name,data in bad.items():(p/(name+'.bin')).write_bytes(data)

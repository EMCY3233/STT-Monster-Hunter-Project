"""Generate original synthetic streams; no game resources required by CI."""
from pathlib import Path
import struct,sys
folder=Path(sys.argv[1]);folder.mkdir(exist_ok=True,parents=True)
vertices=[(-4,0,-4),(4,0,-4),(4,0,4),(-4,0,4)];faces=[(0,2,1),(0,3,2)]
body=[(-.15,.1,0),(.15,.1,0),(0,1.7,0)]
blob=b'STTZONE1'+struct.pack('<7I3f',4,2,3,1,16,2,0,0,0,0)
blob+=b''.join(struct.pack('<3fI',*p,0xff668855)for p in vertices)+struct.pack('<6H',0,2,1,0,3,2)
blob+=b''.join(struct.pack('<3f',*p)for _ in range(16)for p in body)+struct.pack('<3I3H',0xff55aacc,0xff55aacc,0xff55aacc,0,1,2)
for face in faces:blob+=struct.pack('<12f',*(v for i in face for v in vertices[i]),0,1,0)
(folder/'synthetic.bin').write_bytes(blob)
(folder/'truncated.bin').write_bytes(blob[:-1])
invalid=bytearray(blob);struct.pack_into('<I',invalid,8,0xffffffff);(folder/'bad-count.bin').write_bytes(invalid)
invalid=bytearray(blob);struct.pack_into('<f',invalid,48,float('nan'));(folder/'nonfinite.bin').write_bytes(invalid)
invalid=bytearray(blob);struct.pack_into('<H',invalid,112,65535);(folder/'bad-index.bin').write_bytes(invalid)

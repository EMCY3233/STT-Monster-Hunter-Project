"""Inspect GPU lab package; no commercial scene is allowed inside the VPK."""
from pathlib import Path
import hashlib
import importlib.util
import sys
import zipfile
spec=importlib.util.spec_from_file_location('old_inspect',Path(__file__).parents[1]/'vita-prototype/tests/inspect_package.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
p=Path(sys.argv[1]);vpk=p/'stt_vita_prototype.vpk'
assert hashlib.sha256(vpk.read_bytes()).hexdigest()==(p/'SHA256SUMS').read_text().split()[0]
with zipfile.ZipFile(vpk) as z:
 assert len(z.namelist())==2 and set(z.namelist())=={'eboot.bin','sce_sys/param.sfo'}
 assert z.read('eboot.bin').startswith(b'SCE\0')
 assert sum(i.file_size for i in z.infolist())<4*1024*1024
 s=module.sfo_strings(z.read('sce_sys/param.sfo'))
 assert s['TITLE_ID']=='STTP00001' and s['TITLE']=='STT Vita Prototype' and s['APP_VER']=='00.24'
print('PASS GPU VPK identity, hash and no embedded scene resources')

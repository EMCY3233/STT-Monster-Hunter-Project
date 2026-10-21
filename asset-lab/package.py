"""Build deterministic source executable ZIP; Python 3.11+ and Tk supplied by host."""
import hashlib
from pathlib import Path
import zipfile

root = Path(__file__).parent
out = root/'dist'; out.mkdir(exist_ok=True)
path = out/'stt-asset-lab-0.1.zip'
files = [*sorted((root/'stt_asset_lab').glob('*.py')),
         root/'samples/practice-dummy.stt.json', root/'generate_sample.py', root/'README.md']
with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_STORED) as archive:
    for source in files:
        info=zipfile.ZipInfo('stt-asset-lab/'+source.relative_to(root).as_posix(),(2026,10,21,0,0,0))
        info.external_attr=0o100644 << 16
        archive.writestr(info,source.read_bytes())
(out/'SHA256SUMS').write_text(hashlib.sha256(path.read_bytes()).hexdigest()+'  '+path.name+'\n')
print((out/'SHA256SUMS').read_text(),end='')

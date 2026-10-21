"""Run preserved Citra with an isolated portable profile and bounded lifetime."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--input',type=Path)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--install',action='store_true')
    a=p.parse_args()
    exe=a.exe.resolve(); out=a.out.resolve()
    out.mkdir(parents=True,exist_ok=False)
    user=exe.parent/'user'
    if user.exists() and any(user.iterdir()): raise ValueError('profile must be fresh')
    user.mkdir(exist_ok=True)
    before=sha(a.input) if a.input else None
    args=[str(exe)]+(['--install',str(a.input.resolve())] if a.install else [str(a.input.resolve())]) if a.input else [str(exe),'--help']
    info=subprocess.STARTUPINFO(); info.dwFlags|=subprocess.STARTF_USESHOWWINDOW; info.wShowWindow=0
    started=time.monotonic(); timed_out=False
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
        child=subprocess.Popen(args,cwd=exe.parent,stdout=stdout,stderr=stderr,startupinfo=info)
        try: child.wait(timeout=15)
        except subprocess.TimeoutExpired:
            timed_out=True; child.terminate(); child.wait(timeout=10)
    after=sha(a.input) if a.input else None
    receipt=dict(executable_sha256=sha(exe),input=str(a.input) if a.input else None,input_sha256=before,input_unchanged=before==after,returncode=child.returncode,terminated_after_timeout=timed_out,elapsed_seconds=time.monotonic()-started,profile=str(user),logs=[dict(path=str(x.relative_to(user)),bytes=x.stat().st_size,sha256=sha(x)) for x in user.rglob('*') if x.is_file()])
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))

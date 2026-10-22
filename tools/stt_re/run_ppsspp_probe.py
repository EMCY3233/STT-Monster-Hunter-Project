"""Bounded PPSSPP portable boot probe. No console/FTP, firmware install or game export."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while b:=f.read(8*1024*1024): h.update(b)
    return h.hexdigest()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--exe',type=Path,required=True)
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--seconds',type=int,default=20)
    p.add_argument('--dump-eboot',action='store_true',help='Enable emulator-supported local EBOOT dump, never publish it')
    a=p.parse_args()
    if not 1<=a.seconds<=45: p.error('probe duration must be 1..45 seconds')
    exe=a.exe.resolve(strict=True)
    iso=a.iso.resolve(strict=True)
    out=a.out.resolve()
    if (exe.parent/'installed.txt').exists(): raise ValueError('requires portable executable without installed.txt')
    if a.dump_eboot and any((q/'.git').exists() for q in (exe.parent,*exe.parent.parents)):
        raise ValueError('commercial executable dump must stay outside Git')
    out.mkdir(parents=True,exist_ok=False)
    config=exe.parent/'memstick/PSP/SYSTEM'
    config.mkdir(parents=True,exist_ok=True)
    if a.dump_eboot and (config/'DUMP').exists() and any((config/'DUMP').iterdir()):
        raise ValueError('existing dump directory is not empty; use a fresh isolated portable copy')
    own_config='[General]\nFirstRun=False\nAutoRun=True\nCheckForNewVersion=False\nEnable Logging=True\n[Network]\nEnableWlan=False\nEnableAdhocServer=False\n[Sound]\nEnable=False\n'
    config_path=config/'ppsspp.ini'
    if config_path.exists():
        if config_path.read_text(encoding='utf-8')!=own_config: raise ValueError('existing configuration is not this probe configuration')
    else:
        with config_path.open('x',encoding='utf-8') as f: f.write(own_config)
    override=out/'probe.ini'
    override.write_text('[General]\nDumpFileTypes='+('1' if a.dump_eboot else '0')+'\nLoadPlugins=False\n',encoding='utf-8')
    before=digest(iso)
    log=out/'ppsspp.log'
    args=[str(exe),'-d','--log='+str(log),'--appendconfig='+str(override),'-direct3d11',str(iso)]
    info=subprocess.STARTUPINFO()
    info.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow=0
    start=time.monotonic()
    reason='process_exited'
    with (out/'stdout.txt').open('wb') as stdout,(out/'stderr.txt').open('wb') as stderr:
        child=subprocess.Popen(args,cwd=exe.parent,stdout=stdout,stderr=stderr,startupinfo=info)
        try: code=child.wait(timeout=a.seconds)
        except subprocess.TimeoutExpired:
            reason='bounded_probe_terminated'
            child.terminate()
            code=child.wait(timeout=10)
    elapsed=time.monotonic()-start
    after=digest(iso)
    result=dict(generated_utc=datetime.now(timezone.utc).isoformat(),emulator_sha256=digest(exe),
                iso_sha256_before=before,iso_sha256_after=after,source_unchanged=before==after,
                seconds=elapsed,exit_code=code,stop_reason=reason,log_exists=log.exists(),
                logs=[dict(name=q.name,bytes=q.stat().st_size,sha256=digest(q)) for q in out.iterdir() if q.is_file()],
                scope='Bounded hidden portable process; game progress must be established from logs, not elapsed runtime.',
                headless=False,visual_validation=False,dump_eboot_requested=a.dump_eboot,
                dumps=[dict(path=q.relative_to(exe.parent).as_posix(),bytes=q.stat().st_size,sha256=digest(q)) for q in (config/'DUMP').rglob('*') if q.is_file()])
    (out/'receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))

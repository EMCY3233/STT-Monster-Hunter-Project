"""Corroborate one static PSP section mapping using two existing loader logs.

No emulator launch, memory inspection, code execution or function attribution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

PATTERN=re.compile(r'Data Section found:\s+(\S+)\s+Sitting at ([0-9a-fA-F]{8}), size ([0-9a-fA-F]{8})')

def announcements(text,expected):
    rows=[]
    for number,line in enumerate(text.splitlines(),1):
        match=PATTERN.search(line)
        if not match: continue
        name,va,size=match.groups(); va=int(va,16); size=int(size,16)
        if name in expected and (va,size)==expected[name]: rows.append(dict(line_number=number,section=name,vaddr=va,bytes=size))
    return rows

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); root=a.root.resolve(strict=True)
    static_path=root/'analysis-local/psp-import-reference-20261021.json'
    public=json.loads((root/'research-work/docs/research/stt-re-20261021/mhfu-import-reference-evidence.json').read_text())
    if sha(static_path)!=public['receipt_sha256']: raise ValueError('static receipt mismatch')
    static=json.loads(static_path.read_text()); baseline_path=root/'analysis-local/frontier-local-inspection-20261021/mhfu-elf-sections.json'
    if sha(baseline_path)!=static['baseline_receipt_sha256']: raise ValueError('baseline receipt mismatch')
    baseline=json.loads(baseline_path.read_text())
    source=static['source_section']; target=next(s for s in baseline['sections'] if s['index']==static['reference']['target_section_index'])
    expected={source['name']:(source['address'],source['bytes']),target['name']:(target['address'],target['bytes'])}
    exe=root/'analysis-local/emulators/ppsspp-1.20.4/PPSSPPWindows64.exe'; emulator_sha=sha(exe); runs=[]
    for label in ('ppsspp-probe-20261021','ppsspp-decrypt-20261021'):
        folder=root/'analysis-local'/label; receipt_path=folder/'receipt.json'; receipt=json.loads(receipt_path.read_text())
        log=folder/'ppsspp.log'; expected_log=next(r for r in receipt['logs'] if r['name']=='ppsspp.log')
        if sha(log)!=expected_log['sha256'] or log.stat().st_size!=expected_log['bytes'] or emulator_sha!=receipt['emulator_sha256']: raise ValueError('historical log/executable mismatch')
        rows=announcements(log.read_text(encoding='utf-8',errors='strict'),expected)
        runs.append(dict(label=label,receipt_sha256=sha(receipt_path),log_sha256=expected_log['sha256'],log_bytes=expected_log['bytes'],announcements=rows,both_section_announcements_match=all(any(r['section']==name for r in rows) for name in expected),historical_iso_sha256_before=receipt['iso_sha256_before'],historical_iso_sha256_after=receipt['iso_sha256_after'],historical_source_unchanged=receipt['source_unchanged'],historical_stop_reason=receipt['stop_reason']))
    report=dict(emulator_version='1.20.4',emulator_sha256=emulator_sha,static_receipt_sha256=sha(static_path),new_emulator_runs=0,new_dumps=0,existing_runs_reused=2,runs=runs,runtime_section_announcement_corroborated=all(r['both_section_announcements_match'] for r in runs),runtime_pointer_dereference_confirmed=False,function_identity_verified=False,function_invocation_verified=False,visual_validation=False,fps=None,acceptance='section address/size corroboration only; concrete pointer dereference remains unproved')
    with a.out.open('x',encoding='utf-8') as f: f.write(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))

"""Read-only audit; no extraction, decryption, mounts, network, or game execution."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import struct
from probe_arc import parse_table, decode_entry, classify
from probe_resource_headers import probe_mod230, probe_lmt67
from inventory_games import iso_record

def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while b := f.read(8 * 1024 * 1024):
            h.update(b)
    return h.hexdigest()

def iso_entries(path):
    result = []
    with path.open('rb') as f:
        size = path.stat().st_size
        f.seek(32768)
        pvd = f.read(2048)
        if pvd[:7] != b'\x01CD001\x01':
            raise ValueError('not ISO9660')
        todo = [('', iso_record(pvd[156:156+pvd[156]]))]
        seen = set()
        while todo:
            prefix, (ex, ln, _, _) = todo.pop()
            if ex in seen:
                continue
            seen.add(ex)
            if len(seen) > 2048 or ln > 8*1024*1024 or ex*2048+ln > size:
                raise ValueError('directory bounds')
            f.seek(ex*2048)
            data = f.read(ln)
            pos = 0
            while pos < len(data):
                n = data[pos]
                if not n:
                    pos = (pos//2048+1)*2048
                    continue
                if n < 34 or pos+n > len(data):
                    raise ValueError('record bounds')
                rec = iso_record(data[pos:pos+n])
                pos += n
                extent, length, isdir, name = rec
                if name in (b'\x00', b'\x01'):
                    continue
                name = prefix+name.decode('ascii', 'replace').split(';')[0]
                if extent*2048+length > size:
                    raise ValueError('file bounds')
                if isdir:
                    todo.append((name+'/', rec))
                    continue
                f.seek(extent*2048)
                remaining, h, head = length, hashlib.sha256(), b''
                while remaining:
                    b = f.read(min(8*1024*1024, remaining))
                    if not b:
                        raise ValueError('truncated file')
                    if not head:
                        head = b[:16]
                    h.update(b)
                    remaining -= len(b)
                result.append(dict(path=name, bytes=length, offset=extent*2048,
                                   sha256=h.hexdigest(), header_hex=head.hex(),
                                   excluded_from_asset_study='/UPDATE/' in name))
    return result

def main(root, out):
    out.mkdir(parents=True, exist_ok=False)
    records, excluded = [], []
    for base, dirs, names in os.walk(root, followlinks=False):
        kept = []
        for name in sorted(dirs):
            p = Path(base)/name
            if name == '.git' or p.is_symlink() or p.resolve() == out.resolve():
                excluded.append(p.relative_to(root).as_posix())
            else:
                kept.append(name)
        dirs[:] = kept
        for name in sorted(names):
            p = Path(base)/name
            rel = p.relative_to(root).as_posix()
            r = dict(path=rel)
            try:
                if p.is_symlink():
                    raise ValueError('symlink skipped')
                before = p.stat()
                r.update(bytes=before.st_size, sha256=digest_file(p))
                with p.open('rb') as f:
                    head = f.read(512)
                r['signature'] = ('ARC' if head[:4] == b'ARC\0' else
                                  'CRO0_at_0x80' if head[128:132] == b'CRO0' else
                                  'NCCH_at_0x100' if head[256:260] == b'NCCH' else
                                  'ELF' if head[:4] == b'\x7fELF' else
                                  'PSP_wrapped' if head[:4] == b'~PSP' else 'unclassified')
                after = p.stat()
                r['status'] = 'read_ok' if (before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns) else 'changed_during_read'
            except (OSError, ValueError) as e:
                r.update(status='failed', error=str(e))
            records.append(r)
    (out/'physical-files.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records),encoding='utf-8')
    arc_counts, signatures, resources, errors = Counter(), Counter(), [], []
    bank = root/'analysis-local/resource-bank/catalog.sqlite'
    db = sqlite3.connect(bank.as_uri()+'?mode=ro',uri=True)
    bank_errors = []
    for p in sorted((root/'analysis-local/romfs').rglob('*.arc')):
        try:
            data = p.read_bytes()
            rel = p.relative_to(root/'analysis-local/romfs').as_posix()
            file_id = db.execute("SELECT id FROM files WHERE root_label='romfs' AND relative_path=?",(rel,)).fetchone()
            if not file_id:
                raise ValueError('missing bank source')
            for entry in parse_table(data):
                output = decode_entry(data,entry)
                sha = hashlib.sha256(output).hexdigest()
                kind = classify(output)
                signatures[kind] += 1
                arc_counts['entries'] += 1
                old = db.execute('SELECT sha256 FROM entries WHERE file_id=? AND entry_index=?',(file_id[0],entry['index'])).fetchone()
                if not old or old[0] != sha:
                    bank_errors.append(dict(container=rel,index=entry['index']))
                if kind in ('MOD_candidate','LMT_candidate'):
                    r = dict(container=rel,index=entry['index'],internal_path=entry['path'],bytes=len(output),sha256=sha,kind=kind)
                    try:
                        r['header_probe'] = probe_mod230(output) if kind=='MOD_candidate' else probe_lmt67(output)
                    except (ValueError,struct.error) as e:
                        r['probe_error'] = str(e)
                    resources.append(r)
            arc_counts['archives'] += 1
        except (OSError,ValueError) as e:
            errors.append(dict(path=str(p.relative_to(root)),error=str(e)))
    objects_checked = 0
    for sha, length, rel in db.execute('SELECT sha256,bytes,relative_path FROM objects'):
        p = bank.parent/rel
        if not p.exists() or p.stat().st_size != length or digest_file(p) != sha:
            bank_errors.append(dict(object=sha,error='missing/size/hash mismatch'))
        objects_checked += 1
    integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
    db.close()
    (out/'resource-headers.json').write_text(json.dumps(resources,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    iso = iso_entries(root/'Juegos/MHFU/Monster Hunter Freedom Unite.iso')
    (out/'psp-files.json').write_text(json.dumps(iso,indent=2)+'\n',encoding='utf-8')
    baseline = json.loads((root/'inventory-work/docs/research/game-inputs-2026-10-21/inventory.json').read_text(encoding='utf-8'))
    lookup = {r['path']:r for r in records}
    originals = [dict(path=r['path'],bytes=r['bytes'],sha256=lookup['Juegos/'+r['path']].get('sha256'),matches_baseline=lookup['Juegos/'+r['path']].get('sha256')==r['sha256']) for r in baseline['records']]
    summary = dict(generated_utc=datetime.now(timezone.utc).isoformat(),scope='All physical project files except .git, links and this output; hash/read only. ARC decoding only plain v17 RomFS. No semantic asset validation.',
                   files=len(records),bytes=sum(r.get('bytes',0) for r in records),status=dict(Counter(r['status'] for r in records)),excluded=excluded,
                   originals=originals,arc=dict(arc_counts),entry_signatures=dict(signatures),arc_errors=errors,
                   bank_hash_errors=bank_errors,bank_objects_checked=objects_checked,sqlite_integrity=integrity,psp_files=len(iso))
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    if errors or bank_errors or any(r['status']!='read_ok' for r in records) or not all(r['matches_baseline'] for r in originals):
        raise SystemExit(1)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    main(args.root.resolve(),args.out.resolve())

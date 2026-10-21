"""Link a receipt-verified local derivative by metadata; never copies game bytes.

SQLite stays read-only. The append-only sidecar is separate from the historical
file and ARC catalogs, whose counts and hashes therefore stay unchanged.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def link(bank, project, source_relative, output, evidence, evidence_sha):
    bank, project, output, evidence = [Path(p).resolve() for p in (bank, project, output, evidence)]
    source = (project / 'Juegos' / source_relative).resolve()
    for path in (source, output, evidence, bank):
        if project not in path.parents:
            raise ValueError('paths must remain inside project')
    if any((p / '.git').exists() for p in [bank, *bank.parents]):
        raise ValueError('bank cannot be in Git')
    if not re.fullmatch('[0-9a-f]{64}', evidence_sha) or digest(evidence) != evidence_sha:
        raise ValueError('evidence hash mismatch')
    proof = json.loads(evidence.read_text(encoding='utf-8'))
    if proof.get('source_unchanged') is not True:
        raise ValueError('receipt did not verify source preservation')
    source_sha, output_sha = digest(source), digest(output)
    if source_sha != proof['source_sha256'] or output_sha != proof['output_sha256']:
        raise ValueError('source or derivative differs from receipt')
    if source.stat().st_size != proof['source_bytes'] or output.stat().st_size != proof['actual_output_bytes']:
        raise ValueError('size differs from receipt')
    db = sqlite3.connect((bank / 'catalog.sqlite').as_uri() + '?mode=ro', uri=True)
    try:
        row = db.execute('SELECT id,bytes,sha256 FROM files WHERE root_label=? AND relative_path=?',
                         ('originals', source_relative)).fetchone()
    finally:
        db.close()
    if row is None or row[1:] != (source.stat().st_size, source_sha):
        raise ValueError('source not matched to catalog')
    record = {'schema_version': 1, 'source_file_id': row[0], 'source_relative_path': source_relative,
              'source_sha256': source_sha, 'output_relative_path': output.relative_to(project).as_posix(),
              'output_sha256': output_sha, 'output_bytes': output.stat().st_size,
              'evidence_relative_path': evidence.relative_to(project).as_posix(), 'evidence_sha256': evidence_sha,
              'classification': proof.get('classification', {'signature': 'unclassified', 'semantics_verified': False}),
              'method': 'Receipt-linked local derivative; transformation is described by receipt and not reproduced here.'}
    record['id'] = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    ledger = bank / 'derivatives.jsonl'
    if ledger.is_symlink():
        raise ValueError('sidecar cannot be a link')
    if ledger.exists():
        for line in ledger.read_text(encoding='utf-8').splitlines():
            if json.loads(line)['id'] == record['id']:
                return {'status': 'already_linked', 'record': record}
    with ledger.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + '\n')
    return {'status': 'linked', 'record': record}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--source-relative', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--evidence-sha256', required=True)
    args = parser.parse_args()
    print(json.dumps(link(args.bank, args.project, args.source_relative, args.output, args.evidence, args.evidence_sha256)))

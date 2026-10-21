"""Read-only consistency and duplicate audit of catalog metadata, not file bytes."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import sqlite3


def audit(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        files = [dict(r) for r in db.execute('SELECT id,root_label,relative_path,bytes,sha256,status,source_unchanged FROM files')]
        entries = [dict(r) for r in db.execute('SELECT file_id,entry_index,declared_bytes,sha256,status FROM entries')]
        objects = {r['sha256']: dict(r) for r in db.execute('SELECT sha256,bytes,relative_path FROM objects')}
        groups = defaultdict(list)
        file_ids = {r['id'] for r in files}
        errors = []
        for row in files:
            if not row['sha256'] or row['status'] != 'hashed' or row['source_unchanged'] != 1:
                errors.append({'kind': 'file_not_verified', 'file_id': row['id']})
            else:
                groups[row['sha256']].append(row)
        entry_hashes = set()
        for row in entries:
            label = {'file_id': row['file_id'], 'entry_index': row['entry_index']}
            if row['file_id'] not in file_ids:
                errors.append({'kind': 'missing_source_file', **label})
            obj = objects.get(row['sha256'])
            if row['status'] != 'decoded_and_hash_verified' or obj is None:
                errors.append({'kind': 'missing_or_unverified_object', **label})
            elif obj['bytes'] != row['declared_bytes']:
                errors.append({'kind': 'entry_object_size_mismatch', **label})
            entry_hashes.add(row['sha256'])
        for digest, rows in groups.items():
            sizes = {r['bytes'] for r in rows}
            if len(sizes) != 1 or (digest in objects and objects[digest]['bytes'] not in sizes):
                errors.append({'kind': 'same_hash_inconsistent_sizes', 'sha256': digest})
        duplicates = [rows for rows in groups.values() if len(rows) > 1]
        repeated_bytes = sum(rows[0]['bytes'] * (len(rows) - 1) for rows in duplicates)
        samples = []
        for rows in sorted(duplicates, key=lambda r: r[0]['bytes'] * (len(r) - 1), reverse=True)[:12]:
            samples.append({'sha256': rows[0]['sha256'], 'bytes_each': rows[0]['bytes'],
                            'occurrences': len(rows),
                            'locations': [{'root_label': r['root_label'], 'path': r['relative_path']} for r in rows]})
        return {'scope': 'Metadata consistency only; no rehash of source or object bytes, deletion, repacking or semantic equivalence inference.',
                'sqlite_integrity_check': db.execute('PRAGMA integrity_check').fetchone()[0],
                'physical_files': len(files), 'physical_bytes_in_catalog': sum(r['bytes'] or 0 for r in files),
                'unique_physical_hashes': len(groups), 'physical_duplicate_hash_groups': len(duplicates),
                'physical_repeated_occurrences': sum(len(r) - 1 for r in duplicates),
                'physical_repeated_bytes': repeated_bytes,
                'entries': len(entries), 'object_records': len(objects),
                'unreferenced_object_records': len(set(objects) - entry_hashes),
                'physical_hashes_also_present_as_objects': len(set(groups) & set(objects)),
                'combined_unique_hashes': len(set(groups) | set(objects)),
                'duplicate_samples': samples, 'errors': errors,
                'byte_identity_basis': 'Previously recorded SHA-256 and sizes; no license, provenance or gameplay equivalence established.'}
    finally:
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if args.catalog.resolve() == args.report.resolve():
        parser.error('report cannot replace catalog')
    result = audit(args.catalog)
    with args.report.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'duplicate_samples'}))
    if result['errors'] or result['sqlite_integrity_check'] != 'ok':
        raise SystemExit(1)

"""Local content-addressed game-file bank. Never modifies input files.

Catalogs every regular file under explicit roots, hashes full contents, and
decodes supported ARC17 entries. Internal names are metadata, never disk paths.
No game execution, key handling, external downloads or uploads.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import zlib

from probe_arc import parse_table, decode_entry, classify, MAX_ARCHIVE


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def identify(head, suffix):
    for magic, name in [(b'ARC\0', 'ARC'), (b'MOD\0', 'MOD'),
                        (b'LMT\0', 'LMT'), (b'TEX\0', 'TEX'),
                        (b'GMD\0', 'GMD'), (b'MRL\0', 'MRL'),
                        (b'\x7fELF', 'ELF'), (b'~PSP', 'PSP_wrapper'),
                        (b'7z\xbc\xaf\x27\x1c', '7z')]:
        if head.startswith(magic):
            return name + '_signature'
    return 'extension_only:' + (suffix.lower() or '(none)')


def put_blob(bank, payload):
    digest = hashlib.sha256(payload).hexdigest()
    path = bank / 'objects' / digest[:2] / digest
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if hash_file(path) != digest:
            raise ValueError('existing bank object hash mismatch')
    else:
        with path.open('xb') as stream:
            stream.write(payload)
        if hash_file(path) != digest:
            raise ValueError('written bank object hash mismatch')
    return digest


def build(roots, bank):
    bank = bank.resolve()
    if any((p / '.git').exists() for p in [bank, *bank.parents]):
        raise ValueError('bank must be outside Git checkouts')
    roots = [(label, path.resolve()) for label, path in roots]
    if len({label for label, _ in roots}) != len(roots):
        raise ValueError('root labels must be unique')
    for _, root in roots:
        if not root.is_dir() or bank == root or root in bank.parents or bank in root.parents:
            raise ValueError('source roots must exist and be separate from bank')
    bank.mkdir(parents=True, exist_ok=False)
    db = sqlite3.connect(bank / 'catalog.sqlite')
    db.executescript('''
    CREATE TABLE files(id INTEGER PRIMARY KEY, root_label TEXT, relative_path TEXT,
      bytes INTEGER, sha256 TEXT, format_observed TEXT, mtime_ns INTEGER,
      source_unchanged INTEGER, status TEXT, error TEXT,
      UNIQUE(root_label, relative_path));
    CREATE TABLE entries(file_id INTEGER, entry_index INTEGER, internal_path TEXT,
      type_id TEXT, compressed_bytes INTEGER, declared_bytes INTEGER, offset INTEGER,
      flags INTEGER, sha256 TEXT, signature_candidate TEXT, status TEXT, error TEXT,
      PRIMARY KEY(file_id, entry_index));
    CREATE TABLE objects(sha256 TEXT PRIMARY KEY, bytes INTEGER, relative_path TEXT);
    CREATE INDEX file_hash ON files(sha256);
    CREATE INDEX entry_hash ON entries(sha256);
    CREATE INDEX entry_path ON entries(internal_path);
    ''')
    formats, failures = Counter(), []
    for label, root in roots:
        for path in sorted(root.rglob('*')):
            if path.is_symlink():
                failures.append({'root': label, 'path': path.relative_to(root).as_posix(), 'error': 'symlink skipped'})
                continue
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            cursor = db.execute('INSERT INTO files(root_label,relative_path,status) VALUES(?,?,?)', (label, rel, 'pending'))
            file_id = cursor.lastrowid
            try:
                before = path.stat()
                digest = hash_file(path)
                with path.open('rb') as stream:
                    head = stream.read(512)
                kind = identify(head, path.suffix)
                formats[kind] += 1
                db.execute('UPDATE files SET bytes=?,sha256=?,format_observed=?,mtime_ns=? WHERE id=?',
                           (before.st_size, digest, kind, before.st_mtime_ns, file_id))
                if head.startswith(b'ARC\0'):
                    if before.st_size > MAX_ARCHIVE:
                        raise ValueError('ARC exceeds bounded decoder limit')
                    data = path.read_bytes()
                    if hashlib.sha256(data).hexdigest() != digest:
                        raise ValueError('source changed between reads')
                    for entry in parse_table(data):
                        output_sha, signature, status, error = None, None, 'failed', None
                        try:
                            output = decode_entry(data, entry)
                            output_sha = put_blob(bank, output)
                            signature = classify(output)
                            db.execute('INSERT OR IGNORE INTO objects VALUES(?,?,?)',
                                       (output_sha, len(output), 'objects/' + output_sha[:2] + '/' + output_sha))
                            status = 'decoded_and_hash_verified'
                        except (OSError, ValueError, zlib.error) as exc:
                            error = str(exc)
                        db.execute('INSERT INTO entries VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                                   (file_id, entry['index'], entry['path'], entry['type_id'],
                                    entry['compressed_bytes'], entry['declared_bytes'], entry['offset'],
                                    entry['flags'], output_sha, signature, status, error))
                after = path.stat()
                unchanged = (before.st_size == after.st_size and before.st_mtime_ns == after.st_mtime_ns
                             and hash_file(path) == digest)
                db.execute('UPDATE files SET bytes=?,sha256=?,format_observed=?,mtime_ns=?,source_unchanged=?,status=? WHERE id=?',
                           (before.st_size, digest, kind, before.st_mtime_ns, int(unchanged),
                            'hashed' if unchanged else 'changed_during_read', file_id))
            except (OSError, ValueError) as exc:
                db.execute('UPDATE files SET status=?,error=? WHERE id=?', ('failed', str(exc), file_id))
                failures.append({'root': label, 'path': rel, 'error': str(exc)})
            db.commit()
    summary = {'schema_version': 1, 'roots': [{'label': l, 'path': str(p)} for l, p in roots],
               'files': db.execute('SELECT count(*) FROM files').fetchone()[0],
               'file_status': dict(db.execute('SELECT status,count(*) FROM files GROUP BY status')),
               'entries': db.execute('SELECT count(*) FROM entries').fetchone()[0],
               'entry_status': dict(db.execute('SELECT status,count(*) FROM entries GROUP BY status')),
               'unique_objects': db.execute('SELECT count(*) FROM objects').fetchone()[0],
               'object_bytes': db.execute('SELECT coalesce(sum(bytes),0) FROM objects').fetchone()[0],
               'formats_observed': dict(formats), 'errors': failures,
               'scope': 'All physical game files under selected roots; supported ARC17 payloads only. Other containers stay cataloged, not recursively decoded.'}
    with (bank / 'catalog-files.jsonl').open('x', encoding='utf-8') as stream:
        db.row_factory = sqlite3.Row
        for row in db.execute('SELECT * FROM files ORDER BY id'):
            stream.write(json.dumps(dict(row), ensure_ascii=False) + '\n')
    with (bank / 'catalog-entries.jsonl').open('x', encoding='utf-8') as stream:
        for row in db.execute('SELECT * FROM entries ORDER BY file_id,entry_index'):
            stream.write(json.dumps(dict(row), ensure_ascii=False) + '\n')
    integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
    summary['sqlite_integrity_check'] = integrity
    db.close()
    (bank / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', action='append', required=True, help='unique-label=directory')
    parser.add_argument('--bank', type=Path, required=True, help='new directory outside Git')
    args = parser.parse_args()
    selected = [(v.split('=', 1)[0], Path(v.split('=', 1)[1])) for v in args.root]
    print(json.dumps(build(selected, args.bank), ensure_ascii=False))

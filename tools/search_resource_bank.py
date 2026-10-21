"""Search a local bank by path or SHA-256; opens SQLite in read-only mode."""
import argparse
import json
from pathlib import Path
import sqlite3


def search(bank, text, limit=50):
    if not 1 <= limit <= 1000:
        raise ValueError('limit must be between 1 and 1000')
    db = sqlite3.connect((Path(bank).resolve() / 'catalog.sqlite').as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        needle = '%' + text.replace('!', '!!').replace('%', '!%').replace('_', '!_') + '%'
        files = [dict(r) for r in db.execute("SELECT * FROM files WHERE relative_path LIKE ? ESCAPE '!' OR sha256=? ORDER BY id LIMIT ?", (needle, text, limit))]
        entries = [dict(r) for r in db.execute("SELECT e.*,f.root_label,f.relative_path AS archive_path,o.relative_path AS object_path FROM entries e JOIN files f ON f.id=e.file_id LEFT JOIN objects o ON e.sha256=o.sha256 WHERE e.internal_path LIKE ? ESCAPE '!' OR e.sha256=? ORDER BY e.file_id,e.entry_index LIMIT ?", (needle, text, limit))]
        return {'files': files, 'entries': entries, 'limit_per_category': limit}
    finally:
        db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bank', type=Path, required=True)
    parser.add_argument('text')
    parser.add_argument('--limit', type=int, default=50)
    args = parser.parse_args()
    print(json.dumps(search(args.bank, args.text, args.limit), ensure_ascii=False, indent=2))

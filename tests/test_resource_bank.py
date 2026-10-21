"""Temporary synthetic inputs only; no commercial fixtures."""
import hashlib
import os
from contextlib import closing
from pathlib import Path
import sqlite3
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
from build_resource_bank import build
from search_resource_bank import search


def temporary_directory():
    return tempfile.TemporaryDirectory(dir=os.environ.get('STT_TEST_TMP'))


def arc(payload=b'TEX\0example', corrupt=False):
    compressed = b'broken' if corrupt else zlib.compress(payload)
    return struct.pack('<4sHHI', b'ARC\0', 17, 1, 0) + struct.pack(
        '<64sIIII', b'../../outside', 1, len(compressed), len(payload), 92) + compressed


class BankTests(unittest.TestCase):
    def test_deduplicates_with_provenance_and_preserves_sources(self):
        with temporary_directory() as directory:
            base = Path(directory); source = base / 'source'; source.mkdir()
            for name in ('a.arc', 'b.arc'): (source / name).write_bytes(arc())
            before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()}
            bank = base / 'bank'; result = build([('test', source)], bank)
            self.assertEqual(result['entries'], 2)
            self.assertEqual(result['unique_objects'], 1)
            self.assertEqual(result['file_status'], {'hashed': 2})
            self.assertEqual(result['sqlite_integrity_check'], 'ok')
            self.assertEqual(before, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source.iterdir()})
            self.assertFalse((base / 'outside').exists())
            matches = search(bank, '../../outside')
            self.assertEqual(len(matches['entries']), 2)
            self.assertTrue(matches['entries'][0]['object_path'].startswith('objects/'))
            self.assertEqual(search(bank, '%')['entries'], [])
            with closing(sqlite3.connect(bank / 'catalog.sqlite')) as db:
                self.assertEqual(db.execute('SELECT count(DISTINCT file_id) FROM entries').fetchone()[0], 2)

    def test_decode_failure_retained(self):
        with temporary_directory() as directory:
            base = Path(directory); source = base / 'source'; source.mkdir()
            (source / 'bad.arc').write_bytes(arc(corrupt=True))
            result = build([('test', source)], base / 'bank')
            self.assertEqual(result['entry_status'], {'failed': 1})
            self.assertEqual(result['unique_objects'], 0)

    def test_bank_inside_source_rejected(self):
        with temporary_directory() as directory:
            source = Path(directory)
            with self.assertRaises(ValueError): build([('test', source)], source / 'bank')

    def test_bank_inside_git_rejected(self):
        from unittest.mock import patch
        with temporary_directory() as directory:
            base = Path(directory)
            source = base / 'source'; source.mkdir()
            original = Path.exists
            with patch.object(Path, 'exists', lambda p: p.name == '.git' or original(p)):
                with self.assertRaises(ValueError): build([('test', source)], base / 'bank')

    def test_existing_destination_rejected(self):
        with temporary_directory() as directory:
            base = Path(directory); source = base / 'source'; source.mkdir()
            bank = base / 'bank'; bank.mkdir()
            with self.assertRaises(FileExistsError): build([('test', source)], bank)


if __name__ == '__main__': unittest.main()

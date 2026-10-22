"""Synthetic metadata fixtures; audit must preserve SQLite bytes."""
import hashlib
import importlib.util
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bank_audit', Path(__file__).parents[1] / 'tools/audit_bank_catalog.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CatalogAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('STT_TEST_TMP'))
        self.path = Path(self.temp.name) / 'fixture.sqlite'
        db = sqlite3.connect(self.path)
        db.executescript('''
        CREATE TABLE files(id,root_label,relative_path,bytes,sha256,status,source_unchanged);
        CREATE TABLE entries(file_id,entry_index,declared_bytes,sha256,status);
        CREATE TABLE objects(sha256,bytes,relative_path);
        INSERT INTO files VALUES(1,'test','a',10,'hash','hashed',1);
        INSERT INTO files VALUES(2,'test','b',10,'hash','hashed',1);
        INSERT INTO objects VALUES('hash',10,'objects/hash');
        INSERT INTO entries VALUES(1,0,10,'hash','decoded_and_hash_verified');
        ''')
        db.commit(); db.close()

    def tearDown(self):
        self.temp.cleanup()

    def change(self, sql):
        db = sqlite3.connect(self.path)
        db.execute(sql); db.commit(); db.close()

    def test_duplicate_counts_and_no_mutation(self):
        before = hashlib.sha256(self.path.read_bytes()).hexdigest()
        result = m.audit(self.path)
        self.assertEqual(result['physical_repeated_bytes'], 10)
        self.assertEqual(result['combined_unique_hashes'], 1)
        self.assertEqual(result['errors'], [])
        self.assertEqual(before, hashlib.sha256(self.path.read_bytes()).hexdigest())

    def test_missing_object(self):
        self.change('DELETE FROM objects')
        self.assertIn('missing_or_unverified_object', [e['kind'] for e in m.audit(self.path)['errors']])

    def test_dangling_source(self):
        self.change('DELETE FROM files WHERE id=1')
        self.assertIn('missing_source_file', [e['kind'] for e in m.audit(self.path)['errors']])

    def test_size_mismatch(self):
        self.change('UPDATE objects SET bytes=11')
        self.assertIn('entry_object_size_mismatch', [e['kind'] for e in m.audit(self.path)['errors']])

    def test_failed_source_not_counted_as_verified(self):
        self.change("UPDATE files SET status='failed' WHERE id=2")
        self.assertIn('file_not_verified', [e['kind'] for e in m.audit(self.path)['errors']])


if __name__ == '__main__': unittest.main()

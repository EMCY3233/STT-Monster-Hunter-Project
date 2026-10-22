"""Synthetic metadata and bytes; no commercial fixtures."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).parents[1] / 'tools'))
from link_bank_derivative import link, digest
from search_resource_bank import search


class DerivativeLinkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get('STT_TEST_TMP'))
        self.base = Path(self.temp.name)
        self.bank = self.base / 'bank'; self.bank.mkdir()
        source = self.base / 'Juegos/a.bin'; source.parent.mkdir(); source.write_bytes(b'compressed')
        self.output = self.base / 'decoded.bin'; self.output.write_bytes(b'decoded')
        self.proof = self.base / 'proof.json'
        self.proof.write_text(json.dumps({'source_unchanged': True, 'source_bytes': 10,
            'source_sha256': digest(source), 'output_sha256': digest(self.output), 'actual_output_bytes': 7}))
        self.proof_sha = digest(self.proof)
        db = sqlite3.connect(self.bank / 'catalog.sqlite')
        db.execute('CREATE TABLE files(id,root_label,relative_path,bytes,sha256)')
        db.execute('CREATE TABLE entries(file_id,entry_index,internal_path,sha256)')
        db.execute('CREATE TABLE objects(sha256,relative_path)')
        db.execute('INSERT INTO files VALUES(1,?,?,?,?)', ('originals', 'a.bin', 10, digest(source)))
        db.commit(); db.close()

    def tearDown(self): self.temp.cleanup()

    def run_link(self):
        return link(self.bank, self.base, 'a.bin', self.output, self.proof, self.proof_sha)

    def test_link_idempotent_and_catalog_unchanged(self):
        before = digest(self.bank / 'catalog.sqlite')
        self.assertEqual(self.run_link()['status'], 'linked')
        self.assertEqual(self.run_link()['status'], 'already_linked')
        self.assertEqual(len((self.bank / 'derivatives.jsonl').read_text().splitlines()), 1)
        self.assertEqual(before, digest(self.bank / 'catalog.sqlite'))
        self.assertEqual(len(search(self.bank, 'a.bin')['derivatives']), 1)
        self.assertEqual(len(search(self.bank, digest(self.output))['derivatives']), 1)

    def test_output_tamper_refused(self):
        self.output.write_bytes(b'bad')
        with self.assertRaises(ValueError): self.run_link()

    def test_proof_tamper_refused(self):
        self.proof.write_text('{}')
        with self.assertRaises(ValueError): self.run_link()

    def test_unregistered_source_refused(self):
        db = sqlite3.connect(self.bank / 'catalog.sqlite')
        db.execute('DELETE FROM files'); db.commit(); db.close()
        with self.assertRaises(ValueError): self.run_link()

    def test_outside_project_refused(self):
        with self.assertRaises(ValueError):
            link(self.bank, self.base / 'other', 'a.bin', self.output, self.proof, self.proof_sha)


if __name__ == '__main__': unittest.main()

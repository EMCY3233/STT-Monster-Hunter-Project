import importlib.util,json,sqlite3,tempfile,unittest,zlib
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/'tools/stt_re/audit_resource_relations.py'
spec=importlib.util.spec_from_file_location('relations',FILE);audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def fixture():
    db=sqlite3.connect(':memory:')
    db.executescript('CREATE TABLE assets(sha256 TEXT); CREATE TABLE resources(id INTEGER,path TEXT,sha256 TEXT,type_id TEXT); CREATE TABLE resource_links(source_sha256 TEXT,target_path TEXT,match_kind TEXT,occurrences INTEGER,semantic_verified INTEGER); CREATE TABLE resource_types(type_id TEXT,class_name_candidate TEXT);')
    db.executemany('INSERT INTO assets VALUES(?)',[(c*64,) for c in ('a','b','c')])
    db.executemany('INSERT INTO resources VALUES(?,?,?,?)',[(1,'mesh/body','a'*64,'x'),(2,'tex/main','b'*64,'x'),(3,'tex/main','b'*64,'x')])
    db.execute('INSERT INTO resource_links VALUES(?,?,?,?,?)',('a'*64,'tex/main','exact_normalized_ascii_path',1,0))
    db.execute('INSERT INTO resource_types VALUES(?,?)',(f'{(zlib.crc32(b"rModel")^0xffffffff)&0x7fffffff:08X}','rModel'))
    return db
class RelationsTests(unittest.TestCase):
    def test_repeated_occurrence_not_content_ambiguity(self):
        with fixture() as db:r=audit.analyze(db)
        self.assertEqual(r['repeated_paths'],1);self.assertEqual(r['paths_with_multiple_contents'],0)
        self.assertEqual(r['links']['target_exact_multiple_contents'],0);self.assertEqual(r['type_name_crc_formula_mismatches'],0)
    def test_missing_sources_targets_and_invalid_count(self):
        with fixture() as db:
            db.execute('INSERT INTO resource_links VALUES(?,?,?,?,?)',('d'*64,'missing/path','crc_candidate',0,2));r=audit.analyze(db)
        for key in ('source_missing_asset','source_missing_resource_occurrence','target_missing_exact_path','invalid_occurrence_counts','invalid_semantic_flags'):self.assertEqual(r['links'][key],1)
    def test_content_ambiguity_alias_and_duplicates(self):
        with fixture() as db:
            db.execute('INSERT INTO resources VALUES(?,?,?,?)',(4,'TEX\\MAIN','c'*64,'x'))
            db.execute('INSERT INTO resource_links SELECT * FROM resource_links');r=audit.analyze(db)
        self.assertEqual(r['paths_with_multiple_contents'],0);self.assertEqual(r['normalized_paths_with_multiple_contents'],1)
        self.assertEqual(r['links']['target_normalized_multiple_contents'],2);self.assertEqual(r['links']['duplicate_link_excess_rows'],1)
    def test_stored_semantic_flag_is_not_independent_confirmation(self):
        with fixture() as db:
            db.execute('UPDATE resource_links SET semantic_verified=1');db.execute('UPDATE resource_types SET type_id="bad"');r=audit.analyze(db)
        self.assertEqual(r['recorded_semantic_flag_counts'],{'1':1});self.assertEqual(r['independently_confirmed_semantic_links'],0);self.assertEqual(r['type_name_crc_formula_mismatches'],1)
    def test_readonly_file_unchanged(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as temp:
            p=Path(temp)/'index.sqlite';source=fixture();source.commit();dest=sqlite3.connect(p);source.backup(dest);dest.close();source.close()
            before=p.read_bytes();r=audit.audit(p)
            self.assertTrue(r['index_unchanged']);self.assertEqual(before,p.read_bytes());self.assertEqual(r['asset_payloads_opened'],0)
            self.assertEqual(r['sqlite_integrity_check'],['ok'])
if __name__=='__main__':unittest.main()

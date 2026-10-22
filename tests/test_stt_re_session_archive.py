import hashlib,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
import citra_session_archive as m


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)

    def tearDown(self):self.tmp.cleanup()

    def session(self,size=64,probes=()):
        image=b'C'*8192;(self.root/'image.bin').write_bytes(image)
        mapping=dict(output_sha256=m.sha(image),segments=[dict(name='text',address=0x1000,file_offset=0,code_bytes=32,mapped_bytes=4096),dict(name='data',address=0x2000,file_offset=4096,code_bytes=4096,mapped_bytes=4096)],bss_bytes=8192)
        (self.root/'map.json').write_text(json.dumps(mapping))
        def read(a,n):return b'C'*4 if n==4 else bytes([a//32%256])*32
        with patch.object(m,'read_memory',side_effect=read),patch.object(m.time,'sleep'):
            r=m.capture(self.root/'image.bin',self.root/'map.json',self.root/'session',0x3000,size,2,probes)
        return self.root/'session',r

    def test_dedup_export_and_repeated_address_index(self):
        folder,r=self.session()
        self.assertEqual(r['successful_reads'],4)
        self.assertEqual(r['unique_objects'],2)
        self.assertEqual(r['deduplicated_bytes'],64)
        out=self.root/'export.bin';result=m.export(folder,0,out)
        self.assertEqual(result['sha256'],m.sha(out.read_bytes()))
        self.assertEqual(len(out.read_bytes()),64)
        self.assertEqual(m.analyze(folder)['changed_aligned_words'],[])
        with self.assertRaises(FileExistsError):m.export(folder,0,out)

    def test_tampered_object_rejected(self):
        folder,r=self.session();next((folder/'objects').glob('*.bin')).write_bytes(b'Z'*32)
        with self.assertRaisesRegex(ValueError,'hash/length'):m.load_session(folder)

    def test_tampered_index_rejected(self):
        folder,r=self.session();p=folder/'reads.jsonl';p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaisesRegex(ValueError,'manifest identity'):m.load_session(folder)

    def test_incomplete_session_rejected(self):
        folder,r=self.session();r['status']='failed';(folder/'receipt.json').write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'incomplete'):m.load_session(folder)

    def test_gap_and_duplicate_rejected(self):
        d=self.root/'objects';d.mkdir();digest,_=m.put_object(d,b'A'*32)
        for rows in ([dict(address=0x3000,sha256=digest),dict(address=0x3040,sha256=digest)], [dict(address=0x3000,sha256=digest)]*2):
            with self.assertRaisesRegex(ValueError,'noncontiguous'):m.assemble(d,rows,0x3000,64)

    def test_existing_corrupt_object_rejected(self):
        d=self.root/'objects';d.mkdir();digest,_=m.put_object(d,b'A'*32);(d/(digest+'.bin')).write_bytes(b'B'*32)
        with self.assertRaisesRegex(ValueError,'integrity'):m.put_object(d,b'A'*32)

    def test_object_path_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError,'identity'):m.assemble(self.root,[dict(address=0x3000,sha256='../other')],0x3000,32)

    def test_priority_probes_separate_from_dense_export(self):
        folder,r=self.session(512,(0x3000,0x3020))
        self.assertEqual(r['successful_reads'],36)
        analysis=m.analyze(folder)
        self.assertEqual(len(analysis['priority_probe_summaries']),2)
        self.assertEqual(analysis['priority_probe_summaries'][0]['stats']['samples'],2)
        self.assertEqual(m.export(folder,0,self.root/'dense.bin')['bytes'],512)

    def test_corrupt_accounting_rejected(self):
        folder,r=self.session();r['stored_bytes']+=32;(folder/'receipt.json').write_text(json.dumps(r))
        with self.assertRaisesRegex(ValueError,'accounting'):m.load_session(folder)

import json,struct,sys,tempfile,unittest,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
import extract_arc as m


def fixture(bodies=(b'MOD\0example',b'TEX\0example'),names=(b'../same',b'../same')):
    offset=12+80*len(bodies);table=[];payload=[]
    for body,name in zip(bodies,names):
        compressed=zlib.compress(body)
        table.append(struct.pack('<64sIIII',name,1,len(compressed),len(body)|(1<<29),offset))
        payload.append(compressed);offset+=len(compressed)
    return struct.pack('<4sHHI',b'ARC\0',17,len(bodies),0)+b''.join(table)+b''.join(payload)


class ExtractorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.source=self.root/'source.arc';self.source.write_bytes(fixture());self.out=self.root/'out'

    def tearDown(self):self.tmp.cleanup()

    def test_full_extract_and_source_redecode(self):
        before=m.sha(self.source.read_bytes());r=m.extract(self.source,self.out,before)
        self.assertEqual(r['entry_count'],2);self.assertTrue(r['fresh_source_decode_verified'])
        self.assertEqual(m.sha(self.source.read_bytes()),before)
        self.assertEqual((self.out/'entries/00000.mod').read_bytes(),b'MOD\0example')

    def test_unsafe_duplicate_names_remain_metadata(self):
        m.extract(self.source,self.out)
        manifest=json.loads((self.out/'manifest.json').read_text())
        self.assertEqual([x['path'] for x in manifest['entries']],['../same','../same'])
        self.assertFalse((self.root/'same').exists())
        self.assertEqual(len(list((self.out/'entries').iterdir())),2)

    def test_existing_destination_rejected(self):
        self.out.mkdir();(self.out/'keep').write_text('keep')
        with self.assertRaises(FileExistsError):m.extract(self.source,self.out)
        self.assertEqual((self.out/'keep').read_text(),'keep')

    def test_wrong_expected_source_rejected_before_output(self):
        with self.assertRaises(ValueError):m.extract(self.source,self.out,'0'*64)
        self.assertFalse(self.out.exists())

    def test_corrupt_zlib_rejected_before_output(self):
        b=bytearray(self.source.read_bytes());b[-1]^=255;self.source.write_bytes(b)
        with self.assertRaises((ValueError,zlib.error)):m.extract(self.source,self.out)
        self.assertFalse(self.out.exists())

    def test_tampered_export_rejected(self):
        m.extract(self.source,self.out);(self.out/'entries/00000.mod').write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'hash/size'):m.verify(self.out)

    def test_tampered_manifest_rejected(self):
        m.extract(self.source,self.out);p=self.out/'manifest.json';p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'manifest hash'):m.verify(self.out)

    def test_unexpected_file_rejected(self):
        m.extract(self.source,self.out);(self.out/'entries/extra.bin').write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError,'unexpected'):m.verify(self.out)

    def test_wrong_version_rejected(self):
        b=bytearray(self.source.read_bytes());struct.pack_into('<H',b,4,18);self.source.write_bytes(b)
        with self.assertRaises(ValueError):m.extract(self.source,self.out)
        self.assertFalse(self.out.exists())

    def test_failure_marker_rejected(self):
        m.extract(self.source,self.out);(self.out/'failure.json').write_text('{}')
        with self.assertRaisesRegex(ValueError,'failed export'):m.verify(self.out)

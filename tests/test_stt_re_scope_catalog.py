import json,struct,sys,tempfile,unittest,zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
import extract_arc as arc
from catalog_conversion_scope import catalog


def archive(bodies):
    offset=12+len(bodies)*80;table=[];blobs=[]
    for i,b in enumerate(bodies):
        z=zlib.compress(b);table.append(struct.pack('<64sIIII',str(i).encode(),1,len(z),len(b)|(1<<29),offset));blobs.append(z);offset+=len(z)
    return struct.pack('<4sHHI',b'ARC\0',17,len(bodies),0)+b''.join(table+blobs)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        tex=struct.pack('<4s4I',b'TEX\0',0xa6,1|(8<<6)|(8<<19),1|(12<<8),0)+bytes(64)
        source=self.root/'source.arc';source.write_bytes(archive([tex,b'MOD\0bad']))
        self.out=self.root/'out';arc.extract(source,self.out)
    def tearDown(self):self.tmp.cleanup()
    def modify(self,f):
        p=self.out/'manifest.json';m=json.loads(p.read_text());f(m);raw=json.dumps(m).encode();p.write_bytes(raw);(self.out/'manifest.sha256').write_text(arc.sha(raw))
    def test_supported_texture_and_rejected_model(self):
        r=catalog(self.out);self.assertEqual(r['summary'],dict(tex_header_within_converter_scope=1,outside_current_converter_scope=1))
        self.assertFalse(r['commercial_derivatives_written'])
    def test_catalog_rejects_tampered_payload(self):
        (self.out/'entries/00000.tex').write_bytes(b'bad')
        with self.assertRaises(ValueError):catalog(self.out)
    def test_manifest_size_budget_checked_before_read(self):
        def change(m):m['entries'][0]['observed_bytes']=m['entries'][0]['declared_bytes']=arc.MAX_ENTRY+1
        self.modify(change)
        with self.assertRaisesRegex(ValueError,'budget'):arc.verify(self.out)
    def test_filename_index_checked(self):
        self.modify(lambda m:m['entries'][0].update(output_file='entries/99999.tex'))
        with self.assertRaisesRegex(ValueError,'filename index'):arc.verify(self.out)

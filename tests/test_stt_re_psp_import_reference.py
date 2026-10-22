import importlib.util
from pathlib import Path
import struct
import unittest
spec=importlib.util.spec_from_file_location('imports',Path(__file__).parents[1]/'tools/stt_re/map_psp_import_reference.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def fixture():
    d=bytearray(352); d[:7]=b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH',d,16,2,8,1,0x1000,52,192,0,52,32,1,40,4,1)
    struct.pack_into('<8I',d,52,1,0,0x1000,0x1000,160,192,7,4)
    rows=[]
    for index,name,addr,off,size in ((2,'.lib.stub',0x1080,128,20),(3,'.rodata.sceNid',0x1094,148,12)):
        struct.pack_into('<10I',d,192+index*40,0,1,2,addr,off,size,0,0,4,1)
        rows.append(dict(index=index,name=name,type=1,flags=2,address=addr,offset=off,bytes=size,entry_bytes=1))
    struct.pack_into('<I2BHBBHII',d,128,0,0,0,0,5,0,3,0x1094,0)
    baseline=dict(program_types={'1':1},load_segments=[dict(vaddr=0x1000,offset=0,filesz=160,memsz=192,flags=7,alignment=4)],sections=rows)
    return d,baseline

class ImportPointer(unittest.TestCase):
    def test_dual_mapping(self):
        d,b=fixture(); r=m.inspect(d,b)
        self.assertEqual(r['reference']['target_file_offset'],148); self.assertTrue(r['mapping_agrees_between_section_and_pt_load'])
    def test_bss_is_not_file_data(self):
        d,b=fixture(); struct.pack_into('<I',d,140,0x10a0)
        with self.assertRaisesRegex(ValueError,'file-backed'): m.inspect(d,b)
    def test_nid_array_crosses_backed_end(self):
        d,b=fixture(); struct.pack_into('<H',d,138,4)
        with self.assertRaisesRegex(ValueError,'file-backed'): m.inspect(d,b)
    def test_record_length_outside_scope(self):
        d,b=fixture(); d[136]=4
        with self.assertRaisesRegex(ValueError,'five-word'): m.inspect(d,b)
    def test_section_disagrees_with_segment(self):
        d,b=fixture(); b['sections'][1]['offset']=149; struct.pack_into('<I',d,192+3*40+16,149)
        with self.assertRaisesRegex(ValueError,'mapping mismatch'): m.inspect(d,b)

if __name__=='__main__': unittest.main()

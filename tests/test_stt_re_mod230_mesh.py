import importlib.util
from pathlib import Path
import struct
import unittest

spec=importlib.util.spec_from_file_location('mod_mesh',Path(__file__).parents[1]/'tools/stt_re/inspect_mod230_mesh.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def fixture():
    d=bytearray(382)
    struct.pack_into('<4s4H3I',d,0,b'MOD\0',230,0,1,1,2,3,0)
    struct.pack_into('<10I',d,24,56,0,1,0,0,96,128,256,320,376)
    struct.pack_into('<HH8IBBHHHI',d,256,0,2,0,(28<<16)|(4<<24),0,0,0x59dc400b,0,3,0,0,0,0,0,1,0)
    struct.pack_into('<3H',d,376,0,1,0)
    return d

class ModMeshBounds(unittest.TestCase):
    def test_valid_synthetic_ranges(self):
        r=m.inspect(fixture()); self.assertTrue(r['meshes'][0]['index_values']['all_after_vertex_start_in_range']); self.assertFalse(r['geometry_validated'])
    def test_global_shortfall_reported(self):
        d=fixture(); struct.pack_into('<I',d,16,4)
        self.assertEqual(m.inspect(d)['global_index_shortfall_bytes'],2)
    def test_bad_index(self):
        d=fixture(); struct.pack_into('<H',d,376,2)
        self.assertFalse(m.inspect(d)['meshes'][0]['index_values']['all_after_vertex_start_in_range'])
    def test_nan_position(self):
        d=fixture(); struct.pack_into('<f',d,320,float('nan'))
        self.assertEqual(m.inspect(d)['meshes'][0]['attributes']['finite_position_records'],1)
    def test_stride_span(self):
        d=fixture(); struct.pack_into('<I',d,264,(29<<16)|(4<<24))
        self.assertFalse(m.inspect(d)['meshes'][0]['vertex_span']['in_buffer'])
    def test_table_overlap(self):
        d=fixture(); struct.pack_into('<I',d,44,128)
        with self.assertRaisesRegex(ValueError,'overlap'): m.inspect(d)
    def test_table_outside(self):
        d=fixture(); struct.pack_into('<I',d,52,382)
        with self.assertRaisesRegex(ValueError,'outside'): m.inspect(d)
    def test_bad_signature(self):
        d=fixture(); d[0]=0
        with self.assertRaisesRegex(ValueError,'signature'): m.inspect(d)

if __name__=='__main__': unittest.main()

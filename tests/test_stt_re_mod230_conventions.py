import importlib.util
from pathlib import Path
import unittest
import struct
spec=importlib.util.spec_from_file_location('conventions',Path(__file__).parents[1]/'tools/stt_re/compare_mod230_index_conventions.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def fixture():
    d=bytearray(120)
    struct.pack_into('<4s4H13I',d,0,b'MOD\0',230,0,1,0,2,5,0,0,0,0,0,0,0,0,64,112,112)
    struct.pack_into('<HHIHBB9I',d,64,0,2,0,0,28,4,0,0,0,0,3,0,0,0,0)
    struct.pack_into('<4H',d,112,0,1,0,0)
    return d

class IndexWindows(unittest.TestCase):
    def test_two_conventions_without_silent_padding(self):
        r=m.inspect(fixture())
        self.assertFalse(r['revil_global_read']['in_file'])
        self.assertTrue(r['mhff_mesh_read_plus_two_bytes']['in_file'])
        self.assertEqual(r['mesh_plus_one_checks']['distinct_index_triplets'],r['mesh_declared_checks']['distinct_index_triplets'])
    def test_rejects_multiple_mesh_scope(self):
        d=fixture(); struct.pack_into('<H',d,8,2)
        with self.assertRaisesRegex(ValueError,'single mesh'): m.inspect(d)
    def test_rejects_mesh_header_outside(self):
        d=fixture(); struct.pack_into('<I',d,52,120)
        with self.assertRaisesRegex(ValueError,'bounds'): m.inspect(d)
    def test_rejects_another_version(self):
        d=fixture(); struct.pack_into('<H',d,4,229)
        with self.assertRaisesRegex(ValueError,'MOD230'): m.inspect(d)

if __name__=='__main__': unittest.main()

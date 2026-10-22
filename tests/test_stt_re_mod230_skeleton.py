from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from inspect_mod230_skeleton import inspect,forest


def fixture():
    data=bytearray(64+3*24+3*128+256+28)
    struct.pack_into('<4s4H',data,0,b'MOD\0',230,3,0,0)
    struct.pack_into('<10I',data,24,0,0,0,1,64,len(data),len(data),len(data),len(data),len(data))
    for i,p in enumerate([255,255,1]):struct.pack_into('<BBB',data,64+i*24,0,p,i)
    struct.pack_into('<I',data,len(data)-28,3)
    return data


def probe(data):return inspect(lambda at,n:data[at:at+n],len(data))


class SkeletonTests(unittest.TestCase):
    def test_two_roots_duplicate_ids_do_not_resolve_parents(self):
        r=probe(fixture());self.assertEqual(r['hierarchy']['root_count'],2)
        self.assertEqual(r['hierarchy']['max_depth'],1)
        self.assertEqual(r['index_field_duplicate_records'],2)
        self.assertTrue(r['matrices']['ref_poses']['all_finite'])

    def test_outside_parent(self):
        with self.assertRaisesRegex(ValueError,'outside'):forest([255,7])

    def test_cycle(self):
        with self.assertRaisesRegex(ValueError,'cycle'):forest([255,2,1])

    def test_self_cycle(self):
        with self.assertRaisesRegex(ValueError,'cycle'):forest([0])

    def test_matrix_nan(self):
        data=fixture();struct.pack_into('<f',data,64+72,float('nan'))
        with self.assertRaisesRegex(ValueError,'matrix'):probe(data)

    def test_bone_infinity(self):
        data=fixture();struct.pack_into('<f',data,68,float('inf'))
        with self.assertRaisesRegex(ValueError,'nonfinite bone'):probe(data)

    def test_truncated_tables(self):
        data=fixture()[:-1]
        with self.assertRaisesRegex(ValueError,'exceed file'):probe(data)

    def test_overlap(self):
        data=fixture();struct.pack_into('<I',data,44,80)
        with self.assertRaisesRegex(ValueError,'overlaps'):probe(data)

    def test_no_bones_is_outside_scope(self):
        data=fixture();struct.pack_into('<H',data,6,0)
        with self.assertRaisesRegex(ValueError,'1..255'):probe(data)

    def test_skin_count_capacity(self):
        data=fixture();struct.pack_into('<I',data,len(data)-28,25)
        with self.assertRaisesRegex(ValueError,'capacity'):probe(data)


if __name__=='__main__':unittest.main()

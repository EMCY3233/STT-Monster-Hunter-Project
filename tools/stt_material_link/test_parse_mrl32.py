import struct
import unittest
from parse_mrl32 import parse

class MrlTests(unittest.TestCase):
    def sample(self):
        d=bytearray(176)
        struct.pack_into('<4s6I',d,0,b'MRL\0',32,1,1,0,28,104)
        struct.pack_into('<I',d,28,0x241f5deb)
        d[40:49]=b'tex\\test\0'
        struct.pack_into('<I',d,108,0x813e69ea)
        struct.pack_into('<I',d,112,12)
        struct.pack_into('<I',d,128,1)
        struct.pack_into('<I',d,156,164)
        struct.pack_into('<3I',d,164,3,1,0x12345678)
        return d
    def test_record_and_one_based_candidate(self):
        m=parse(self.sample())['materials'][0]
        self.assertEqual(m['name_hash'],'813e69ea')
        self.assertEqual(m['descriptors'][0]['candidate_resource']['path'],'tex\\test')
    def test_null_candidate(self):
        d=self.sample();struct.pack_into('<I',d,168,0)
        self.assertIsNone(parse(d)['materials'][0]['descriptors'][0]['candidate_resource'])
    def test_out_of_range_candidate(self):
        d=self.sample();struct.pack_into('<I',d,168,2)
        with self.assertRaises(ValueError):parse(d)
    def test_descriptor_count_overflow(self):
        d=self.sample();struct.pack_into('<I',d,128,2)
        with self.assertRaises(ValueError):parse(d)
    def test_block_inside_table(self):
        d=self.sample();struct.pack_into('<I',d,156,104)
        with self.assertRaises(ValueError):parse(d)
    def test_truncation(self):
        with self.assertRaises(ValueError):parse(self.sample()[:-1])
if __name__=='__main__':unittest.main()

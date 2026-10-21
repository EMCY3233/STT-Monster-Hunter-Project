from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from probe_ncsd_executable import probe
from test_stt_re_ncch_code import plain_ncch


def fixture():
    ncch=bytearray(plain_ncch());ncch[0x18d]=2
    struct.pack_into('<I',ncch,0x104,len(ncch)//512)
    struct.pack_into('<I',ncch,0x1a8,1)
    outer=bytearray(512);outer[256:260]=b'NCSD'
    struct.pack_into('<II',outer,0x120,1,len(ncch)//512)
    return bytes(outer+ncch)


def inspect(data):return probe(lambda at,n:data[at:at+n],len(data))


class NcsdProbeTests(unittest.TestCase):
    def test_plain_partition_reuses_layout_no_decompression(self):
        r=inspect(fixture())
        self.assertEqual(r['partition_index'],0)
        self.assertEqual(r['declared_code_pages_bytes'],12288)
        self.assertFalse(r['code_decompressed']);self.assertIsNone(r['blz_footer'])
        self.assertTrue(all(x['hash_verified'] for x in r['exefs_entries']))

    def test_partition_outside_file(self):
        data=bytearray(fixture());struct.pack_into('<I',data,0x124,999999)
        with self.assertRaisesRegex(ValueError,'partition'):inspect(data)

    def test_encryption_rejected(self):
        data=bytearray(fixture());data[512+399]=0
        with self.assertRaisesRegex(ValueError,'plain NCCH'):inspect(data)

    def test_non_executable_rejected(self):
        data=bytearray(fixture());data[512+0x18d]=0
        with self.assertRaisesRegex(ValueError,'not executable'):inspect(data)

    def test_exheader_hash_rejected(self):
        data=bytearray(fixture());data[1024+0x20c]=3
        with self.assertRaisesRegex(ValueError,'ExHeader hash'):inspect(data)

    def test_entry_corruption_rejected(self):
        data=bytearray(fixture());data[-1]=1
        with self.assertRaisesRegex(ValueError,'entry hash'):inspect(data)

    def test_short_reader_rejected(self):
        with self.assertRaisesRegex(ValueError,'short read'):probe(lambda at,n:b'',20000)


if __name__=='__main__':unittest.main()

import hashlib
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from inspect_ncch_code import blz_footer,decompress_blz,inspect_ncch


def packed(extra=7):
    stream=b'PRE'+bytes([0,0xf0,ord('C'),ord('B'),ord('A'),0x10])
    return stream+struct.pack('<II',(8<<24)|14,extra)


def plain_ncch():
    code=bytes(3*4096)
    ex=bytearray(1024)
    for at,address in [(0x10,0x100000),(0x20,0x101000),(0x30,0x102000)]:
        struct.pack_into('<III',ex,at,address,1,4096)
    table=bytearray(512)
    struct.pack_into('<8sII',table,0,b'.code',0,len(code))
    table[480:512]=hashlib.sha256(code).digest()
    h=bytearray(512);h[256:260]=b'NCCH';h[399]=4
    struct.pack_into('<I',h,384,1024)
    struct.pack_into('<II',h,416,3,25)
    h[352:384]=hashlib.sha256(ex).digest()
    h[448:480]=hashlib.sha256(table).digest()
    return bytes(h+ex+table+code)


class NcchCodeTests(unittest.TestCase):
    def test_overlap_reference_and_prefix(self):
        output,r=decompress_blz(packed())
        self.assertEqual(output,b'PRE'+b'CBA'*7)
        self.assertEqual((r['literals'],r['backreferences'],r['backreference_bytes']),(3,1,18))
        self.assertTrue(r['input_stream_consumed'])

    def test_short_footer(self):
        with self.assertRaisesRegex(ValueError,'truncated'):blz_footer(b'123')

    def test_bad_top(self):
        data=packed();data=data[:-8]+struct.pack('<II',(7<<24)|14,7)
        with self.assertRaisesRegex(ValueError,'bounds'):blz_footer(data)

    def test_output_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'):blz_footer(packed(100*1024*1024))

    def test_bad_reference(self):
        data=b'PRE'+bytes([0,0,0x80])+struct.pack('<II',(8<<24)|11,7)
        with self.assertRaisesRegex(ValueError,'reference beyond'):decompress_blz(data)

    def test_coverage_mismatch(self):
        with self.assertRaisesRegex(ValueError,'coverage'):decompress_blz(packed(8))

    def test_uncompressed_flag_does_not_force_blz(self):
        r,output=inspect_ncch(plain_ncch())
        self.assertFalse(r['compressed']);self.assertFalse(r['decompressed'])
        self.assertEqual(output,bytes(12288));self.assertIsNone(r['decompression'])

    def test_exheader_hash_rejects_change(self):
        data=bytearray(plain_ncch());data[512+13]=1
        with self.assertRaisesRegex(ValueError,'ExHeader hash'):inspect_ncch(data)

    def test_encrypted_ncch_rejected(self):
        data=bytearray(plain_ncch());data[399]=0
        with self.assertRaisesRegex(ValueError,'plain NCCH'):inspect_ncch(data)

    def test_segment_overlap_rejected(self):
        data=bytearray(plain_ncch());struct.pack_into('<I',data,512+0x20,0x100000)
        data[352:384]=hashlib.sha256(data[512:1536]).digest()
        with self.assertRaisesRegex(ValueError,'overlap'):inspect_ncch(data)


if __name__=='__main__':unittest.main()

import importlib.util
from pathlib import Path
import struct
import unittest
spec=importlib.util.spec_from_file_location('tex',Path(__file__).parents[1]/'tools/stt_re/inspect_tex3ds_header.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def fixture(): return bytearray(struct.pack('<4s4I',b'TEX\0',0x200000a6,1|(8<<6)|(8<<19),1|(12<<8),0)+bytes(64))

class TexRanges(unittest.TestCase):
    def test_full_block_payload_without_pixels(self):
        r=m.inspect(fixture()); self.assertTrue(r['exact_header_table_payload_fit']); self.assertFalse(r['pixel_decoding_performed'])
    def test_truncated_table(self):
        with self.assertRaisesRegex(ValueError,'bounds'): m.inspect(fixture()[:19])
    def test_payload_overrun(self):
        with self.assertRaisesRegex(ValueError,'exceeds'): m.inspect(fixture()[:-1])
    def test_offset_is_relative(self):
        d=fixture(); struct.pack_into('<I',d,16,4)
        with self.assertRaisesRegex(ValueError,'exceeds'): m.inspect(d)
    def test_zero_dimensions(self):
        d=fixture(); struct.pack_into('<I',d,8,1)
        with self.assertRaisesRegex(ValueError,'dimensions'): m.inspect(d)
    def test_unsupported_version(self):
        d=fixture(); struct.pack_into('<I',d,4,0xa3)
        with self.assertRaisesRegex(ValueError,'layout scope'): m.inspect(d)
    def test_no_guess_for_unknown_format(self):
        d=fixture(); struct.pack_into('<I',d,12,1|(13<<8))
        with self.assertRaisesRegex(ValueError,'color format'): m.inspect(d)

if __name__=='__main__': unittest.main()

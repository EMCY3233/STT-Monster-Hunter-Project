import importlib.util
from pathlib import Path
import struct
import unittest

spec=importlib.util.spec_from_file_location('jkr',Path(__file__).parents[1]/'tools/stt_re/decode_jkr_lz.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class JkrLz(unittest.TestCase):
    def test_literals(self): self.assertEqual(m.decode_payload(b'\0ABC',3)[0],b'ABC')
    def test_short_overlap(self): self.assertEqual(m.decode_payload(b'\x40A\0',4)[0],b'AAAA')
    def test_medium(self): self.assertEqual(m.decode_payload(b'\x60A\x20\0',4)[0],b'AAAA')
    def test_long_a(self): self.assertEqual(m.decode_payload(b'\x60A\0\0',11)[0],b'A'*11)
    def test_long_b(self): self.assertEqual(m.decode_payload(b'\x70A\0\0\0',27)[0],b'A'*27)
    def test_raw_block(self): self.assertEqual(m.decode_payload(b'\xe0\0\0\xff'+b'X'*27,27)[0],b'X'*27)
    def test_truncated(self):
        with self.assertRaisesRegex(ValueError,'truncated'): m.decode_payload(b'\0',1)
    def test_bad_backreference(self):
        with self.assertRaisesRegex(ValueError,'before output'): m.decode_payload(b'\x80\0',3)
    def test_output_overshoot(self):
        with self.assertRaisesRegex(ValueError,'exceeds'): m.decode_payload(b'\x40A\0',3)
    def test_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'): m.decode_payload(b'',m.LIMIT+1)
    def test_control_reload(self): self.assertEqual(m.decode_payload(b'\0ABCDEFGH\0I',9)[0],b'ABCDEFGHI')
    def test_trailing_recorded(self): self.assertEqual(m.decode_payload(b'\0A?',1)[1]['trailing_payload_bytes'],1)
    def test_wrong_codec(self):
        with self.assertRaisesRegex(ValueError,'unsupported'): m.decode_container(b'JKR\x1a'+struct.pack('<HHII',0x108,4,16,3))

if __name__=='__main__': unittest.main()

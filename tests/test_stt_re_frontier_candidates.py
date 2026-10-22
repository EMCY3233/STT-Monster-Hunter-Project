import importlib.util
from pathlib import Path
import struct
import unittest

spec=importlib.util.spec_from_file_location('candidates',Path(__file__).parents[1]/'tools/stt_re/inspect_frontier_candidates.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class CandidateHeaders(unittest.TestCase):
    def test_jkr(self): self.assertEqual(m.header(b'JKR\x1a'+struct.pack('<HHII',0x108,4,16,50),30)['declared_output_bytes'],50)
    def test_jkr_bad_offset(self):
        with self.assertRaisesRegex(ValueError,'offset'): m.header(b'JKR\x1a'+struct.pack('<HHII',0x108,4,31,50),30)
    def test_jkr_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'): m.header(b'JKR\x1a'+struct.pack('<HHII',0x108,4,16,2**32-1),30)
    def test_ecd(self): self.assertTrue(m.header(b'ecd\x1a'+struct.pack('<HHII',4,0,10,0),26)['payload_length_matches'])
    def test_ecd_length_mismatch(self):
        with self.assertRaisesRegex(ValueError,'length'): m.header(b'ecd\x1a'+struct.pack('<HHII',4,0,10,0),27)
    def test_sce_does_not_claim_elf(self): self.assertEqual(m.header(b'SCE\0'+bytes(12),100)['kind'],'SCE_wrapper')

if __name__=='__main__': unittest.main()

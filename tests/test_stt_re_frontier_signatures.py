"""Only synthetic public format markers, no licenses or commercial data."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('frontier',Path(__file__).parents[1]/'tools/stt_re/inspect_frontier_local.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class SignatureTests(unittest.TestCase):
    def test_ecd(self): self.assertEqual(m.signature(b'ecd\x1a'),'ECD_candidate')
    def test_exf(self): self.assertEqual(m.signature(b'exf\x1a'),'EXF_candidate')
    def test_jkr(self): self.assertEqual(m.signature(b'JKR\x1a'),'JKR_candidate')
    def test_reversed_marker_not_accepted(self): self.assertEqual(m.signature(b'\x1aecd'),'unclassified')

if __name__=='__main__': unittest.main()

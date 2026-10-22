import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('block',Path(__file__).parents[1]/'tools/stt_re/capture_citra_bss_block.py')
import sys
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class PlanTests(unittest.TestCase):
    def setUp(self):
        self.mapping=dict(segments=[dict(name='data',address=4096,mapped_bytes=4096,file_offset=0)],bss_bytes=8192)

    def test_exact_edges(self):
        r=m.plan(self.mapping,4096,8192,8192)
        self.assertEqual(len(r),256)
        self.assertEqual(r[-1],(16352,32))

    def test_reject_outside_and_large_and_unaligned(self):
        for a,n in [(8160,32),(16384,32),(8192,8224),(8193,32),(8192,31)]:
            with self.assertRaises(ValueError):m.plan(self.mapping,4096,a,n)

    def test_wrong_backing(self):
        with self.assertRaises(ValueError):m.plan(self.mapping,4097,8192,32)

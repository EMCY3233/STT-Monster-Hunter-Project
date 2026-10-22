import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('layout',Path(__file__).parents[1]/'tools/stt_re/inspect_frontier_text_layout.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class LayoutBounds(unittest.TestCase):
    def test_external_anchors_only(self):
        data=bytes(20)+b'AB\0'+bytes(12)+b'XYZ\0'
        r=m.inspect(data,[dict(offset=20,bytes=2),dict(offset=35,bytes=3)])
        self.assertEqual(r['region_count'],2); self.assertFalse(r['grammar_verified'])
    def test_missing_terminator(self):
        with self.assertRaisesRegex(ValueError,'boundary'): m.inspect(bytes(20)+b'ABC',[dict(offset=20,bytes=2)])
    def test_embedded_nul(self):
        with self.assertRaisesRegex(ValueError,'NUL'): m.inspect(bytes(20)+b'A\0B\0',[dict(offset=20,bytes=3)])
    def test_overlapping_anchors(self):
        with self.assertRaisesRegex(ValueError,'boundary'): m.inspect(bytes(20)+b'AB\0',[dict(offset=20,bytes=2),dict(offset=20,bytes=2)])
    def test_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'): m.inspect(bytes(65537),[])

if __name__=='__main__': unittest.main()

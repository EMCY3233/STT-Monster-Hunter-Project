import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('pair',Path(__file__).parents[1]/'tools/stt_re/compare_frontier_jkr_pair.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class PairBounds(unittest.TestCase):
    def test_partial_template_is_not_grammar(self):
        data=bytes(20)+b'AB\0'
        r=m.compare(data,data,[dict(offset=20,bytes=2)])
        self.assertTrue(r['contrast_partial_pattern_matches']); self.assertTrue(r['pattern_is_not_grammar'])
    def test_pair_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'): m.compare(b'A',bytes(4097),[])
    def test_bad_anchor(self):
        with self.assertRaisesRegex(ValueError,'bounds'): m.compare(b'ABC',b'ABC',[dict(offset=0,bytes=2)])

if __name__=='__main__': unittest.main()

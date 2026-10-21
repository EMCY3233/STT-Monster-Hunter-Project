import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('jkr_selection',Path(__file__).parents[1]/'tools/stt_re/decode_jkr_lz.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def row(path,size=500,sha='new',codec=3): return dict(path=path,declared_output_bytes=size,sha256=sha,kind='JKR',version=0x108,codec=codec)

class Selection(unittest.TestCase):
    def test_exclude_control(self): self.assertEqual(m.select_candidate([row('a',349,'old'),row('b')],'old',4096)['path'],'b')
    def test_tie_by_path(self): self.assertEqual(m.select_candidate([row('z'),row('a')],None,4096)['path'],'a')
    def test_filters_codec(self): self.assertEqual(m.select_candidate([row('a',100,codec=4),row('b')],None,4096)['path'],'b')
    def test_no_candidate_does_not_expand(self):
        with self.assertRaisesRegex(ValueError,'no verified'): m.select_candidate([row('a',4097)],None,4096)
    def test_bad_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'): m.select_candidate([row('a')],None,m.LIMIT+1)

if __name__=='__main__': unittest.main()

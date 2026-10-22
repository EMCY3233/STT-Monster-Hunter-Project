"""Bounds checks for synthetic sector tables; no game data or cipher tables."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec=importlib.util.spec_from_file_location('data_probe',Path(__file__).parents[1]/'tools/stt_re/probe_mhfu_data.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def table(values):
    return struct.pack('<'+'I'*len(values),*values).ljust(2048,b'\0')

class TocBounds(unittest.TestCase):
    def test_sector_entries(self):
        rows=m.validate_toc(table([1,2,3]),6144)
        self.assertEqual([r['allocated_bytes'] for r in rows],[2048,2048])
    def test_missing_end(self):
        with self.assertRaisesRegex(ValueError,'sentinel'): m.validate_toc(table([1,2]),6144)
    def test_backward_sector(self):
        with self.assertRaisesRegex(ValueError,'nonmonotonic'): m.validate_toc(table([1,3,2,4]),8192)
    def test_table_length_mismatch(self):
        with self.assertRaisesRegex(ValueError,'length'): m.validate_toc(table([2,3]),6144)
    def test_unaligned_source(self):
        with self.assertRaisesRegex(ValueError,'unaligned'): m.validate_toc(table([1,2,3]),6145)
    def test_entry_budget(self):
        with self.assertRaisesRegex(ValueError,'budget'): m.validate_toc(table([1,40000]),40000*2048)

if __name__=='__main__': unittest.main()

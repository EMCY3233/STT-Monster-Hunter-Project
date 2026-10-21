"""Synthetic encoding fixtures only; no commercial text."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('cp932_probe', Path(__file__).parents[1] / 'tools/probe_cp932_regions.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Cp932ProbeTests(unittest.TestCase):
    def test_offsets_and_no_text_export(self):
        result = m.probe(b'\x00\x82\xa0\x82\xa2\x00')
        self.assertEqual(result['regions'][0]['offset'], 1)
        self.assertEqual(result['regions'][0]['bytes'], 4)
        self.assertEqual(result['regions'][0]['kana_block_codepoints'], 2)
        self.assertFalse(result['exports_text'])
        self.assertFalse(result['format_identified'])
        self.assertNotIn('text', result['regions'][0])

    def test_ascii_only_not_selected(self):
        self.assertEqual(m.probe(b'plain\x00text\x00')['matching_regions'], 0)

    def test_truncated_lead_byte_not_replaced(self):
        self.assertEqual(m.probe(b'\x82\xa0\x82\x00')['matching_regions'], 0)

    def test_controls_preserved_as_metadata(self):
        region = m.probe(b'\x07\x0a\x0c\x82\xa0\x00')['regions'][0]
        self.assertEqual(region['control_codepoints'], 3)
        self.assertTrue(region['nul_terminated'])

    def test_unterminated_tail_not_presented_as_terminated(self):
        self.assertFalse(m.probe(b'\x82\xa0')['regions'][0]['nul_terminated'])

    def test_byte_budget_and_type(self):
        with self.assertRaises(ValueError): m.probe(b'x' * (m.MAX_BYTES + 1))
        with self.assertRaises(ValueError): m.probe('text')


if __name__ == '__main__': unittest.main()

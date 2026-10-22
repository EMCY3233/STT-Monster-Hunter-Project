import importlib.util,struct,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('counter',Path(__file__).parents[1]/'tools/stt_re/translate_citra_counter.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def sample(v):
    b=bytearray(32);struct.pack_into('<II',b,4,v,v);return bytes(b)


class CounterTests(unittest.TestCase):
    def test_frequency_and_wrap(self):
        r=m.summarize([sample(0xfffffffa),sample(0),sample(6)],[0,.1,.2])
        self.assertAlmostEqual(r['fields']['4']['units_per_host_second'],60)
        self.assertTrue(r['paired_fields_equal'])
        self.assertFalse(r['semantic_identity_verified'])

    def test_frozen(self):
        r=m.summarize([sample(9),sample(9)],[1,2])
        self.assertEqual(r['fields']['4']['observed_units'],0)

    def test_reject_invalid_times(self):
        with self.assertRaises(ValueError):m.summarize([sample(0),sample(6)],[1,1])

    def test_asymmetric_frozen_fields(self):
        b=bytearray(sample(9));struct.pack_into('<I',b,8,8)
        r=m.summarize([bytes(b),bytes(b)],[1,2])
        self.assertFalse(r['paired_fields_equal'])
        self.assertEqual(r['paired_difference_u32_counts'],[dict(delta=0xffffffff,count=2)])

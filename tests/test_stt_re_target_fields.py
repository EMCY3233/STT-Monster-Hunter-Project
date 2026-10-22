from pathlib import Path
import struct,sys,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from record_citra_target import field_stats,record


class FieldTests(unittest.TestCase):
    def test_wrapping_u32_is_a_bit_view(self):
        samples=[struct.pack('<I',x)+bytes(28) for x in [0xffffffff,0,1,1]]
        r=field_stats(samples);f=r['u32_le'][0]
        self.assertEqual(f['modular_delta_counts'],[dict(delta=0,count=1),dict(delta=1,count=2)])
        self.assertEqual(f['changed_pairs'],2);self.assertEqual(f['distinct_bit_patterns'],3)
        self.assertEqual(r['changed_byte_indices'],[0,1,2,3])

    def test_constant_fields_are_not_named(self):
        r=field_stats([bytes(32),bytes(32)])
        self.assertTrue(all(x['changed_pairs']==0 for x in r['u32_le']))
        self.assertEqual(r['changed_byte_indices'],[])

    def test_malformed_samples_rejected(self):
        with self.assertRaises(ValueError):field_stats([bytes(32),bytes(31)])
        self.assertEqual(field_stats([])['samples'],0)

    def test_capture_limits_before_any_file_read(self):
        for seconds,interval in [(61,.1),(12,.01),(float('nan'),.1)]:
            with self.assertRaises(ValueError):record('absent','absent','absent','absent','user-declared-idle',seconds=seconds,interval=interval)


if __name__=='__main__':unittest.main()

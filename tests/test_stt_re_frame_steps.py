import importlib.util,struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from compare_citra_frame_steps import compare


def block(v):
    b=bytearray(32);struct.pack_into('<II',b,4,v,v);return bytes(b)*2


class FrameStepTests(unittest.TestCase):
    def test_zero_and_single_with_u32_wrap(self):
        r=compare([block(0xffffffff),block(0xffffffff),block(0)],[0,1])
        self.assertTrue(r['all_match'])
        self.assertFalse(r['game_logic_frame_identity_verified'])

    def test_mismatch_is_not_success(self):
        self.assertFalse(compare([block(1),block(3)],[1])['all_match'])

    def test_unstable_capture_rejected(self):
        with self.assertRaises(ValueError):compare([block(1),block(2)[:32]+block(3)[:32]],[1])

    def test_bad_action_count(self):
        with self.assertRaises(ValueError):compare([block(1),block(2)],[])

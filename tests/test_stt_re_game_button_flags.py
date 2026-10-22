import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from hold_citra_arrow import event_flags,KEYS


class ButtonTests(unittest.TestCase):
    def test_arrow_extended_flags(self):
        self.assertEqual(event_flags('right',False),9);self.assertEqual(event_flags('right',True),11)
    def test_normal_button_not_extended(self):
        for key in ('interact','cancel','menu'):
            self.assertEqual(event_flags(key,False),8);self.assertEqual(event_flags(key,True),10)
        self.assertEqual(KEYS['interact'][1],0x1e)
    def test_unknown_control_rejected(self):
        with self.assertRaises(ValueError):event_flags('Windows',False)

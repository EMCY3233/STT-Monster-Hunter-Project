import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from audit_game_input import audit

class AuditTests(unittest.TestCase):
    def row(self,key,event,t,accepted=1):return dict(key=key,event=event,monotonic=t,accepted=accepted)
    def test_combo_released(self):
        r=audit(dict(keys=['left','up'],executed=True,status='completed',events=[self.row('left','down',1),self.row('up','down',1),self.row('up','up',2),self.row('left','up',2)]))
        self.assertEqual(r['issues'],[]);self.assertFalse(r['game_effect_verified'])
    def test_unreleased_key(self):
        r=audit(dict(keys=['left'],executed=True,status='failed',events=[self.row('left','down',1),self.row('left','up',2,0)]))
        self.assertIn('release_not_confirmed',r['issues'])
    def test_wrong_focus_no_events(self):
        r=audit(dict(keys=['left'],executed=False,status='failed',events=[]))
        self.assertEqual(r['event_count'],0);self.assertEqual(r['issues'],[])
    def test_nonmonotonic_invalid(self):
        with self.assertRaises(ValueError):audit(dict(keys=['left'],events=[self.row('left','down',2),self.row('left','up',1)]))

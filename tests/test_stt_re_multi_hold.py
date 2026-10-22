import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from hold_citra_arrow import hold_keys,validate_keys

class MultiTests(unittest.TestCase):
    def exercise(self,fail=None,focus=None):
        events=[];ticks=[0.0]
        def send(key,up):
            events.append((key,up))
            if (key,up)==fail:raise RuntimeError('rejected')
        def sleep(n):ticks[0]+=n
        def run():return hold_keys(send,focus or (lambda:True),sleep,lambda:ticks[0],5,('left','down','dash'))
        return events,run
    def test_long_three_key_hold(self):
        e,run=self.exercise();self.assertGreaterEqual(run(),5)
        self.assertEqual(e,[('left',False),('down',False),('dash',False),('dash',True),('down',True),('left',True)])
    def test_partial_press_failure_releases_attempted(self):
        e,run=self.exercise(('down',False))
        with self.assertRaises(RuntimeError):run()
        self.assertEqual(e[-2:],[('down',True),('left',True)])
    def test_release_failure_does_not_skip_others(self):
        e,run=self.exercise(('dash',True))
        with self.assertRaises(RuntimeError):run()
        self.assertEqual(e[-2:],[('down',True),('left',True)])
    def test_focus_loss_releases_all(self):
        checks=iter([True,True,True,True,False]);e,run=self.exercise(focus=lambda:next(checks))
        with self.assertRaises(RuntimeError):run()
        self.assertEqual(e[-3:],[('dash',True),('down',True),('left',True)])
    def test_invalid_combinations(self):
        for keys in [(),('left','right'),('up','down'),('left','left'),('unknown',)]:
            with self.assertRaises(ValueError):validate_keys(keys)

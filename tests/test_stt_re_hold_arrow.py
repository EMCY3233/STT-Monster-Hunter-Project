import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("hold_arrow", Path(__file__).parents[1] / "tools/stt_re/hold_citra_arrow.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class HoldTests(unittest.TestCase):
    def run_hold(self, focus=lambda: True, fail_down=False):
        events, ticks = [], [0.0]
        def send(up):
            events.append(up)
            if fail_down and not up:
                raise RuntimeError("input rejected")
        def sleep(n):
            ticks[0] += n
        return events, lambda: m.hold(send, focus, sleep, lambda: ticks[0], 0.1)

    def test_one_down_one_up_with_duration(self):
        events, run = self.run_hold()
        self.assertGreaterEqual(run(), 0.1)
        self.assertEqual(events, [False, True])

    def test_release_on_focus_loss(self):
        checks = iter([True, False])
        events, run = self.run_hold(lambda: next(checks))
        with self.assertRaisesRegex(RuntimeError, "foreground changed"):
            run()
        self.assertEqual(events, [False, True])

    def test_release_after_rejected_down(self):
        events, run = self.run_hold(fail_down=True)
        with self.assertRaisesRegex(RuntimeError, "input rejected"):
            run()
        self.assertEqual(events, [False, True])

    def test_no_input_wrong_focus(self):
        events, run = self.run_hold(lambda: False)
        with self.assertRaisesRegex(RuntimeError, "not foreground"):
            run()
        self.assertEqual(events, [])

    def test_duration_limit(self):
        for value in (0, 3.1, float("nan")):
            with self.assertRaises(ValueError):
                m.hold(None, None, None, None, value)


if __name__ == "__main__":
    unittest.main()

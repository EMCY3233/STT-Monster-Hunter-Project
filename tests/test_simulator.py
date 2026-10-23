import unittest

from stt_monitor.protocol import decode, encode
from stt_monitor.simulator import SIMULATED_ERROR, attempts, packet


class SimulatorV2Test(unittest.TestCase):
    def test_v1_default_unchanged(self):
        self.assertEqual(packet('s', 0, 0)['version'], 1)
        self.assertNotIn('diagnostics', packet('s', 0, 0))

    def test_v2_without_failures_counts_prior_successes(self):
        rows = list(attempts(5))
        self.assertTrue(all(send for _, send, _ in rows))
        for seq, _, d in rows:
            self.assertEqual(d, dict(send_ok=seq, send_errors=0, last_result=0, net_errno=0))
            decode(encode(packet('s', seq, seq * 1000, version=2, diagnostics=d)))

    def test_v2_failures_are_skipped_and_reported_by_next_packet(self):
        rows = list(attempts(7, fail_every=3))
        self.assertEqual([send for _, send, _ in rows], [True, True, False, True, True, False, True])
        _, _, d3 = rows[3]
        self.assertEqual(d3, dict(send_ok=2, send_errors=1, last_result=SIMULATED_ERROR, net_errno=1))
        _, _, d6 = rows[6]
        self.assertEqual((d6['send_ok'], d6['send_errors']), (4, 2))
        for seq, send, d in rows:
            if send:  # Every emitted packet must satisfy the receiver's STT/2 contract.
                decode(encode(packet('s', seq, 0, version=2, diagnostics=d)))


if __name__ == '__main__':
    unittest.main()

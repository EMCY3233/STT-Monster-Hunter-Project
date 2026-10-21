import json
import unittest
from stt_monitor.analyze import summarize
from stt_monitor.simulator import packet


def line(seq, session='demo', peer='127.0.0.1'):
    return json.dumps({'peer_ip': peer, 'packet': packet(session, seq, seq*1000)})


class AnalysisTests(unittest.TestCase):
    def test_duplicates_reordering_and_gap(self):
        report = summarize([line(n) for n in (2, 5, 2, 3)])
        session = report['sessions'][0]
        self.assertEqual(session['packets'], 4)
        self.assertEqual(session['duplicates'], 1)
        self.assertEqual(session['out_of_order'], 1)
        self.assertEqual(session['missing_between_observed'], 1)
        self.assertEqual(session['first_seq'], 2)

    def test_late_arrival_fills_gap(self):
        report = summarize([line(n) for n in (0, 2, 1)])
        self.assertEqual(report['sessions'][0]['missing_between_observed'], 0)

    def test_separate_restarts_and_peers(self):
        report = summarize([line(0), line(0, 'restart'), line(0, peer='127.0.0.2')])
        self.assertEqual(len(report['sessions']), 3)

    def test_empty_and_invalid(self):
        self.assertEqual(summarize([]), {'sessions': [], 'invalid_lines': 0})
        report = summarize(['bad', '{}', 'null', '[]', line(0)])
        self.assertEqual(report['invalid_lines'], 4)
        self.assertEqual(len(report['sessions']), 1)


class ReceptionTimingTests(unittest.TestCase):
    @staticmethod
    def record(seq, stamp, uptime, session='timing'):
        return json.dumps(dict(peer_ip='127.0.0.1', received_at=stamp,
                               packet=packet(session, seq, uptime)))

    def test_gap_compares_same_session_process_time_and_normalizes_zone(self):
        rows = [self.record(15, '2026-10-21T08:00:00+02:00', 15000),
                self.record(0, '2026-10-21T06:00:25+00:00', 0, 'other'),
                self.record(16, '2026-10-21T06:00:53.5+00:00', 23000)]
        summary = summarize(rows)
        timing = next(s for s in summary['sessions'] if s['session'] == 'timing')['reception_timing']
        self.assertEqual(timing['largest_gap'], dict(seconds=53.5, from_seq=15,
                         to_seq=16, process_uptime_delta_ms=8000))
        self.assertEqual(timing['first_received_at'], '2026-10-21T06:00:00+00:00')
        self.assertEqual(timing['timestamped_packets'], 2)

    def test_missing_invalid_or_naive_timestamps_break_comparison(self):
        for value in (None, 10, 'bad', '2026-10-21T06:00:01'):
            with self.subTest(value=value):
                rows = [self.record(0, '2026-10-21T06:00:00Z', 0),
                        self.record(1, value, 1000),
                        self.record(2, '2026-10-21T06:00:30Z', 2000)]
                summary = summarize(rows)
                timing = summary['sessions'][0]['reception_timing']
                self.assertEqual(timing['unusable_timestamps'], 1)
                self.assertIsNone(timing['largest_gap'])
                self.assertEqual(summary['sessions'][0]['unique_packets'], 3)
                self.assertEqual(summary['invalid_lines'], 0)

    def test_clock_regression_and_out_of_order_uptime_are_not_suspend_claims(self):
        rows = [self.record(2, '2026-10-21T06:00:02Z', 2000),
                self.record(3, '2026-10-21T06:00:01Z', 3000),
                self.record(1, '2026-10-21T06:00:05Z', 1000)]
        session = summarize(rows)['sessions'][0]
        self.assertEqual(session['reception_timing']['clock_regressions'], 1)
        self.assertEqual(session['reception_timing']['largest_gap'], dict(
            seconds=4.0, from_seq=3, to_seq=1, process_uptime_delta_ms=-2000))
        self.assertEqual(session['out_of_order'], 1)

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

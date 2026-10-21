import copy
import json
import unittest
from stt_monitor.protocol import decode, encode
from stt_monitor.simulator import packet
from stt_monitor.analyze import summarize


def diagnostic_packet(seq=3):
    p = packet('diagnostic', seq, 1000)
    p.update(version=2, diagnostics=dict(send_ok=seq-1, send_errors=1,
                                        last_result=-2143223347, net_errno=50))
    return p


class DiagnosticTests(unittest.TestCase):
    def test_v2_roundtrip_signed_code(self):
        p = diagnostic_packet()
        self.assertEqual(decode(encode(p)), p)
        self.assertEqual(p['diagnostics']['last_result'] & 0xffffffff, 0x804101CD)

    def test_reject_invalid_counters_and_codes(self):
        for key, value in [('send_ok', True), ('send_ok', -1), ('send_ok', 3),
                           ('send_errors', 0), ('send_errors', 4),
                           ('last_result', 2**31), ('net_errno', -(2**31)-1),
                           ('net_errno', False)]:
            with self.subTest(key=key, value=value):
                p = diagnostic_packet()
                p['diagnostics'][key] = value
                with self.assertRaises(ValueError):
                    encode(p)

    def test_reject_unknown_missing_or_nonobject_diagnostics(self):
        p = diagnostic_packet()
        for d in (None, [], {}, dict(p['diagnostics'], extra=0)):
            q = copy.deepcopy(p)
            q['diagnostics'] = d
            with self.assertRaises(ValueError):
                encode(q)
        p['version'] = 1
        with self.assertRaises(ValueError):
            encode(p)

    def test_v1_still_roundtrips(self):
        p = packet('old', 0, 0)
        self.assertEqual(decode(encode(p)), p)

    def test_analyzer_preserves_highest_sequence_diagnostics(self):
        latest = diagnostic_packet(3)
        older = diagnostic_packet(2)
        older['diagnostics']['net_errno'] = 0
        lines = [json.dumps(dict(peer_ip='127.0.0.1', packet=p)) for p in (latest, older)]
        summary = summarize(lines)['sessions'][0]
        self.assertEqual(summary['diagnostics_latest'], latest['diagnostics'])

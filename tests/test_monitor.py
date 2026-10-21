import io
import json
import socket
import threading
import unittest
from unittest.mock import patch
from stt_monitor.protocol import decode, encode
from stt_monitor.receiver import receive
from stt_monitor.simulator import packet


class ProtocolTests(unittest.TestCase):
    def test_roundtrip_and_unknown_battery(self):
        p = packet('test', 0, 10)
        for battery in (None, 0, 100, 49.5):
            p['battery_pct'] = battery
            self.assertEqual(decode(encode(p)), p)

    def test_reject_invalid_fields(self):
        for key, value in [('version', 2), ('version', True), ('seq', -1),
                           ('seq', True), ('uptime_ms', 2**53), ('battery_pct', 101),
                           ('battery_pct', float('nan')), ('source', 'unknown'),
                           ('session', '../bad')]:
            with self.subTest(key=key, value=value):
                p = packet('test', 0, 0)
                p[key] = value
                with self.assertRaises(ValueError):
                    decode(json.dumps(p).encode())

    def test_malformed(self):
        for raw in (b'[]', b'null', b'{', b'\xff', b'x'*1025,
                    b'{"version":1,"version":1}', b'['*1000):
            with self.subTest(raw=raw[:30]), self.assertRaises(ValueError):
                decode(raw)

    def test_missing_extra_fields(self):
        p = packet('test', 0, 0)
        p['extra'] = 1
        with self.assertRaises(ValueError):
            encode(p)
        del p['extra']
        del p['seq']
        with self.assertRaises(ValueError):
            encode(p)


class ReceiverTests(unittest.TestCase):
    def test_udp_recovery_and_preservation_of_sequence(self):
        output = io.StringIO()
        result = {}
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            receiver.bind(('127.0.0.1', 0))
            def run():
                result.update(receive(receiver, output, idle_timeout=2, max_packets=3))
            thread = threading.Thread(target=run)
            thread.start()
            sender.sendto(b'bad', receiver.getsockname())
            for seq in (2, 2, 0):
                p = packet('test', seq, 0)
                if seq == 2:
                    p.update(version=2, diagnostics=dict(send_ok=2, send_errors=0, last_result=0, net_errno=0))
                sender.sendto(encode(p), receiver.getsockname())
            thread.join(4)
            self.assertFalse(thread.is_alive())
        self.assertEqual(result, {'accepted': 3, 'rejected': 1})
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r['packet']['seq'] for r in records], [2, 2, 0])
        self.assertTrue(all(r['peer_ip'] == '127.0.0.1' for r in records))
        self.assertEqual(records[0]['packet']['diagnostics']['send_ok'], 2)

    def test_live_diagnostics_preserve_log_and_historical_error(self):
        output, live = io.StringIO(), io.StringIO()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            receiver.bind(('127.0.0.1', 0))
            sender.sendto(b'bad', receiver.getsockname())
            old = packet('v1', 0, 0)
            current = packet('new-session', 0, 0)
            current.update(version=2, diagnostics=dict(send_ok=0, send_errors=0,
                           last_result=0x804101CD - 2**32, net_errno=205))
            for item in (old, current):
                sender.sendto(encode(item), receiver.getsockname())
            result = receive(receiver, output, idle_timeout=2, max_packets=2, live_output=live)
            sender.settimeout(0.02)
            with self.assertRaises(socket.timeout):
                sender.recvfrom(1024)  # Reception must never send replies.
        self.assertEqual(result, {'accepted': 2, 'rejected': 1})
        self.assertEqual([json.loads(line)['packet'] for line in output.getvalue().splitlines()], [old, current])
        lines = live.getvalue().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn('STT/1: sin diagnostico', lines[0])
        self.assertIn('sesion=new-session muestra=0', lines[1])
        self.assertIn('intentos previos: env=0 err=0', lines[1])
        self.assertIn('ultimo error conservado=0x804101CD detalle=0x000000CD', lines[1])

    def test_total_duration_bounds_continuous_valid_and_invalid_traffic(self):
        class ClockSocket:
            now = 0.0
            def settimeout(self, seconds):
                self.timeout = seconds
            def recvfrom(self, size):
                if self.timeout < 0.4:
                    self.now += self.timeout
                    raise socket.timeout()
                self.now += 0.4
                return self.raw, ('127.0.0.1', 1234)
        for raw, expected in ((encode(packet('continuous', 0, 0)),
                               {'accepted': 2, 'rejected': 0}),
                              (b'{', {'accepted': 0, 'rejected': 2})):
            with self.subTest(raw=raw):
                sock = ClockSocket()
                sock.raw = raw
                with patch('stt_monitor.receiver.time.monotonic', side_effect=lambda: sock.now):
                    result = receive(sock, io.StringIO(), idle_timeout=5, duration=1)
                self.assertEqual(result, expected)
                self.assertAlmostEqual(sock.now, 1)

    def test_byte_limit_exact_boundary_and_no_silent_discard(self):
        class DatagramSocket:
            calls = 0
            def settimeout(self, seconds):
                pass
            def recvfrom(self, size):
                self.calls += 1
                return encode(packet('bounded', 0, 0)), ('127.0.0.1', 1234)
        from datetime import datetime, timezone
        fixed = datetime(2026, 10, 21, tzinfo=timezone.utc)
        def capture(**kwargs):
            output = io.StringIO()
            sock = DatagramSocket()
            with patch('stt_monitor.receiver.datetime') as clock:
                clock.now.return_value = fixed
                result = receive(sock, output, **kwargs)
            return result, output.getvalue(), sock.calls
        _, single, _ = capture(max_packets=1)
        size = len(single.encode('utf-8'))
        result, logged, calls = capture(max_bytes=size, max_packets=1)
        self.assertEqual(logged, single)
        self.assertEqual(result['accepted'], 1)
        result, logged, calls = capture(max_bytes=size*2-1)
        self.assertEqual(result['stop_reason'], 'max_bytes')
        self.assertEqual(result['not_recorded'], 1)
        self.assertEqual(result['bytes_written'], size)
        self.assertEqual(result['accepted'], 1)
        self.assertEqual(logged, single)
        self.assertEqual(calls, 2)
        result, logged, calls = capture(max_bytes=size, initial_bytes=size)
        self.assertEqual(result['not_recorded'], 0)
        self.assertEqual(logged, '')
        self.assertEqual(calls, 0)
        result, logged, _ = capture(max_bytes=size, initial_bytes=1)
        self.assertEqual(result['not_recorded'], 1)
        self.assertEqual(logged, '')

    def test_inactivity(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('127.0.0.1', 0))
            self.assertEqual(receive(sock, io.StringIO(), idle_timeout=0.02),
                             {'accepted': 0, 'rejected': 0})


if __name__ == '__main__':
    unittest.main()

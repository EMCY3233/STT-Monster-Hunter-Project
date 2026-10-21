import io
import json
import socket
import threading
import unittest
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

    def test_inactivity(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(('127.0.0.1', 0))
            self.assertEqual(receive(sock, io.StringIO(), idle_timeout=0.02),
                             {'accepted': 0, 'rejected': 0})


if __name__ == '__main__':
    unittest.main()

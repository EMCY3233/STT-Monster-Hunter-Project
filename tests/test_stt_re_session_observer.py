from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import socket
import struct
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from observe_citra_session import LogTail, read_memory, observe


class SessionTests(unittest.TestCase):
    def test_partial_utf8_and_truncation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/'log'
            tail = LogTail(p)
            self.assertEqual(tail.poll(), [])
            p.write_bytes(b'abc\n\xc3')
            self.assertEqual(tail.poll(), ['abc'])
            with p.open('ab') as f: f.write(b'\xa9\n')
            self.assertEqual(tail.poll(), ['é'])
            p.write_bytes(b'x\n')
            self.assertEqual(tail.poll(), ['x'])

    def test_rpc_only_reads(self):
        with patch('observe_citra_session.secrets.randbits', return_value=7), patch('observe_citra_session.socket.socket') as factory:
            sock = factory.return_value.__enter__.return_value
            sock.recv.return_value = struct.pack('<4I', 1, 7, 1, 4)+b'test'
            self.assertEqual(read_memory(0x100000, 4), b'test')
            sock.send.assert_called_once_with(struct.pack('<6I',1,7,1,8,0x100000,4))
            sock.connect.assert_called_once_with(('127.0.0.1',45987))

    def test_bad_id_and_short_reply_rejected(self):
        for reply in [b'x', struct.pack('<4I',1,8,1,4)+b'test']:
            with patch('observe_citra_session.secrets.randbits', return_value=7), patch('observe_citra_session.socket.socket') as factory:
                factory.return_value.__enter__.return_value.recv.return_value = reply
                with self.assertRaises(ValueError): read_memory(0,4)

    def test_range_bounds(self):
        for address,size in [(0,0),(0,33),(-1,4),(0xffffffff,2)]:
            with self.assertRaises(ValueError): read_memory(address,size)

    def test_timeout_is_receipted_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp, patch('observe_citra_session.read_memory', side_effect=socket.timeout):
            out = Path(tmp)/'out'
            result = observe(Path(tmp)/'absent',out,seconds=0.12,interval=0.1,address=0)
            self.assertGreater(result['memory_failures'],0)
            self.assertEqual(result['memory_successes'],0)
            with self.assertRaises(FileExistsError): observe('absent',out,seconds=0.1)


if __name__ == '__main__': unittest.main()

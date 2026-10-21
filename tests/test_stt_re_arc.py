"""Synthetic ARC v17 fixtures only; no commercial resource data."""
import importlib.util
from pathlib import Path
import struct
import unittest
import zlib

spec = importlib.util.spec_from_file_location('probe_arc', Path(__file__).parents[1] / 'tools/stt_re/probe_arc.py')
arc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arc)


def fixture(body=b'TEX\x00fixture', path=b'../escape'):
    blob = zlib.compress(body)
    return (struct.pack('<4sHHI', b'ARC\x00', 17, 1, 0) +
            struct.pack('<64sIIII', path, 1, len(blob), len(body) | (2 << 29), 92) + blob)


class ArcProbeTests(unittest.TestCase):
    def test_valid_payload_and_name_not_used_as_destination(self):
        data = fixture()
        entry = arc.parse_table(data)[0]
        self.assertEqual(entry['path'], '../escape')
        self.assertEqual(arc.decode_entry(data, entry), b'TEX\x00fixture')
        self.assertEqual(arc.classify(arc.decode_entry(data, entry)), 'TEX_candidate')

    def test_unsupported_version(self):
        data = bytearray(fixture())
        struct.pack_into('<H', data, 4, 7)
        with self.assertRaises(ValueError):
            arc.parse_table(data)

    def test_truncated_table(self):
        with self.assertRaises(ValueError):
            arc.parse_table(fixture()[:91])

    def test_payload_over_table(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 88, 12)
        with self.assertRaises(ValueError):
            arc.parse_table(data)

    def test_declared_budget(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 84, arc.MAX_ENTRY + 1)
        with self.assertRaises(ValueError):
            arc.parse_table(data)

    def test_decompression_size_lie(self):
        data = bytearray(fixture())
        struct.pack_into('<I', data, 84, 1)
        entry = arc.parse_table(data)[0]
        with self.assertRaises(ValueError):
            arc.decode_entry(data, entry)

    def test_trailing_compressed_data(self):
        data = bytearray(fixture())
        data.extend(b'junk')
        struct.pack_into('<I', data, 80, len(data) - 92)
        entry = arc.parse_table(data)[0]
        with self.assertRaises(ValueError):
            arc.decode_entry(data, entry)

    def test_corrupt_zlib(self):
        data = bytearray(fixture())
        data[-1] ^= 255
        entry = arc.parse_table(data)[0]
        with self.assertRaises(zlib.error):
            arc.decode_entry(data, entry)


if __name__ == '__main__':
    unittest.main()


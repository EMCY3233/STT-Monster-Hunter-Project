"""Synthetic fixtures only: bounds checks are not animation playback tests."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec = importlib.util.spec_from_file_location('headers', Path(__file__).parents[1] / 'tools/stt_re/probe_resource_headers.py')
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def lmt():
    data = bytearray(96)
    struct.pack_into('<4sHHII', data, 0, b'LMT\0', 67, 2, 16, 0)
    struct.pack_into('<IIIi', data, 16, 80, 1, 30, -1)
    return data


class ResourceHeaderTests(unittest.TestCase):
    def test_valid_lmt_and_empty_slot(self):
        result = h.probe_lmt67(lmt())
        self.assertEqual(result['nonempty_slots'], 1)
        self.assertEqual(result['clips'][0]['frames_declared'], 30)
        self.assertIsNone(result['fps'])
        self.assertFalse(result['track_codecs_and_skeleton_binding_validated'])

    def test_truncated_table(self):
        with self.assertRaises(ValueError): h.probe_lmt67(lmt()[:12])

    def test_block_inside_table(self):
        data = lmt(); struct.pack_into('<I', data, 8, 8)
        with self.assertRaises(ValueError): h.probe_lmt67(data)

    def test_block_outside_file(self):
        data = lmt(); struct.pack_into('<I', data, 8, 48)
        with self.assertRaises(ValueError): h.probe_lmt67(data)

    def test_track_pointer_outside_file(self):
        data = lmt(); struct.pack_into('<I', data, 16, 96)
        with self.assertRaises(ValueError): h.probe_lmt67(data)

    def test_unreasonable_counts(self):
        data = lmt(); struct.pack_into('<I', data, 20, 10001)
        with self.assertRaises(ValueError): h.probe_lmt67(data)

    def test_unsupported_lmt(self):
        data = lmt(); struct.pack_into('<H', data, 4, 66)
        with self.assertRaises(ValueError): h.probe_lmt67(data)

    def test_mod_declared_fields(self):
        result = h.probe_mod230(struct.pack('<4s4H3I', b'MOD\0', 230, 14, 2, 1, 100, 200, 300))
        self.assertEqual(result['bone_count_declared'], 14)
        self.assertFalse(result['geometry_and_skeleton_validated'])

    def test_mod_truncated(self):
        with self.assertRaises(ValueError): h.probe_mod230(b'MOD\0')

    def test_mod_unsupported(self):
        with self.assertRaises(ValueError): h.probe_mod230(struct.pack('<4s4H3I', b'MOD\0', 231, 0, 0, 0, 0, 0, 0))


if __name__ == '__main__': unittest.main()


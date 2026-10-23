import hashlib
import json
import math
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

EXE = str(pathlib.Path(sys.argv.pop(1)).resolve())


def fixture(codec=1, payload=None, extremes=None):
    if payload is None:
        payload = struct.pack('<3f', 1., -2., 3.)
    data = bytearray(116+len(payload)+(32 if extremes else 0))
    struct.pack_into('<4sHHI', data, 0, b'LMT\0', 67, 1, 16)
    struct.pack_into('<IIIi', data, 16, 80, 1, 24, -1)
    struct.pack_into('<4BfII4fI', data, 80, codec, 1, 0, 2, 1., len(payload), 116 if payload else 0,
                     0., 0., 0., 0., 116+len(payload) if extremes else 0)
    data[116:116+len(payload)] = payload
    if extremes:
        struct.pack_into('<8f', data, 116+len(payload), *extremes)
    return data


class Motion(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.input = self.root/'input.lmt'
        self.out = self.root/'out'

    def run_case(self, data, ok=True):
        self.input.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        result = subprocess.run([EXE, str(self.input), '--out', str(self.out)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stderr.decode(errors='replace'))
        self.assertEqual(hashlib.sha256(self.input.read_bytes()).hexdigest(), digest)
        if ok:
            report = json.loads((self.out/'report.json').read_text())
            (self.out/'report.json').unlink()
            self.out.rmdir()
            return report
        self.assertFalse(self.out.exists())

    def test_float_vector_keys(self):
        for codec, payload, expected in ((1, struct.pack('<6f', 1, 2, 3, 4, 5, 6), [0, 1]),
                                         (3, struct.pack('<3fI3fI', 1, 2, 3, 7, 4, 5, 6, 3), [0, 7])):
            report = self.run_case(fixture(codec, payload))
            samples = report['tracks'][0]['samples']
            self.assertEqual([s['frame_before_delta'] for s in samples], expected)
            self.assertEqual(samples[1]['xyz'], [4, 5, 6])
            self.assertFalse(report['reference_frame_and_loop_semantics_applied'])

    def test_quantized_scale_offset_not_minmax(self):
        ext = (-2, 4, .5, 0, 10, -1, 0, 0)
        cases = ((4, struct.pack('<4H', 65535, 32768, 0, 9), 65535, 32768),
                 (5, bytes((255, 128, 0, 9)), 255, 128))
        for codec, payload, divisor, middle in cases:
            track = self.run_case(fixture(codec, payload, ext))['tracks'][0]
            self.assertTrue(track['extremes_applied'])
            self.assertEqual(track['samples'][0]['xyz'][0], 8)
            self.assertAlmostEqual(track['samples'][0]['xyz'][1], -1+4*middle/divisor)

    def test_unscaled_quantized_and_zero_delta(self):
        report = self.run_case(fixture(5, bytes((0, 255, 0, 0))))
        self.assertEqual(report['zero_delta_keys'], 1)
        self.assertEqual(report['tracks'][0]['samples'][0]['xyz'], [0, 1, 0])

    def test_unknown_rotation_stays_opaque(self):
        report = self.run_case(fixture(6, b'\xff'*8))
        self.assertEqual(report['decoded_key_occurrences'], 0)
        self.assertEqual(report['unsupported_track_occurrences'], 1)
        self.assertFalse(report['rotation_codecs_decoded'])
        self.assertFalse(report['model_association_verified'])

    def test_empty_slots_and_shared_header(self):
        data = fixture()
        struct.pack_into('<H', data, 6, 2)
        struct.pack_into('<I', data, 12, 16)
        self.assertEqual(self.run_case(data)['distinct_animation_offsets'], 1)
        struct.pack_into('<2I', data, 8, 0, 0)
        report = self.run_case(data)
        self.assertEqual(report['null_slots'], 2)
        self.assertEqual(report['decoded_key_occurrences'], 0)

    def test_interpreted_prefix_tail_reuse(self):
        data = fixture()
        del data[76:80]
        struct.pack_into('<I', data, 16, 76)
        struct.pack_into('<I', data, 88, 112)
        self.assertEqual(self.run_case(data)['decoded_key_occurrences'], 1)
        struct.pack_into('<I', data, 16, 72)
        self.run_case(data, False)

    def test_truncated_records_ranges_overlap(self):
        for codec, n in ((1, 11), (3, 15), (4, 7), (5, 3)):
            self.run_case(fixture(codec, bytes(n)), False)
        for at, value in ((8, 8), (16, 0), (16, 16), (88, 0xffffffff), (92, 0), (92, 16), (112, 116)):
            data = fixture()
            struct.pack_into('<I', data, at, value)
            self.run_case(data, False)

    def test_nonfinite_and_frame_budget(self):
        data = fixture()
        struct.pack_into('<I', data, 116, 0x7fc00000)
        self.run_case(data, False)
        self.run_case(fixture(3, struct.pack('<3fI', 0, 0, 0, 0xffffffff)), False)
        self.run_case(fixture(4, bytes(8), (math.inf, 0, 0, 0, 0, 0, 0, 0)), False)

    def test_no_buffer_does_not_invent_keys(self):
        report = self.run_case(fixture(1, b''))
        self.assertEqual(report['decoded_vector_track_occurrences'], 0)
        self.assertEqual(report['tracks'][0]['samples'], [])

    def test_codec_record_numeric_sampling(self):
        # Exact independent integer-to-rational checkpoints, no encoder round trip.
        for integer in (0, 1, 127, 128, 254, 255):
            sample = self.run_case(fixture(5, bytes((integer, integer, integer, 1))))['tracks'][0]['samples'][0]
            for v in sample['xyz']:
                self.assertAlmostEqual(v, integer/255, delta=1e-15)

    def test_preserve_existing_and_reject_git(self):
        self.input.write_bytes(fixture())
        self.out.mkdir()
        marker = self.out/'marker'
        marker.write_text('keep')
        result = subprocess.run([EXE, str(self.input), '--out', str(self.out)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(marker.read_text(), 'keep')
        marker.unlink()
        self.out.rmdir()
        (self.root/'.git').mkdir()
        self.run_case(fixture(), False)

    def test_profile_budget_and_cli(self):
        self.run_case(b'LMT\0\x44\0\0\0', False)
        self.run_case(b'LMT\0', False)
        data = fixture()
        struct.pack_into('<H', data, 6, 65535)
        self.run_case(data, False)
        data = fixture()
        struct.pack_into('<I', data, 20, 4097)
        self.run_case(data, False)
        self.run_case(fixture(1, struct.pack('<3f', 0, 0, 0)*100001), False)
        for args in ([], ['a'], ['a', '--out'], ['a', '--wrong', 'b']):
            self.assertEqual(subprocess.run([EXE, *args], capture_output=True, timeout=30).returncode, 1)


if __name__ == '__main__':
    unittest.main()

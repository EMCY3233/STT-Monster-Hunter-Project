import hashlib
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

EXE = str(pathlib.Path(sys.argv.pop(1)).resolve())


def fixture(kind=3, width=32, height=16, levels=2):
    payload = bytearray()
    offsets = []
    expected = []
    for level in range(levels):
        offsets.append(len(payload))
        w, h = width >> level, height >> level
        pixels = bytes(v for y in range(h) for x in range(w)
                       for v in ((x * 7 + level) % 256, (y * 13) % 256,
                                 (x + y * 3) % 256,
                                 (x * 17 + y * 31) % 256 if kind == 3 else 255))
        expected.append(pixels)
        # Enumerate physical storage by tiles and Morton positions, independently
        # from the decoder's destination-coordinate loop.
        for ty in range(h // 8):
            for tx in range(w // 8):
                for n in range(64):
                    x = tx * 8 + (n & 1) + ((n >> 1) & 2) + ((n >> 2) & 4)
                    y = ty * 8 + ((n >> 1) & 1) + ((n >> 2) & 2) + ((n >> 3) & 4)
                    r, g, b, a = pixels[(y * w + x) * 4:][:4]
                    payload.extend((a, b, g, r) if kind == 3 else (b, g, r))
    header = struct.pack('<4I', 0x584554, 0x200000a5,
                         levels | width << 6 | height << 19, 0x10001 | kind << 8)
    return header + struct.pack('<' + 'I' * levels, *offsets) + payload, expected


class Tests(unittest.TestCase):
    def run_case(self, data, args=(), good=True):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / 'input.bin'
            source.write_bytes(data)
            before = hashlib.sha256(source.read_bytes()).digest()
            out = root / 'result'
            run = subprocess.run([EXE, str(source), '--out', str(out), *args],
                                 capture_output=True)
            self.assertEqual(run.returncode == 0, good, run.stderr)
            self.assertEqual(hashlib.sha256(source.read_bytes()).digest(), before)
            if good:
                pam = (out / 'image.pam').read_bytes()
                self.assertTrue(pam.startswith(b'P7\n'))
                return pam.split(b'ENDHDR\n', 1)[1]
            self.assertFalse(out.exists())

    def test_pixels_and_alpha(self):
        for kind in (3, 17):
            data, expected = fixture(kind)
            self.assertEqual(self.run_case(data), expected[0])
            self.assertEqual(self.run_case(data, ['--mip', '1']), expected[1])

    def test_embedded_range(self):
        data, expected = fixture()
        self.assertEqual(self.run_case(b'prefix!' + data + b'trailer',
                         ['--offset', '7', '--size', str(len(data))]), expected[0])

    def test_malformed_headers_and_tables(self):
        data, _ = fixture()
        for index, value in ((0, 0), (4, 0x200000a6), (4, 0x600000a5),
                             (4, 0x210000a5), (8, 0), (12, 0x10302),
                             (12, 0x10c01), (12, 0x20001), (16, 1), (20, 0)):
            with self.subTest(index=index, value=value):
                bad = bytearray(data)
                struct.pack_into('<I', bad, index, value)
                self.run_case(bad, good=False)

    def test_truncation_and_trailing_data(self):
        data, _ = fixture()
        for size in (0, 4, 15, 19, 23, len(data) - 1):
            self.run_case(data[:size], good=False)
        self.run_case(data + b'X', good=False)

    def test_options(self):
        data, _ = fixture()
        for args in (['--mip', '2'], ['--offset', str(len(data) + 1)],
                     ['--size', '999999999999'], ['--mip', '-1'],
                     ['--mip', '0', '--mip', '1'], ['--unknown', '1']):
            self.run_case(data, args, good=False)

    def test_sub8_mip_rejected(self):
        data, _ = fixture(width=16, height=16, levels=3)
        self.run_case(data, good=False)

    def test_existing_destination_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            source = root / 'input.tex'
            source.write_bytes(fixture()[0])
            out = root / 'out'
            out.mkdir()
            marker = out / 'image.pam'
            marker.write_bytes(b'keep')
            run = subprocess.run([EXE, str(source), '--out', str(out)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertEqual(marker.read_bytes(), b'keep')


if __name__ == '__main__':
    unittest.main()

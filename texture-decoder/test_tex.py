import hashlib
import pathlib
import random
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


def etc_fixture(alpha=True, levels=3):
    """Encode chosen base colors/selectors; expected pixels use those choices,
    not bit extraction from the resulting stream. No external decoder needed.
    """
    magnitudes = ((2, 8), (5, 17), (9, 29), (13, 42),
                  (18, 60), (24, 80), (33, 106), (47, 183))
    payload, offsets, expected = bytearray(), [], []
    serial = 0
    for level in range(levels):
        offsets.append(len(payload))
        width = 32 >> level
        rgba = bytearray(width * width * 4)
        for ty in range(0, width, 8):
            for tx in range(0, width, 8):
                for block in range(4):
                    flip = (serial // 8) % 2
                    differential = (serial // 16) % 2
                    tables = (serial % 8, 7 - serial % 8)
                    info = tables[0] << 5 | tables[1] << 2 | differential << 1 | flip
                    if differential:
                        delta = serial % 8 - 4
                        first = (4, 16, 28)
                        second = tuple(v + delta for v in first)
                        colors = [tuple(v * 8 + v // 4 for v in color)
                                  for color in (first, second)]
                        fields = [(v << 3) | (delta & 7) for v in first]
                    else:
                        colors = [(0, 136, 255), (255, 119, 0)]
                        fields = [0x0f, 0x87, 0xf0]
                    info |= fields[0] << 24 | fields[1] << 16 | fields[2] << 8
                    selectors = a4 = 0
                    for x in range(4):
                        for y in range(4):
                            n = x * 4 + y
                            choice = (x + y + serial) % 4
                            selectors |= (choice & 1) << n | (choice >> 1) << (16 + n)
                            nibble = (n + serial) % 16
                            a4 |= nibble << (4 * n)
                            half = y // 2 if flip else x // 2
                            modifier = magnitudes[tables[half]][choice & 1]
                            modifier *= -1 if choice >= 2 else 1
                            rgb = [max(0, min(255, v + modifier)) for v in colors[half]]
                            dst = ((ty + block // 2 * 4 + y) * width + tx + block % 2 * 4 + x) * 4
                            rgba[dst:dst + 4] = bytes(rgb + [nibble * 17 if alpha else 255])
                    if alpha:
                        payload.extend(struct.pack('<Q', a4))
                    payload.extend(struct.pack('<II', selectors, info))
                    serial += 1
        expected.append(bytes(rgba))
    header = struct.pack('<4I', 0x584554, 0x200000a5,
                         levels | 32 << 6 | 32 << 19, 0x10001 | (12 if alpha else 11) << 8)
    return header + struct.pack('<' + 'I' * levels, *offsets) + payload, expected


def cube_fixture(kind=11):
    offsets, payload, expected = [], bytearray(), []
    for face in range(6):
        face_pixels = []
        if kind in (3, 17):
            normal, pixels = fixture(kind, 32, 32, 3)
            normal_offsets = struct.unpack_from('<3I', normal, 16)
            offsets.extend(len(payload) + o for o in normal_offsets)
            payload.extend((v + face * 3) % 256 for v in normal[28:])
            for rgba in pixels:
                face_pixels.append(bytes((v + face * 3) % 256 if kind == 3 or i % 4 != 3
                                         else 255 for i, v in enumerate(rgba)))
        else:
            for mip in range(3):
                offsets.append(len(payload))
                width = 32 >> mip
                r, g, b = face + 1, mip + 1, 8
                info = r * 0x11 << 24 | g * 0x11 << 16 | b * 0x11 << 8
                block = struct.pack('<II', 0, info)
                a = (face * 3 + mip) % 16 if kind == 12 else 15
                if kind == 12:
                    block = bytes([a * 17]) * 8 + block
                payload.extend(block * (width * width // 16))
                face_pixels.append(bytes((r * 17 + 2, g * 17 + 2, b * 17 + 2, a * 17))
                                   * (width * width))
        expected.append(face_pixels)
    header = struct.pack('<4I', 0x584554, 0x600400a5, 3 | 32 << 6 | 32 << 19,
                         0x10006 | kind << 8)
    # Opaque metadata is deliberately nonzero: content is not given axis semantics.
    return header + bytes(range(108)) + struct.pack('<18I', *offsets) + payload, expected


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
                             (12, 0x10601), (12, 0x20001), (16, 1), (20, 0)):
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

    def test_etc_modes_tables_tiles_mips_and_alpha(self):
        for alpha in (False, True):
            data, expected = etc_fixture(alpha)
            for mip, pixels in enumerate(expected):
                with self.subTest(alpha=alpha, mip=mip):
                    self.assertEqual(self.run_case(data, ['--mip', str(mip)]), pixels)

    def test_etc_known_zero_block_and_alpha_extremes(self):
        for kind, block, pixel in ((11, bytes(8), bytes((2, 2, 2, 255))),
                                   (12, bytes(16), bytes((2, 2, 2, 0))),
                                   (12, b'\xff' * 8 + bytes(8), bytes((2, 2, 2, 255)))):
            header = struct.pack('<5I', 0x584554, 0x200000a5,
                                 1 | 8 << 6 | 8 << 19, 0x10001 | kind << 8, 0)
            self.assertEqual(self.run_case(header + block * 4), pixel * 64)

    def test_etc_invalid_differential_colors(self):
        header = struct.pack('<5I', 0x584554, 0x200000a5,
                             1 | 8 << 6 | 8 << 19, 0x10b01, 0)
        for channel in range(3):
            for field in (0x07, 0xfb):  # base 0 delta -1 / base 31 delta +3
                info = 2 | field << (24 - channel * 8)
                self.run_case(header + struct.pack('<II', 0, info) * 4, good=False)

    def test_etc_bad_offsets_truncation_and_trailing(self):
        data, _ = etc_fixture()
        for cut in (1, 8, 16, 64):
            self.run_case(data[:-cut], good=False)
        self.run_case(data + b'\0', good=False)
        bad = bytearray(data)
        struct.pack_into('<I', bad, 20, 1)
        self.run_case(bad, good=False)

    def test_etc_reference_random_vectors(self):
        # Golden RGBA hashes independently obtained with texture2ddecoder 1.0.6
        # for RGB, plus byte/nibble alpha expansion. No backend needed in CI.
        rng = random.Random(0xA5)
        hashes = ('110d6f3ad9bc09df0030f63d27ff5903ccaad46c9d6d868b2d03f332b7e6fc37',
                  'bbbb33ec64ff46ddf244fc2a1da3c4a1cc395070051f70bc1a2df7c5b4ca4836')
        for alpha, wanted in zip((False, True), hashes):
            data = bytearray(struct.pack('<5I', 0x584554, 0x200000a5,
                             1 | 128 << 6 | 128 << 19, 0x10001 | (12 if alpha else 11) << 8, 0))
            for _ in range(1024):
                info = rng.getrandbits(8)
                for shift in (24, 16, 8):
                    if info & 2:
                        first = rng.randrange(32)
                        delta = rng.choice([v for v in range(-4, 4) if 0 <= first + v <= 31])
                        field = first * 8 + (delta & 7)
                    else:
                        field = rng.randrange(256)
                    info |= field << shift
                if alpha:
                    data.extend(rng.getrandbits(64).to_bytes(8, 'little'))
                data.extend(struct.pack('<II', rng.getrandbits(32), info))
            self.assertEqual(hashlib.sha256(self.run_case(data)).hexdigest(), wanted)

    def test_cube_every_face_and_mip(self):
        for kind in (3, 17, 11, 12):
            data, expected = cube_fixture(kind)
            for face in range(6):
                for mip in range(3):
                    with self.subTest(kind=kind, face=face, mip=mip):
                        self.assertEqual(self.run_case(data, ['--face', str(face), '--mip', str(mip)]),
                                         expected[face][mip])

    def test_cube_rejects_bad_selection_and_metadata(self):
        data, _ = cube_fixture()
        for args in (['--face', '6'], ['--face', '-1'], ['--face', '0', '--face', '1']):
            self.run_case(data, args, good=False)
        self.run_case(fixture()[0], ['--face', '1'], good=False)
        for pos, value in ((8, 3 | 32 << 6 | 16 << 19), (12, 0x10b05),
                           (12, 0x10b01), (124, 1), (124 + 17 * 4, 0)):
            bad = bytearray(data)
            struct.pack_into('<I', bad, pos, value)
            self.run_case(bad, good=False)

    def test_cube_truncated_table_payload_and_trailing(self):
        data, _ = cube_fixture()
        for cut in (16, 123, 124, 195, len(data) - 1):
            self.run_case(data[:cut], good=False)
        self.run_case(data + b'X', good=False)


if __name__ == '__main__':
    unittest.main()

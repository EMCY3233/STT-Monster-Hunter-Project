import hashlib
import json
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib

EXE = str(pathlib.Path(sys.argv.pop(1)).resolve())


def model(indices=(0, 1, 2, 3), start=0):
    nv = start + 4
    b = bytearray(336 + nv * 28 + len(indices) * 2)
    b[:4] = b'MOD\0'
    struct.pack_into('<4H', b, 4, 230, 0, 1, 1)
    for pos, value in ((12, nv), (16, len(indices)), (24, nv * 28), (32, 1),
                       (44, 128), (48, 160), (52, 288), (56, 336), (60, 336 + nv * 28)):
        struct.pack_into('<I', b, pos, value)
    b[160:165] = b'mat0\0'
    struct.pack_into('<HH8IBBHHHI', b, 288, 0, 4, 0, 28 << 16 | 4 << 24,
                     start, 0, 0x59dc400b, 0, len(indices), 0, 0, 0, 0, start, start + 3, 0)
    for i, p in enumerate(((0., 0., 0.), (1., 0., 0.), (0., 1., 0.), (1., 1., 0.))):
        at = 336 + (start + i) * 28
        struct.pack_into('<3f4b2f4b', b, at, *p, 0, 0, 127, 0, p[0], p[1], 0, 0, 0, 0)
    struct.pack_into('<' + 'H' * len(indices), b, 336 + nv * 28, *indices)
    return b


def mrl():
    b = bytearray(264)
    struct.pack_into('<7I', b, 0, 0x004c524d, 32, 1, 2, 0, 28, 180)
    struct.pack_into('<I', b, 28, 0x241f5deb)
    b[40:56] = b'texture/example\0'
    struct.pack_into('<I', b, 184, (~zlib.crc32(b'mat0')) & 0xffffffff)
    struct.pack_into('<I', b, 188, 24)
    struct.pack_into('<I', b, 204, 2)
    struct.pack_into('<I', b, 232, 240)
    struct.pack_into('<6I', b, 240, 3, 1, 99, 5, 1234, 100)
    return b


class Tests(unittest.TestCase):
    def run_case(self, data, material=None, good=True):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            src = root / 'source.mod'
            src.write_bytes(data)
            before = hashlib.sha256(src.read_bytes()).digest()
            out = root / 'result'
            args = [EXE, str(src), '--out', str(out)]
            if material is not None:
                path = root / 'source.mrl'
                path.write_bytes(material)
                args += ['--mrl', str(path)]
            run = subprocess.run(args, capture_output=True)
            self.assertEqual(run.returncode == 0, good, run.stderr)
            self.assertEqual(hashlib.sha256(src.read_bytes()).digest(), before)
            if material is not None:
                self.assertEqual(path.read_bytes(), material)
            if not good:
                self.assertFalse(out.exists())
                return
            obj = (out / 'model.obj').read_text()
            report = json.loads((out / 'report.json').read_text())
            self.assertNotIn('map_Kd', (out / 'materials.mtl').read_text())
            return obj, report

    def test_quad_positions_uv_normals_winding(self):
        obj, report = self.run_case(model(), mrl())
        self.assertEqual([line for line in obj.splitlines() if line.startswith('f ')],
                         ['f 1/1/1 2/2/2 3/3/3', 'f 3/3/3 2/2/2 4/4/4'])
        self.assertIn('v 1 1 0\n', obj)
        self.assertIn('vt 1 1\n', obj)
        self.assertEqual(obj.count('vn 0 0 1\n'), 4)
        self.assertEqual((report['vertices'], report['triangles']), (4, 2))
        self.assertEqual(report['materials'][0]['mrl_record_matches'], 1)
        self.assertEqual(report['materials'][0]['candidate_resource_slots'][0]['path'], 'texture/example')
        self.assertFalse(report['textures_assigned'])

    def test_nonzero_vertex_start(self):
        obj, report = self.run_case(model((3, 4, 5, 6), 3))
        self.assertEqual(report['triangles'], 2)
        self.assertIn('f 1/1/1 2/2/2 3/3/3', obj)

    def test_restart_and_parity_after_degenerates(self):
        obj, report = self.run_case(model((0, 1, 2, 65535, 0, 1, 1, 2, 3)))
        self.assertEqual(report['triangles'], 2)
        self.assertEqual(report['meshes'][0]['repeated_index_triangles_removed'], 2)
        self.assertIn('f 2/2/2 3/3/3 4/4/4', obj)

    def test_zero_area_removed(self):
        data = model()
        struct.pack_into('<3f', data, 336 + 2 * 28, 2., 0., 0.)
        _, report = self.run_case(data)
        self.assertEqual(report['meshes'][0]['zero_area_triangles_removed'], 1)

    def test_bad_indices_and_nonfinite_attributes(self):
        self.run_case(model((0, 1, 9)), good=False)
        for offset in (336, 336 + 16):
            bad = model()
            struct.pack_into('<f', bad, offset, float('nan'))
            self.run_case(bad, good=False)

    def test_bad_layout_skin_material_and_ranges(self):
        for at, size, value in ((4, 2, 231), (6, 2, 1), (36, 4, 1), (308, 4, 0),
                                 (296, 4, 24 << 16 | 4 << 24), (292, 4, 1 << 12),
                                 (296, 4, 28 << 16 | 4 << 24 | 8), (56, 4, 128),
                                 (60, 4, 9999), (16, 4, 9999)):
            bad = model()
            struct.pack_into('<H' if size == 2 else '<I', bad, at, value)
            self.run_case(bad, good=False)

    def test_truncations_and_global_shortfall_policy(self):
        data = model()
        for size in (0, 64, 127, 200, len(data) - 1, len(data) - 2):
            self.run_case(data[:size], good=False)
        struct.pack_into('<I', data, 16, 5)
        _, report = self.run_case(data)
        self.assertEqual(report['global_index_shortfall_bytes'], 2)

    def test_mrl_rejects_invalid_ranges_and_strings(self):
        for at, value in ((4, 33), (12, 4097), (20, 0), (24, 28), (188, 99999),
                          (204, 4095), (232, 28)):
            bad = mrl()
            struct.pack_into('<I', bad, at, value)
            self.run_case(model(), bad, good=False)
        bad = mrl()
        bad[40:104] = b'X' * 64
        self.run_case(model(), bad, good=False)

    def test_unmatched_hash_and_unresolved_descriptor_are_reported(self):
        data = mrl()
        struct.pack_into('<I', data, 184, 123)
        _, report = self.run_case(model(), data)
        self.assertEqual(report['materials'][0]['mrl_record_matches'], 0)
        data = mrl()
        struct.pack_into('<I', data, 244, 9999)
        _, report = self.run_case(model(), data)
        self.assertFalse(report['materials'][0]['candidate_resource_slots'][0]['one_based_index_in_range'])

    def test_existing_output_and_bad_cli_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            src = root / 'source.mod'
            src.write_bytes(model())
            out = root / 'output'
            out.mkdir()
            marker = out / 'model.obj'
            marker.write_text('keep')
            for args in (['--out', str(out)], ['--out'], ['--out', '--mrl'],
                         ['--out', str(out), '--out', str(out)], ['--other', 'x']):
                run = subprocess.run([EXE, str(src), *args], capture_output=True)
                self.assertNotEqual(run.returncode, 0)
                self.assertEqual(marker.read_text(), 'keep')

    def test_multiple_mesh_global_obj_indices(self):
        original = model()
        data = bytearray(624)
        data[:336] = original[:336]
        struct.pack_into('<H', data, 8, 2)
        for pos, value in ((12, 8), (16, 8), (24, 224), (56, 384), (60, 608)):
            struct.pack_into('<I', data, pos, value)
        data[336:384] = original[288:336]
        struct.pack_into('<I', data, 336 + 12, 4)
        struct.pack_into('<I', data, 336 + 24, 4)
        data[384:496] = original[336:448]
        data[496:608] = original[336:448]
        struct.pack_into('<8H', data, 608, *range(8))
        obj, report = self.run_case(data)
        self.assertEqual((report['vertices'], report['triangles']), (8, 4))
        self.assertIn('f 5/5/5 6/6/6 7/7/7', obj)

    def test_ambiguous_material_hash_is_not_resolved(self):
        data = mrl()
        # Duplicate records share a name hash but have disjoint descriptor blocks.
        material_record = bytes(data[180:240])
        data[180:240] = material_record * 2
        struct.pack_into('<I', data, 8, 2)
        struct.pack_into('<I', data, 232, 300)
        struct.pack_into('<I', data, 292, 324)
        data.extend(bytes(24))
        _, report = self.run_case(model(), data)
        self.assertEqual(report['materials'][0]['mrl_record_matches'], 2)
        self.assertEqual(report['materials'][0]['candidate_resource_slots'], [])

    def test_rejects_asset_output_under_git_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            src = root / 'input.mod'
            src.write_bytes(model())
            (root / '.git').mkdir()
            out = root / 'assets'
            run = subprocess.run([EXE, str(src), '--out', str(out)], capture_output=True)
            self.assertNotEqual(run.returncode, 0)
            self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()

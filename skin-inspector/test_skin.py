import hashlib
import json
import math
import pathlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest

EXE = str(pathlib.Path(sys.argv.pop(1)).resolve())


def fixture(two=False, unknown=False):
    stride = 28 if two else 36
    meshes = 2 if unknown else 1
    bone, group, material, mesh = 128, 716, 748, 876
    vb = mesh+meshes*48
    ib = vb+4*stride
    data = bytearray(ib+6)
    data[:4] = b'MOD\0'
    struct.pack_into('<4H', data, 4, 230, 2, meshes, 1)
    for at, value in ((12, 4), (16, 3), (24, 4*stride), (32, 1), (36, 1),
                      (40, bone), (44, group), (48, material), (52, mesh), (56, vb), (60, ib)):
        struct.pack_into('<I', data, at, value)
    data[bone+1] = 255
    data[bone+24] = 1
    for table in (bone+48, bone+176):
        for i in range(2):
            struct.pack_into('<16f', data, table+i*64, *[float(r == c) for r in range(4) for c in range(4)])
    struct.pack_into('<I', data, 688, 2)
    data[692:694] = bytes((0, 1))
    for i in range(meshes):
        at = mesh+i*48
        struct.pack_into('<H', data, at+2, 4)
        struct.pack_into('<I', data, at+8, stride << 16 | 4 << 24 | (2 if two else 4) << 3)
        struct.pack_into('<I', data, at+20, 0xdeadbeef if i else (0xd6784014 if two else 0x01b36016))
        struct.pack_into('<I', data, at+28, 3)
    for i, position in enumerate(((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 0))):
        at = vb+i*stride
        struct.pack_into('<3f', data, at, *position)
        if i < 3:
            data[at+24:at+28] = bytes((0, 1, 128, 127))
        # Unused zero-weight slots can contain arbitrary bytes.
        if not two:
            data[at+32:at+34] = b'\xff\xff'
    struct.pack_into('<3H', data, ib, 0, 1, 2)
    return data


def profile_fixture(fmt):
    two = fmt in (0xd6784014, 0x43fb3015, 0x7ba7401b)
    data = fixture(two=two)
    if fmt in (0x43fb3015, 0x7ba7401b):
        vb, ib = struct.unpack_from('<2I', data, 56)
        data[vb:ib] = b''.join(data[vb+i*28:vb+(i+1)*28]+bytes(4) for i in range(4))
        struct.pack_into('<I', data, 24, 128)
        struct.pack_into('<I', data, 60, ib+16)
        struct.pack_into('<I', data, 884, 32 << 16 | 4 << 24 | 2 << 3)
    struct.pack_into('<I', data, 896, fmt)
    return data


class Skin(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.source = self.root/'source.mod'
        self.destination = self.root/'out'

    def run_case(self, data, ok=True, rest=False):
        self.source.write_bytes(data)
        before = hashlib.sha256(data).hexdigest()
        args = [EXE, str(self.source), '--out', str(self.destination)]
        if rest:
            args.append('--check-rest-pose')
        result = subprocess.run(args, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 0 if ok else 1, result.stderr.decode(errors='replace'))
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), before)
        if ok:
            value = json.loads((self.destination/'report.json').read_text())
            (self.destination/'report.json').unlink()
            self.destination.rmdir()
            return value
        self.assertFalse(self.destination.exists())

    def test_valid_profiles(self):
        for two in (False, True):
            with self.subTest(two=two):
                report = self.run_case(fixture(two))
                self.assertEqual(report['referenced_vertex_records'], 3)
                self.assertEqual(report['unused_zero_weight_records'], 1)
                self.assertFalse(report['functional_skinning_verified'])
                self.assertFalse(report['palette_semantics_verified'])

    def test_four_influence_grouped_offsets(self):
        data = fixture()
        vb = struct.unpack_from('<I', data, 56)[0]
        data[vb+26:vb+28] = bytes((64, 64))
        data[vb+32:vb+36] = bytes((0, 1, 64, 63))
        report = self.run_case(data)
        self.assertEqual(report['active_influences'], 8)

    def test_f606_profile_and_partial_flag(self):
        data = fixture()
        struct.pack_into('<I', data, 896, 0xf606f017)
        report = self.run_case(data)
        self.assertFalse(report['has_unsupported_meshes'])
        self.assertTrue(report['vertex_counts_are_window_occurrences'])
        self.assertEqual(report['meshes'][0]['stride'], 36)
        self.assertTrue(self.run_case(fixture(unknown=True))['has_unsupported_meshes'])

    def test_two_influence_32_byte_profiles(self):
        for fmt in (0x43fb3015, 0x7ba7401b):
            data = fixture(two=True)
            vb, ib = struct.unpack_from('<2I', data, 56)
            vertices = [data[vb+i*28:vb+(i+1)*28] + bytes((1, 2, 3, 4)) for i in range(4)]
            data[vb:ib] = b''.join(vertices)
            struct.pack_into('<I', data, 24, 128)
            struct.pack_into('<I', data, 60, ib+16)
            struct.pack_into('<I', data, 884, 32 << 16 | 4 << 24 | 2 << 3)
            struct.pack_into('<I', data, 896, fmt)
            report = self.run_case(data)
            self.assertEqual(report['referenced_active_influences'], 6)
            self.assertEqual(report['meshes'][0]['stride'], 32)
            # The profile identifier does not authorize a mismatched stride.
            struct.pack_into('<I', data, 884, 28 << 16 | 4 << 24 | 2 << 3)
            self.run_case(data, False)

    def test_referenced_influence_counter(self):
        data = fixture()
        vb = struct.unpack_from('<I', data, 56)[0]
        data[vb+3*36+24:vb+3*36+28] = bytes((0, 255, 1, 0))
        report = self.run_case(data)
        self.assertEqual(report['active_influences'], 7)
        self.assertEqual(report['referenced_active_influences'], 6)
        self.assertEqual(report['unused_zero_weight_records'], 0)

    def test_oversized_source_rejected_without_output(self):
        with self.source.open('wb') as source:
            source.truncate((32 << 20)+1)
        result = subprocess.run([EXE, str(self.source), '--out', str(self.destination)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b'input budget', result.stderr)
        self.assertFalse(self.destination.exists())

    def test_rest_disabled_and_nonidentity_common_transform(self):
        self.assertEqual(self.run_case(fixture())['rest_pose_diagnostic']['status'], 'disabled')
        data = fixture()
        for at in (304, 368):  # both B matrices share model-space offset
            struct.pack_into('<f', data, at+48, 5)
        report = self.run_case(data, rest=True)['rest_pose_diagnostic']
        self.assertEqual(report['status'], 'computed_under_hypothesis')
        self.assertEqual(report['compared_records'], 3)
        self.assertLess(report['max_absolute_xyz_error'], 1e-12)

    def test_rest_hierarchy_order_and_broken_bind(self):
        data = fixture()
        struct.pack_into('<f', data, 176, 2)  # root local x scale
        struct.pack_into('<f', data, 240+48, 1)  # child local x translation
        for at in (304, 368):
            struct.pack_into('<f', data, at, .5)
        struct.pack_into('<f', data, 368+48, -1)
        self.assertLess(self.run_case(data, rest=True)['rest_pose_diagnostic']['max_absolute_xyz_error'], 1e-12)
        struct.pack_into('<f', data, 368+48, 0)
        report = self.run_case(data, rest=True)['rest_pose_diagnostic']
        self.assertAlmostEqual(report['max_absolute_xyz_error'], 2*127/255)
        self.assertFalse(report['palette_identity_verified'])

    def test_rest_cannot_prove_palette_or_weight_identity(self):
        data = fixture()
        struct.pack_into('<f', data, 240+48, 1)
        struct.pack_into('<f', data, 368+48, -1)
        data[692:694] = bytes((1, 0))
        vb = struct.unpack_from('<I', data, 56)[0]
        for i in range(3):
            data[vb+i*36+26:vb+i*36+28] = bytes((255, 0))
        report = self.run_case(data, rest=True)['rest_pose_diagnostic']
        self.assertLess(report['max_absolute_xyz_error'], 1e-12)
        self.assertFalse(report['palette_identity_verified'])
        self.assertFalse(report['weight_distribution_verified'])

    def test_rest_multiple_roots_and_nonaffine_unavailable(self):
        data = fixture()
        data[153] = 255
        report = self.run_case(data, rest=True)['rest_pose_diagnostic']
        self.assertEqual(report['status'], 'unavailable_multiple_roots')
        self.assertIsNone(report['max_absolute_xyz_error'])
        self.assertEqual(report['compared_records'], 0)
        data = fixture()
        struct.pack_into('<f', data, 176+12, .25)
        report = self.run_case(data, rest=True)['rest_pose_diagnostic']
        self.assertEqual(report['status'], 'unavailable_non_affine')
        self.assertIsNone(report['max_relative_xyz_error'])

    def test_rest_still_requires_valid_weights(self):
        data = fixture()
        vb = struct.unpack_from('<I', data, 56)[0]
        data[vb+26] = 0
        self.run_case(data, False, rest=True)

    def test_rest_singular_common_transform_is_not_evidence(self):
        data = fixture()
        for at in (304, 368):
            struct.pack_into('<f', data, at, 0)
        report = self.run_case(data, rest=True)['rest_pose_diagnostic']
        self.assertEqual(report['status'], 'unavailable_singular_common_transform')
        self.assertEqual(report['common_linear_determinant'], 0)
        self.assertEqual(report['compared_records'], 0)
        self.assertIsNone(report['max_absolute_xyz_error'])
        self.assertEqual(self.run_case(fixture(), rest=True)['rest_pose_diagnostic']['common_linear_determinant'], 1)

    def test_bone_ids_are_not_parent_or_palette_slots(self):
        data = fixture()
        data[128], data[152] = 5, 200
        report = self.run_case(data)
        self.assertEqual(report['bone_index_ids_raw'], [5, 200])
        self.assertTrue(report['bone_index_ids_unique'])
        self.assertFalse(report['bone_index_ids_equal_slots'])
        self.assertTrue(report['parent_references_use_record_slots'])
        self.assertFalse(report['motion_association_verified'])

    def test_duplicate_bone_ids_reported_without_invented_mapping(self):
        data = fixture()
        data[152] = 0
        report = self.run_case(data)
        self.assertFalse(report['bone_index_ids_unique'])
        self.assertEqual(report['bone_index_ids_raw'], [0, 0])
        self.assertEqual(report['referenced_vertex_records'], 3)

    def test_seeded_valid_profile_campaign(self):
        rng = random.Random(23067)
        formats = (0x01b36016, 0xf606f017, 0xd6784014, 0x43fb3015, 0x7ba7401b)
        for case in range(64):
            fmt = formats[case % len(formats)]
            data = profile_fixture(fmt)
            data[128], data[152] = rng.randrange(256), rng.randrange(256)
            vb = struct.unpack_from('<I', data, 56)[0]
            stride = data[886]
            offsets_i = (24, 25, 32, 33) if stride == 36 else (24, 25)
            offsets_w = (26, 27, 34, 35) if stride == 36 else (26, 27)
            for vertex in range(3):
                p = vb+vertex*stride
                struct.pack_into('<3f', data, p, *(rng.uniform(-1000, 1000) for _ in range(3)))
                cuts = sorted([0, 255] + [rng.randrange(256) for _ in range(len(offsets_w)-1)])
                weights = [b-a for a, b in zip(cuts, cuts[1:])]
                for index, weight, oi, ow in zip((rng.randrange(2) for _ in weights), weights, offsets_i, offsets_w):
                    data[p+oi], data[p+ow] = index, weight
            with self.subTest(case=case, format=hex(fmt)):
                report = self.run_case(data, rest=True)
                self.assertEqual(report['referenced_vertex_records'], 3)
                self.assertFalse(report['functional_skinning_verified'])

    def test_seeded_malformed_profile_campaign(self):
        rng = random.Random(670230)
        for case in range(64):
            data = fixture()
            vb = struct.unpack_from('<I', data, 56)[0]
            mode = case % 8
            if mode == 0:
                del data[rng.randrange(len(data)):]
            elif mode == 1:
                struct.pack_into('<H', data, 6, 256)
            elif mode == 2:
                data[153] = 1
            elif mode == 3:
                data[vb+26] -= rng.randrange(1, 128)
            elif mode == 4:
                data[913] = rng.randrange(1, 256)
            elif mode == 5:
                struct.pack_into('<I', data, vb, 0x7fc00000 | rng.randrange(0x10000))
            elif mode == 6:
                struct.pack_into('<I', data, 888, 0xffffffff)
            else:
                struct.pack_into('<H', data, len(data)-2, rng.randrange(4, 65535))
            with self.subTest(case=case, defect=mode):
                self.run_case(data, False, rest=True)

    def test_cpp_pose_perturbation_sweep_against_scalar_oracle(self):
        # This evaluates the C++ diagnostic on synthetic perturbed matrices;
        # it does not turn the diagnostic into an animation player.
        points = ((0., 0.), (1., 0.), (0., 1.))
        for step in range(17):
            angle = -math.pi+step*math.pi/8
            c, s = (struct.unpack('<f', struct.pack('<f', value))[0]
                    for value in (math.cos(angle), math.sin(angle)))
            data = fixture()
            child = (c, s, 0., 0., -s, c, 0., 0., 0., 0., 1., 0., 1., 0., 0., 1.)
            struct.pack_into('<16f', data, 240, *child)
            struct.pack_into('<f', data, 368+48, -1.)
            expected = max(abs(127/255*value) for x, y in points
                           for value in (((x-1)*c-y*s+1)-x, ((x-1)*s+y*c)-y))
            with self.subTest(angle_sample=step):
                report = self.run_case(data, rest=True)['rest_pose_diagnostic']
                self.assertEqual(report['compared_records'], 3)
                self.assertAlmostEqual(report['max_absolute_xyz_error'], expected, delta=1e-12)

    def test_nonzero_start_adjustment_and_stream(self):
        data = fixture()
        vb, ib = struct.unpack_from('<2I', data, 56)
        data[vb:vb] = bytes(108)
        struct.pack_into('<I', data, 12, 7)
        struct.pack_into('<I', data, 24, 252)
        struct.pack_into('<I', data, 60, ib+108)
        struct.pack_into('<I', data, 888, 1)  # vertexStart
        struct.pack_into('<I', data, 892, 36)  # stream offset
        struct.pack_into('<I', data, 908, 1)  # indexValueOffset
        struct.pack_into('<3H', data, ib+108, 1, 2, 3)
        self.assertEqual(self.run_case(data)['referenced_vertex_records'], 3)

    def test_restart_and_empty_reference_rejection(self):
        data = fixture()
        struct.pack_into('<H', data, len(data)-2, 65535)
        self.assertEqual(self.run_case(data)['referenced_vertex_records'], 2)
        struct.pack_into('<3H', data, len(data)-6, 65535, 65535, 65535)
        self.run_case(data, False)
        struct.pack_into('<I', data, 904, 0)
        self.run_case(data, False)

    def test_cycle_with_root_and_direct_bone_domain(self):
        data = fixture()
        data[153] = 1  # self cycle on second bone while first remains a root
        self.run_case(data, False)
        data = fixture()
        struct.pack_into('<I', data, 36, 0)  # opaque former palette bytes remain a gap
        self.assertEqual(self.run_case(data)['skin_palettes'], 0)

    def test_unknown_mesh_explicit(self):
        report = self.run_case(fixture(unknown=True))
        self.assertEqual(report['unsupported_meshes'], 1)
        data = fixture()
        struct.pack_into('<I', data, 896, 0xdeadbeef)
        self.run_case(data, False)

    def test_weight_and_palette_errors(self):
        base = fixture()
        vb = struct.unpack_from('<I', base, 56)[0]
        for at, value in ((vb+26, 0), (vb+24, 2), (vb+34, 1), (913, 1), (692, 2)):
            with self.subTest(at=at):
                data = base[:]
                data[at] = value
                self.run_case(data, False)
        data = base[:]
        data[vb+26:vb+28] = b'\0\0'
        self.run_case(data, False)

    def test_hierarchy(self):
        for at, value in ((129, 2), (129, 0), (129, 1)):
            data = fixture()
            data[at] = value
            self.run_case(data, False)

    def test_ranges_and_nonfinite(self):
        for at, value in ((40, 0), (52, 128), (24, 0xffffffff), (16, 0), (688, 25), (176, 0x7fc00000)):
            data = fixture()
            struct.pack_into('<I', data, at, value)
            self.run_case(data, False)
        self.run_case(fixture()[:100], False)
        data = fixture()
        vb = struct.unpack_from('<I', data, 56)[0]
        struct.pack_into('<I', data, vb+16, 0x7f800000)
        self.run_case(data, False)

    def test_indices_and_shortfall(self):
        data = fixture()
        struct.pack_into('<H', data, len(data)-2, 4)
        self.run_case(data, False)
        data = fixture()
        struct.pack_into('<I', data, 16, 4)
        self.assertEqual(self.run_case(data)['global_index_shortfall_bytes'], 2)
        struct.pack_into('<I', data, 16, 5)
        self.run_case(data, False)

    def test_existing_and_git_destinations(self):
        self.source.write_bytes(fixture())
        self.destination.mkdir()
        sentinel = self.destination/'keep'
        sentinel.write_text('unchanged')
        result = subprocess.run([EXE, str(self.source), '--out', str(self.destination)], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(sentinel.read_text(), 'unchanged')
        (self.root/'.git').mkdir()
        result = subprocess.run([EXE, str(self.source), '--out', str(self.root/'other')], capture_output=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.root/'other').exists())

    def test_cli(self):
        for args in ([], ['a'], ['a', '--out'], ['a', '--unknown', 'b']):
            self.assertEqual(subprocess.run([EXE, *args], capture_output=True, timeout=30).returncode, 1)


if __name__ == '__main__':
    unittest.main()

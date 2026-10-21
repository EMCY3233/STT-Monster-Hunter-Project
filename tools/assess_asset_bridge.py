"""Assess original STT Asset/1 data for a proposed 60 Hz/mm bridge, not an importer.

Executes an explicitly supplied project model evaluator. No sockets or GUI,
no commercial input support, no Vita artifact or target-format output.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import struct
import sys

sys.dont_write_bytecode = True


def nearest_mm(value):
    return math.copysign(math.floor(abs(value) * 1000 + 0.5), value)


def assess(model_path, sample_path):
    spec = importlib.util.spec_from_file_location('stt_asset_bridge_model', model_path)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    data = model.load(sample_path)
    clips = []
    limits = [float('inf')] * 3, [float('-inf')] * 3
    ticks_total = 0
    on_grid = True
    keys_total = 0
    for ci, clip in enumerate(data['clips']):
        duration_ticks = clip['duration'] * 60
        ticks = math.ceil(duration_ticks)
        ticks_total += ticks
        if ticks_total > 4096 or ticks_total * len(data['vertices']) > 2000000:
            raise ValueError('analysis pose/vertex budget exceeded')
        times = [k[0] * 60 for track in clip['tracks'] for k in track['keys']]
        keys_total += len(times)
        grid = all(abs(v - round(v)) < 1e-9 for v in [duration_ticks, *times])
        on_grid &= grid
        loop = model.pose(data, ci, 0) == model.pose(data, ci, clip['duration'])
        for tick in range(ticks):
            joints, vertices = model.pose(data, ci, tick / 60)
            if not all(math.isfinite(v) for p in joints + vertices for v in p):
                raise ValueError('nonfinite sampled pose')
            for vertex in vertices:
                for axis, value in enumerate(vertex):
                    mm = value * 1000
                    limits[0][axis] = min(limits[0][axis], mm)
                    limits[1][axis] = max(limits[1][axis], mm)
        clips.append({'name': clip['name'], 'seconds': clip['duration'], 'duration_times_60': duration_ticks,
                      'sampled_poses': ticks, 'key_times_on_60hz_grid': grid, 'loop_pose_equals_start': loop})
    unit_checks = [(0, 0), (1, 1000), (-1, -1000), (0.0005, 1), (-0.0005, -1)]
    assert all(nearest_mm(x) == expected for x, expected in unit_checks)
    return {'scope': 'Numerical original-project sample assessment only. No importer, resampled asset, GUI/Vita test, telemetry or commercial compatibility claim.',
            'model_sha256': hashlib.sha256(model_path.read_bytes()).hexdigest(),
            'sample_sha256': hashlib.sha256(sample_path.read_bytes()).hexdigest(),
            'format': data['format'], 'version': data['version'],
            'bones': len(data['bones']), 'vertices': len(data['vertices']), 'triangles': len(data['triangles']),
            'clips': clips, 'sampled_poses_total': ticks_total,
            'sampled_world_vertex_bounds_mm': {'min': limits[0], 'max': limits[1]},
            'bounds_are_continuous_extrema': False,
            'all_sample_key_times_on_60hz_grid': on_grid,
            'coordinate_basis_conversion_applied': False,
            'proposed_unit_rounding': 'half away from zero; proposal only, not a target-engine contract',
            'unit_anchor_checks_passed': len(unit_checks),
            'illustrative_packed_payload_bytes': {
                'bone_parent_i16_offset_3i32': len(data['bones']) * struct.calcsize('<hiii'),
                'vertex_position_3i32_bone_u16': len(data['vertices']) * struct.calcsize('<iiiH'),
                'triangle_3u16': len(data['triangles']) * struct.calcsize('<HHH'),
                'key_tick_u32_z_angle_i32': keys_total * struct.calcsize('<Ii')},
            'packed_layout_status': 'Illustrative packing only. Excludes headers, names, runtime/alignment, render buffers and other memory. Not implemented or approved.',
            'asset_to_vita_importer_implemented': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--sample', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = assess(args.model, args.sample)
    with args.report.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))

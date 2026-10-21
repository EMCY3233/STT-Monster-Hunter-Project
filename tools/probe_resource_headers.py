"""Limited MOD230 and LMT67 metadata probes; no geometry or codec decoding.

Field-layout references: RevilLib mtf_mod/header.hpp and mtf_lmt/serialize.cpp,
animation.inl. These independent checks do not run the RevilLib implementation.
"""
import struct


def probe_mod230(data):
    if len(data) < 24:
        raise ValueError('truncated MOD common header')
    magic, version, bones, meshes, materials, vertices, indices, edges = struct.unpack_from('<4s4H3I', data)
    if magic != b'MOD\x00' or version != 230:
        raise ValueError('unsupported MOD signature/version')
    return {'format': 'MOD', 'version': version, 'bone_count_declared': bones,
            'mesh_count_declared': meshes, 'material_count_declared': materials,
            'vertex_count_declared': vertices, 'index_count_declared': indices,
            'edge_count_declared': edges, 'geometry_and_skeleton_validated': False}


def probe_lmt67(data):
    if len(data) < 8:
        raise ValueError('truncated LMT header')
    magic, version, slots = struct.unpack_from('<4sHH', data)
    if magic != b'LMT\x00' or version != 67:
        raise ValueError('unsupported LMT signature/version')
    table_end = 8 + slots * 4
    first_data = (table_end + 15) & ~15
    if table_end > len(data):
        raise ValueError('LMT lookup table outside file')
    clips = []
    offsets = []
    for slot in range(slots):
        offset = struct.unpack_from('<I', data, 8 + slot * 4)[0]
        if offset == 0:
            continue
        if offset < first_data or offset + 64 > len(data):
            raise ValueError('LMT block header outside payload')
        tracks_at, tracks, frames, loop = struct.unpack_from('<IIIi', data, offset)
        if tracks > 10000 or frames > 10000000:
            raise ValueError('LMT counts exceed probe limits')
        if tracks and not (first_data <= tracks_at < len(data)):
            raise ValueError('LMT track pointer outside payload')
        offsets.append(offset)
        clips.append({'slot': slot, 'offset': offset, 'tracks_declared': tracks,
                      'frames_declared': frames, 'loop_frame_declared': loop})
    return {'format': 'LMT', 'version': version, 'pointer_layout_tested': '32-bit little-endian',
            'slots_declared': slots, 'nonempty_slots': len(clips),
            'unique_block_offsets': len(set(offsets)), 'clips': clips,
            'table_and_block_headers_in_bounds': True, 'fps': None,
            'track_codecs_and_skeleton_binding_validated': False}

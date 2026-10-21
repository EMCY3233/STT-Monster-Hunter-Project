"""STT Pose/1 offline bridge. No Vita runtime or combat binding is implied."""
import json
import math
from pathlib import Path
from . import model

MAX_BYTES = 2_097_152
MAX_COORD = 1_000_000
MAX_FRAMES = 600

def integer(value, low, high):
    model.require(type(value) is int and low <= value <= high, 'integer outside bridge bounds')

def mm(value):
    model.require(math.isfinite(value), 'nonfinite coordinate')
    scaled = value * 1000
    result = math.floor(scaled + .5) if scaled >= 0 else math.ceil(scaled - .5)
    integer(result, -MAX_COORD, MAX_COORD)
    return result

def validate(data):
    model.keys(data, 'format version hz basis parents triangles clips')
    model.require(data['format'] == 'STT Pose' and type(data['version']) is int and data['version'] == 1,
                  'unsupported bridge version')
    model.require(type(data['hz']) is int and data['hz'] == 60 and data['basis'] == 'RH_Xright_Yup_Zforward_mm',
                  'unsupported basis or rate')
    parents = data['parents']
    model.require(type(parents) is list and 1 <= len(parents) <= 32, 'bone budget')
    for i, parent in enumerate(parents):
        integer(parent, -1 if i == 0 else 0, i-1)
    triangles = data['triangles']
    model.require(type(triangles) is list and 1 <= len(triangles) <= 512, 'triangle budget')
    clips = data['clips']
    model.require(type(clips) is list and 1 <= len(clips) <= 8, 'clip budget')
    total = 0
    vertex_count = None
    names = set()
    for clip in clips:
        model.keys(clip, 'name frames')
        model.require(model.name(clip['name']) not in names, 'duplicate clip')
        names.add(clip['name'])
        frames = clip['frames']
        model.require(type(frames) is list and len(frames) > 0, 'empty frames')
        total += len(frames)
        model.require(total <= MAX_FRAMES, 'frame budget')
        for frame in frames:
            model.keys(frame, 'joints vertices')
            model.require(type(frame['joints']) is list and len(frame['joints']) == len(parents), 'joint count')
            model.require(type(frame['vertices']) is list and 1 <= len(frame['vertices']) <= 256, 'vertex budget')
            if vertex_count is None:
                vertex_count = len(frame['vertices'])
            model.require(len(frame['vertices']) == vertex_count, 'inconsistent vertex count')
            for point in frame['joints'] + frame['vertices']:
                model.require(type(point) is list and len(point) == 3, 'xyz required')
                for value in point:
                    integer(value, -MAX_COORD, MAX_COORD)
    for triangle in triangles:
        model.require(type(triangle) is list and len(triangle) == 3, 'triangle shape')
        for index in triangle:
            integer(index, 0, vertex_count-1)
        model.require(len(set(triangle)) == 3, 'degenerate index triangle')
    return data

def dumps(data):
    raw = json.dumps(validate(data), separators=(',', ':'), allow_nan=False).encode('utf-8')
    model.require(len(raw) <= MAX_BYTES, 'encoded byte budget')
    return raw

def loads(raw):
    model.require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'input byte budget')
    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=model._pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(model.AssetError('nonfinite JSON')))
        validate(data)
        dumps(data)
        return data
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise model.AssetError('invalid STT Pose/1') from exc

def bake(asset):
    model.validate(asset)
    model.require(len(asset['bones']) <= 32 and len(asset['vertices']) <= 256 and
                  len(asset['triangles']) <= 512 and len(asset['clips']) <= 8, 'source bridge budget')
    counts = []
    for clip in asset['clips']:
        ticks = clip['duration'] * 60
        model.require(abs(ticks-round(ticks)) <= 1e-7, 'duration must be on 60 Hz grid')
        counts.append(round(ticks))
    model.require(all(n > 0 for n in counts) and sum(counts) <= MAX_FRAMES, 'frame budget')
    result = dict(format='STT Pose', version=1, hz=60, basis='RH_Xright_Yup_Zforward_mm',
                  parents=[b['parent'] for b in asset['bones']], triangles=asset['triangles'], clips=[])
    for i, count in enumerate(counts):
        frames = []
        for tick in range(count):
            joints, vertices = model.pose(asset, i, tick/60)
            frames.append({key: [[mm(x) for x in v] for v in points]
                           for key, points in [('joints', joints), ('vertices', vertices)]})
        result['clips'].append(dict(name=asset['clips'][i]['name'], frames=frames))
    dumps(result)
    return result

def frame(data, clip, tick):
    """Caller validates once at import; integer tick wraps, including negative ticks."""
    integer(clip, 0, len(data['clips'])-1)
    model.require(type(tick) is int, 'integer tick required')
    frames = data['clips'][clip]['frames']
    return frames[tick % len(frames)]

def runtime_dumps(data):
    """Canonical C-reader profile of Pose/1; does not change geometry or time.

    C requires this field order and printable ASCII clip names without escapes.
    General Pose/1 readers continue to accept other JSON ordering/Unicode names.
    """
    validate(data)
    for clip in data['clips']:
        model.require(all(32 <= ord(c) <= 126 and c not in '\\"' for c in clip['name']),
                      'C profile requires unescaped printable ASCII clip names')
    canonical = dict(format=data['format'], version=data['version'], hz=data['hz'], basis=data['basis'],
                     parents=data['parents'], triangles=data['triangles'],
                     clips=[dict(name=c['name'], frames=[dict(joints=f['joints'], vertices=f['vertices'])
                             for f in c['frames']]) for c in data['clips']])
    return dumps(canonical)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('destination')
    parser.add_argument('--runtime', action='store_true', help='canonical C-reader JSON profile')
    args = parser.parse_args()
    raw = (runtime_dumps if args.runtime else dumps)(bake(model.load(args.source)))
    with Path(args.destination).open('xb') as stream:
        stream.write(raw)
    print(f'STT Pose/1: {len(raw)} bytes')

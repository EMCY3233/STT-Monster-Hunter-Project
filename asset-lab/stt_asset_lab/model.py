"""Bounded STT Asset/1 reader and rigid-bone animation evaluator (metres, seconds)."""
import json
import math
from pathlib import Path

MAX_BYTES = 1_048_576

class AssetError(ValueError):
    pass

def require(ok, message):
    if not ok:
        raise AssetError(message)

def number(value, limit=10000):
    require(type(value) in (int, float) and abs(value) <= limit and math.isfinite(value),
            'expected bounded finite number')
    return value

def vector(value):
    require(type(value) is list and len(value) == 3, 'expected xyz vector')
    return [number(v) for v in value]

def name(value):
    require(type(value) is str and 0 < len(value) <= 64 and value.isprintable(), 'invalid name')
    return value

def keys(obj, required):
    require(type(obj) is dict and set(obj) == set(required.split()), 'unknown or missing fields')

def validate(data):
    keys(data, 'format version name bones vertices triangles clips')
    require(data['format'] == 'STT Asset' and type(data['version']) is int and data['version'] == 1,
            'unsupported asset contract')
    name(data['name'])
    bones, vertices, triangles, clips = (data[k] for k in ('bones','vertices','triangles','clips'))
    for value, maximum in ((bones,128),(vertices,8192),(triangles,16384),(clips,32)):
        require(type(value) is list and 0 < len(value) <= maximum, 'array size outside contract')
    names = set()
    for i, bone in enumerate(bones):
        keys(bone, 'name parent offset')
        require(name(bone['name']) not in names, 'duplicate bone name')
        names.add(bone['name'])
        require(type(bone['parent']) is int and -1 <= bone['parent'] < i, 'parent must precede child')
        vector(bone['offset'])
    require(bones[0]['parent'] == -1 and all(b['parent'] >= 0 for b in bones[1:]), 'single root required')
    for vertex in vertices:
        keys(vertex, 'position bone')
        vector(vertex['position'])
        require(type(vertex['bone']) is int and 0 <= vertex['bone'] < len(bones), 'invalid bone index')
    for triangle in triangles:
        require(type(triangle) is list and len(triangle) == 3 and len(set(map(str,triangle))) == 3,
                'triangle needs three distinct indices')
        require(all(type(i) is int and 0 <= i < len(vertices) for i in triangle), 'invalid vertex index')
    names.clear()
    for clip in clips:
        keys(clip, 'name duration tracks')
        require(name(clip['name']) not in names, 'duplicate clip name')
        names.add(clip['name'])
        require(0 < number(clip['duration'], 600) <= 600, 'invalid duration')
        tracks = clip['tracks']
        require(type(tracks) is list and len(tracks) <= len(bones), 'invalid track count')
        used = set()
        for track in tracks:
            keys(track, 'bone keys')
            bone = track['bone']
            require(type(bone) is int and 0 <= bone < len(bones) and bone not in used, 'invalid/duplicate track bone')
            used.add(bone)
            frames = track['keys']
            require(type(frames) is list and 1 <= len(frames) <= 1024, 'invalid key count')
            previous = -1
            for frame in frames:
                require(type(frame) is list and len(frame) == 2, 'key must be [seconds, z radians]')
                t, angle = frame
                require(0 <= number(t,600) <= clip['duration'] and t > previous, 'key times must increase')
                number(angle, 100)
                previous = t
            require(frames[0][0] == 0 and frames[-1][0] == clip['duration'], 'keys must span clip duration')
    return data

def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'duplicate JSON field')
        result[key] = value
    return result

def loads(raw):
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'asset exceeds byte budget')
    try:
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(AssetError('non-finite JSON')))
        return validate(data)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise AssetError('invalid JSON or nesting') from exc

def load(path):
    with Path(path).open('rb') as stream:
        return loads(stream.read(MAX_BYTES + 1))

def export(data, path):
    raw = (json.dumps(validate(data), indent=2, allow_nan=False) + '\n').encode()
    require(len(raw) <= MAX_BYTES, 'export exceeds byte budget')
    Path(path).write_bytes(raw)

def pose(data, clip_index, seconds):
    """Linear local Z rotation. Vertices are local to exactly one rigid bone."""
    clip = data['clips'][clip_index]
    t = seconds % clip['duration']
    angles = [0.0] * len(data['bones'])
    for track in clip['tracks']:
        frames = track['keys']
        for (a, x), (b, y) in zip(frames, frames[1:]):
            if a <= t <= b:
                angles[track['bone']] = x + (y-x) * (t-a)/(b-a)
                break
    joints, world_angles = [], []
    def rotate(v, angle):
        c, s = math.cos(angle), math.sin(angle)
        return [c*v[0]-s*v[1], s*v[0]+c*v[1], v[2]]
    for i, bone in enumerate(data['bones']):
        parent = bone['parent']
        angle = 0 if parent < 0 else world_angles[parent]
        offset = rotate(bone['offset'], angle)
        origin = [0,0,0] if parent < 0 else joints[parent]
        joints.append([origin[j]+offset[j] for j in range(3)])
        world_angles.append(angle + angles[i])
    vertices = []
    for v in data['vertices']:
        i = v['bone']
        local = rotate(v['position'], world_angles[i])
        vertices.append([joints[i][j]+local[j] for j in range(3)])
    return joints, vertices

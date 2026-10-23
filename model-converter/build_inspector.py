"""Build a private, self-contained inspector for stt-model output (stdlib only)."""
import argparse
import base64
import hashlib
import json
import math
import pathlib
import struct


def read(path, limit):
    with path.open('rb') as f:
        data = f.read(limit + 1)
    if len(data) > limit:
        raise ValueError('input exceeds budget')
    return data


def build(source, destination, textures=None):
    source, destination = pathlib.Path(source).resolve(), pathlib.Path(destination).resolve()
    if destination.exists() or any((p / '.git').exists() for p in (destination, *destination.parents)):
        raise ValueError('destination exists or is inside Git')
    report = json.loads(read(source / 'report.json', 16 << 20))
    positions, uv, normals, meshes = [], [], [], []
    current = None
    for line in read(source / 'model.obj', 128 << 20).decode('ascii').splitlines():
        fields = line.split()
        if not fields or fields[0].startswith('#'):
            continue
        op, values = fields[0], fields[1:]
        if op in ('v', 'vt', 'vn'):
            size = 2 if op == 'vt' else 3
            numbers = list(map(float, values))
            if len(numbers) != size or not all(math.isfinite(x) and abs(x) <= 1e30 for x in numbers):
                raise ValueError('invalid attribute')
            {'v': positions, 'vt': uv, 'vn': normals}[op].append(numbers)
            if len(positions) > 250000 or len(uv) > 250000 or len(normals) > 250000:
                raise ValueError('vertex budget')
        elif op == 'o':
            if values != ['mesh_' + str(len(meshes))] or len(meshes) >= 4096:
                raise ValueError('invalid mesh order')
            current = {'indices': [], 'material': None}
            meshes.append(current)
        elif op == 'usemtl':
            if current is None or current['material'] is not None or len(values) != 1 or not values[0].startswith('material_'):
                raise ValueError('invalid material')
            current['material'] = int(values[0][9:])
        elif op == 'f':
            if current is None or len(values) != 3:
                raise ValueError('invalid face')
            for value in values:
                ids = list(map(int, value.split('/')))
                if len(ids) != 3 or len(set(ids)) != 1 or not 1 <= ids[0] <= min(len(positions), len(uv), len(normals)):
                    raise ValueError('invalid face index')
                current['indices'].append(ids[0] - 1)
        elif op != 'mtllib':
            raise ValueError('unsupported OBJ directive')
    if not positions or len(positions) != len(uv) or len(positions) != len(normals):
        raise ValueError('missing attributes')
    if len(positions) != report['vertices'] or len(meshes) != len(report['meshes']):
        raise ValueError('report mismatch')
    total = sum(len(m['indices']) for m in meshes)
    if total > 1000000 or total != report['triangles'] * 3:
        raise ValueError('triangle budget or report mismatch')
    for i, (mesh, metadata) in enumerate(zip(meshes, report['meshes'])):
        if metadata['mesh'] != i or mesh['material'] != metadata['material_index'] or len(mesh['indices']) != metadata['triangles'] * 3:
            raise ValueError('mesh report mismatch')
        if not 0 <= mesh['material'] < len(report['materials']):
            raise ValueError('material range')
    images, used = [], 0
    if textures:
        root = pathlib.Path(textures).resolve()
        catalog = json.loads(read(root / 'catalog.json', 1 << 20))
        paths = set()
        for texture in catalog['textures']:
            if len(images) >= 256 or texture['path'] in paths:
                raise ValueError('texture budget or duplicate path')
            paths.add(texture['path'])
            relative = pathlib.Path(texture['png'])
            file = (root / relative).resolve()
            if relative.is_absolute() or '..' in relative.parts or not file.is_relative_to(root):
                raise ValueError('texture path escapes catalog')
            data = read(file, 16 << 20)
            used += len(data)
            if used > 32 << 20 or data[:16] != b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR':
                raise ValueError('invalid PNG or budget')
            width, height = struct.unpack('>II', data[16:24])
            if not 1 <= width <= 4096 or not 1 <= height <= 4096 or (width, height) != (texture['width'], texture['height']):
                raise ValueError('PNG dimensions')
            if hashlib.sha256(data).hexdigest() != texture['png_sha256']:
                raise ValueError('PNG hash mismatch')
            images.append({'path': texture['path'], 'data': 'data:image/png;base64,' + base64.b64encode(data).decode()})
    payload = {'positions': positions, 'uv': uv, 'meshes': meshes, 'report': report, 'textures': images}
    encoded = json.dumps(payload, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    template = pathlib.Path(__file__).with_name('inspector.html').read_text(encoding='utf-8')
    html = template.replace('/*PAYLOAD*/null', encoded).encode('utf-8')
    if len(html) > 64 << 20:
        raise ValueError('HTML budget')
    destination.mkdir(parents=True)
    (destination / 'index.html').write_bytes(html)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=pathlib.Path)
    parser.add_argument('--textures', type=pathlib.Path)
    parser.add_argument('--out', type=pathlib.Path, required=True)
    args = parser.parse_args()
    try:
        build(args.source, args.out, args.textures)
    except (ValueError, KeyError, TypeError, OSError, struct.error) as error:
        parser.exit(1, str(error) + '\n')

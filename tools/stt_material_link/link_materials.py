"""Read-only evidence linker. MRL shader bindings remain unparsed.

Paths inside assets are metadata only, never filesystem destinations.
No external code imports; CRC relation inferred from local samples.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zlib

LIMIT = 32 * 1024 * 1024

def digest(data):
    return hashlib.sha256(data).hexdigest()

def material_names(data):
    if not 64 <= len(data) <= LIMIT or data[:4] != b'MOD\0':
        raise ValueError('MOD size/signature')
    if struct.unpack_from('<H', data, 4)[0] != 230:
        raise ValueError('MOD version')
    count = struct.unpack_from('<H', data, 10)[0]
    start = struct.unpack_from('<I', data, 48)[0]
    if count > 4096 or start < 64 or start + count * 128 > len(data):
        raise ValueError('MOD material range')
    out = []
    for i in range(count):
        field = data[start+i*128:start+(i+1)*128]
        if b'\0' not in field:
            raise ValueError('unterminated material name')
        raw = field.split(b'\0', 1)[0]
        name = raw.decode('ascii')
        out.append(dict(index=i, offset=start+i*128, name=name,
                        complement_crc32=f'{(~zlib.crc32(raw)) & 0xffffffff:08x}'))
    return out

def mrl_evidence(data, textures):
    if not 28 <= len(data) <= LIMIT or data[:4] != b'MRL\0':
        raise ValueError('MRL size/signature')
    if struct.unpack_from('<I', data, 4)[0] != 32:
        raise ValueError('MRL version')
    # Scan explicit NUL-terminated strings only; does NOT claim shader semantics.
    refs = []
    for match in re.finditer(rb'[A-Za-z0-9_\\/.-]{6,}\x00', data):
        raw = match.group()[:-1]
        if b'\\' not in raw and b'/' not in raw:
            continue
        name = raw.decode('ascii')
        refs.append(dict(offset=match.start(), path=name,
                         exact_archive_matches=textures.get(name, [])))
    return refs

def run(root):
    manifest = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    entries = manifest['entries']
    payloads = {}
    for e in entries:
        if Path(e['output_file']).suffix not in ('.mod', '.mrl', '.tex'):
            continue
        p = (root/e['output_file']).resolve()
        if not p.is_relative_to(root.resolve()) or p.stat().st_size > LIMIT:
            raise ValueError('manifest file path/size')
        data = p.read_bytes()
        if digest(data) != e['sha256'] or len(data) != e['observed_bytes']:
            raise ValueError('manifest content mismatch')
        payloads[e['index']] = data
    textures = {}
    materials = []
    models = []
    for e in entries:
        ext = Path(e['output_file']).suffix
        if ext == '.tex':
            textures.setdefault(e['path'], []).append(e['index'])
        elif ext == '.mrl':
            materials.append(e)
    for position, e in enumerate(materials):
        e = dict(e)
        d = payloads[e['index']]
        e['texture_references'] = mrl_evidence(d, textures)
        # Raw aligned words, not an assumed MRL material-table layout.
        e['aligned_words'] = {struct.unpack_from('<I', d, at)[0]: at
                              for at in range(28, len(d)-3, 4)}
        materials[position] = e
    for e in entries:
        if Path(e['output_file']).suffix != '.mod':
            continue
        d = payloads[e['index']]
        row = dict(index=e['index'], path=e['path'], sha256=e['sha256'])
        try:
            row['materials'] = material_names(d)
            for mat in row['materials']:
                h = int(mat['complement_crc32'], 16)
                mat['mrl_hash_occurrences'] = [dict(index=m['index'], offset=m['aligned_words'][h],
                    same_archive_path=m['path']==e['path'], texture_references=m['texture_references'])
                    for m in materials if h in m['aligned_words']]
        except (ValueError, UnicodeDecodeError) as exc:
            row['unsupported'] = str(exc)
        models.append(row)
    return dict(schema=1, source_manifest_sha256=digest((root/'manifest.json').read_bytes()),
                source_arc_sha256=manifest['source_sha256'], models=models,
                mrls=[{k:v for k,v in m.items() if k in ('index','path','sha256','texture_references')} for m in materials],
                method='MOD230 128-byte names; complement CRC32 aligned-word occurrence; exact MRL strings to ARC TEX names',
                limits=['CRC word occurrence is evidence, not a parsed MRL material record',
                        'texture slot, shader, UV transform, blend and runtime appearance unverified'])

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('output', type=Path)
    a=p.parse_args()
    result=run(a.root)
    with a.output.open('x', encoding='utf-8') as f:
        json.dump(result,f,indent=2)
        f.write('\n')
    print(json.dumps(dict(models=len(result['models']),mrls=len(result['mrls']))))

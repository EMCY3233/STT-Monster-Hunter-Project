"""Read-only game input inventory. Writes metadata only, never dumps or keys.

Limited structural probes; not a signature validator, extractor or decryptor.
"""
import argparse
import hashlib
import json
import struct
import zlib
from datetime import datetime, timezone
from pathlib import Path


def read_at(stream, offset, size):
    if offset < 0 or size < 0 or size > 8 * 1024 * 1024:
        raise ValueError('invalid bounded read')
    stream.seek(offset)
    data = stream.read(size)
    if len(data) != size:
        raise ValueError('truncated structure')
    return data


def align64(value):
    return (value + 63) & ~63


def cia_probe(stream, size):
    header = read_at(stream, 0, 32)
    hs, typ, ver, cert, ticket, tmd, meta, content = struct.unpack('<IHHIIIIQ', header)
    if hs != 0x2020 or typ != 0:
        return {'format': 'unconfirmed_CIA_extension'}
    cert_off = align64(hs)
    ticket_off = align64(cert_off + cert)
    tmd_off = align64(ticket_off + ticket)
    content_off = align64(tmd_off + tmd)
    end = content_off + content
    fits = end <= size and (not meta or align64(end) + meta <= size)
    result = {'format': 'CIA_structural_header', 'header_version': ver,
              'sections_within_file': fits, 'content_bytes_declared': content,
              'tmd_bytes': tmd, 'cryptographic_validation': 'not_performed'}
    if not fits or tmd < 4:
        return result
    # Public TMD header only. Never read or export ticket title keys.
    sig_type = struct.unpack('>I', read_at(stream, tmd_off, 4))[0]
    body_offset = {0x10000: 0x240, 0x10001: 0x140, 0x10002: 0x80,
                   0x10003: 0x240, 0x10004: 0x140, 0x10005: 0x80}.get(sig_type)
    if body_offset is not None and body_offset + 0xA4 <= tmd:
        body = read_at(stream, tmd_off + body_offset, 0xA4)
        title_ver, count = struct.unpack_from('>HH', body, 0x9C)
        result.update(title_id_tmd=body[0x4C:0x54].hex().upper(),
                      title_version_raw=title_ver,
                      title_version_components=[title_ver >> 10, (title_ver >> 4) & 63, title_ver & 15],
                      content_count_tmd=count)
        table = body_offset + 0x9C4
        if count <= 4096 and table + count * 48 <= tmd:
            entries = read_at(stream, tmd_off + table, count * 48)
            result['contents_metadata'] = []
            for pos in range(0, len(entries), 48):
                cid, idx, flags, length = struct.unpack_from('>IHHQ', entries, pos)
                result['contents_metadata'].append({'id': f'{cid:08X}', 'index': idx,
                    'type_flags': flags, 'encrypted_flag': bool(flags & 1), 'declared_bytes': length})
    if content >= 0x200:
        result['first_content_has_plain_ncch_marker'] = read_at(stream, content_off + 0x100, 4) == b'NCCH'
    return result


def iso_record(data):
    if len(data) < 34:
        raise ValueError('short ISO directory record')
    extent, length = struct.unpack_from('<I', data, 2)[0], struct.unpack_from('<I', data, 10)[0]
    name = data[33:33 + data[32]]
    return extent, length, bool(data[25] & 2), name


def sfo_fields(data):
    if data[:4] != b'\x00PSF' or len(data) < 20:
        raise ValueError('invalid SFO')
    _, keys, values, count = struct.unpack_from('<IIII', data, 4)
    if count > 4096 or 20 + 16 * count > len(data):
        raise ValueError('invalid SFO entry count')
    result = {}
    allowed = {'TITLE', 'DISC_ID', 'DISC_VERSION', 'PSP_SYSTEM_VER', 'CATEGORY'}
    for i in range(count):
        keyoff, fmt, length, maximum, valoff = struct.unpack_from('<HHIII', data, 20 + i * 16)
        start = keys + keyoff
        if start >= len(data) or values + valoff + length > len(data) or length > maximum:
            raise ValueError('SFO entry outside file')
        stop = data.find(b'\x00', start)
        if stop < 0:
            raise ValueError('SFO unterminated key')
        key = data[start:stop].decode('ascii', 'strict')
        if key in allowed and fmt in (0x204, 0x4):
            result[key] = data[values + valoff:values + valoff + length].rstrip(b'\x00').decode('utf-8', 'replace')
    return result


def iso_probe(stream, size):
    pvd = read_at(stream, 16 * 2048, 2048)
    if pvd[:7] != b'\x01CD001\x01':
        return {'format': 'unconfirmed_ISO_extension'}
    root = iso_record(pvd[156:156 + pvd[156]])
    queue = [('', root)]
    visited = set()
    files = []
    sfo = None
    executable = None
    while queue:
        prefix, (extent, length, _, _) = queue.pop(0)
        if extent in visited:
            continue
        visited.add(extent)
        if len(visited) > 2048 or len(files) > 100000:
            raise ValueError('ISO traversal limit exceeded')
        if extent * 2048 + length > size:
            raise ValueError('ISO extent outside file')
        directory = read_at(stream, extent * 2048, length)
        pos = 0
        while pos < len(directory):
            n = directory[pos]
            if not n:
                pos = (pos // 2048 + 1) * 2048
                continue
            if n < 34 or pos + n > len(directory):
                raise ValueError('invalid ISO directory record length')
            rec = iso_record(directory[pos:pos + n])
            pos += n
            ex, ln, isdir, name = rec
            if name in (b'\x00', b'\x01'):
                continue
            label = name.decode('ascii', 'replace').split(';')[0]
            path = prefix + label
            if ex * 2048 + ln > size:
                raise ValueError('ISO child outside image')
            if isdir:
                queue.append((path + '/', rec))
            else:
                files.append({'path': path, 'bytes': ln})
                if path == 'PSP_GAME/PARAM.SFO':
                    sfo = sfo_fields(read_at(stream, ex * 2048, ln))
                if path == 'PSP_GAME/SYSDIR/EBOOT.BIN':
                    magic = read_at(stream, ex * 2048, min(4, ln))
                    executable = {'path': path, 'bytes': ln,
                                  'container': {b'~PSP': 'PSP_wrapped', b'\x7fELF': 'ELF'}.get(magic, 'unknown')}
    suffixes = {}
    for item in files:
        suffix = Path(item['path']).suffix.lower() or '<none>'
        suffixes[suffix] = suffixes.get(suffix, 0) + 1
    return {'format': 'ISO9660_primary_volume', 'file_count': len(files),
            'suffix_counts': suffixes, 'sfo_metadata': sfo, 'executable': executable,
            'largest_files': sorted(files, key=lambda x: x['bytes'], reverse=True)[:12]}


def split_probe(first):
    prefix = first.name[:-3]
    parts = sorted(p for p in first.parent.glob(prefix + '*') if p.name[len(prefix):].isdigit())
    numbers = [int(p.name[len(prefix):]) for p in parts]
    total = sum(p.stat().st_size for p in parts)

    def virtual_read(offset, count):
        output = bytearray()
        for part in parts:
            size = part.stat().st_size
            if offset >= size:
                offset -= size
                continue
            with part.open('rb') as stream:
                stream.seek(offset)
                output += stream.read(min(count - len(output), size - offset))
            offset = 0
            if len(output) == count:
                return bytes(output)
        raise ValueError('split archive truncated')

    head = virtual_read(0, 32)
    if head[:6] != b'7z\xbc\xaf\x27\x1c':
        return {'format': 'unconfirmed_split_extension'}
    expected, off, length, next_crc = struct.unpack_from('<IQQI', head, 8)
    within = 32 + off + length <= total
    result = {'format': '7z_split_header', 'parts': [p.name for p in parts],
              'parts_contiguous_from_one': numbers == list(range(1, len(parts) + 1)),
              'aggregate_bytes': total, 'start_header_crc_ok': zlib.crc32(head[12:32]) == expected,
              'next_header_within_parts': within, 'payload_test': 'not_performed'}
    if within and length <= 8 * 1024 * 1024:
        result['next_header_crc_ok'] = zlib.crc32(virtual_read(32 + off, length)) == next_crc
    return result


def inventory(root):
    records = []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('symlink input refused')
        if not path.is_file():
            continue
        rec = {'path': path.relative_to(root).as_posix(), 'filename': path.name,
               'version_from_filename_only': 'v2' if 'Patch_v2' in path.name else None,
               'version_verified': None}
        try:
            before = path.stat()
            digest = hashlib.sha256()
            with path.open('rb') as stream:
                while block := stream.read(8 * 1024 * 1024):
                    digest.update(block)
                rec.update(access='full_read_ok', bytes=before.st_size, sha256=digest.hexdigest())
                if path.suffix.lower() == '.cia':
                    probe = cia_probe(stream, before.st_size)
                elif path.suffix.lower() == '.iso':
                    probe = iso_probe(stream, before.st_size)
                elif path.name.endswith('.7z.001'):
                    probe = split_probe(path)
                elif path.name.endswith('.7z.002'):
                    probe = {'format': 'split_continuation_by_filename', 'independent_archive': False}
                else:
                    probe = {'format': 'unknown'}
            after = path.stat()
            stable = (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
            rec.update(access='full_read_ok', bytes=before.st_size, sha256=digest.hexdigest(),
                       size_mtime_stable_during_read=stable, probe=probe)
            rec['version_metadata_observed'] = (probe.get('sfo_metadata') or {}).get('DISC_VERSION')
            if 'title_version_raw' in probe:
                rec['version_metadata_observed'] = {'tmd_raw': probe['title_version_raw'],
                                                     'components': probe['title_version_components']}
        except (OSError, ValueError, struct.error) as exc:
            rec.update(access=rec.get('access', 'read_failed'), error=str(exc))
        records.append(rec)
        print(json.dumps({'path': rec['path'], 'access': rec['access'], 'sha256': rec.get('sha256')}, ensure_ascii=False), flush=True)
    return {'schema_version': 1, 'generated_utc': datetime.now(timezone.utc).isoformat(),
            'input_root_label': root.name, 'method': 'read-only streaming SHA-256 and bounded structural probes; no extraction/decryption',
            'records': records}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    output = args.output.resolve()
    if output.is_relative_to(root):
        parser.error('output must be outside input root')
    report = inventory(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

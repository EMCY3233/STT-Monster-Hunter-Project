"""Bounded read-only probe for plain little-endian ARC v17.

Layout cross-reference: Paxlord/pax_arc_explorer arc.odin (arcle_read).
This is an independent limited parser, not Arc Explorer compatibility validation.
Reports metadata only. Optional single-entry export must stay outside the checkout.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib

MAX_ENTRY = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_ARCHIVE = 64 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse_table(data):
    if len(data) < 12 or len(data) > MAX_ARCHIVE:
        raise ValueError('archive size outside probe limits')
    magic, version, count, reserved = struct.unpack_from('<4sHHI', data)
    if magic != b'ARC\x00' or version != 17 or reserved != 0:
        raise ValueError('only plain ARC little-endian v17 with zero reserved field supported')
    end = 12 + count * 80
    if end > len(data):
        raise ValueError('truncated entry table')
    entries = []
    spans = []
    declared_total = 0
    for index in range(count):
        name, type_id, packed_size, size_flags, offset = struct.unpack_from('<64sIIII', data, 12 + index * 80)
        if b'\x00' not in name:
            raise ValueError('unterminated entry name')
        size = size_flags & 0x1FFFFFFF
        declared_total += size
        if size > MAX_ENTRY or declared_total > MAX_TOTAL:
            raise ValueError('declared decompression budget exceeded')
        if offset < end or offset + packed_size > len(data):
            raise ValueError('entry outside payload region')
        spans.append((offset, offset + packed_size))
        entries.append({'index': index, 'path': name.split(b'\x00', 1)[0].decode('utf-8', 'replace'),
                        'type_id': f'{type_id:08X}', 'compressed_bytes': packed_size,
                        'declared_bytes': size, 'flags': size_flags >> 29, 'offset': offset})
    ordered = sorted(spans)
    if any(a[1] > b[0] for a, b in zip(ordered, ordered[1:])):
        raise ValueError('overlapping payload spans')
    return entries


def decode_entry(data, entry):
    blob = data[entry['offset']:entry['offset'] + entry['compressed_bytes']]
    decoder = zlib.decompressobj()
    output = decoder.decompress(blob, entry['declared_bytes'] + 1)
    if len(output) != entry['declared_bytes'] or not decoder.eof or decoder.unconsumed_tail or decoder.unused_data:
        raise ValueError('zlib length, termination or trailing data mismatch')
    return output


def classify(output):
    # These are signature candidates, not model/animation/texture validation.
    for magic, kind in [(b'TEX\x00', 'TEX_candidate'), (b'MOD\x00', 'MOD_candidate'),
                        (b'LMT\x00', 'LMT_candidate'), (b'GMD\x00', 'GMD_candidate'),
                        (b'RCN\x00', 'RCN_candidate'), (b'MRL\x00', 'MRL_candidate')]:
        if output.startswith(magic):
            return kind
    return 'unclassified'


def probe(path, export_index=None, export_dir=None):
    with path.open('rb') as stream:
        data = stream.read(MAX_ARCHIVE + 1)
    entries = parse_table(data)
    output_hash = None
    exported = None
    if export_index is not None and not 0 <= export_index < len(entries):
        raise ValueError('export index outside table')
    for entry in entries:
        try:
            output = decode_entry(data, entry)
            entry.update(decompression='ok', observed_bytes=len(output), sha256=sha(output),
                         signature_candidate=classify(output))
            if entry['index'] == export_index:
                export_dir.mkdir(parents=True, exist_ok=True)
                target = export_dir / f"entry_{entry['index']:04d}.bin"
                with target.open('xb') as stream:
                    stream.write(output)
                exported = target.name
                output_hash = sha(target.read_bytes())
                if output_hash != entry['sha256']:
                    raise ValueError('export hash mismatch')
        except (zlib.error, ValueError) as exc:
            entry.update(decompression='failed', error=str(exc))
    with path.open('rb') as stream:
        after = sha(stream.read(MAX_ARCHIVE + 1))
    return {'schema_version': 1, 'source_name': path.name, 'source_sha256': sha(data),
            'source_bytes': len(data), 'source_hash_unchanged': after == sha(data),
            'format_observed': 'ARC_LE_v17', 'entry_count': len(entries),
            'decompression_counts': dict(Counter(e['decompression'] for e in entries)),
            'signature_candidates': dict(Counter(e.get('signature_candidate', 'failed') for e in entries)),
            'exported_local_name': exported, 'exported_local_sha256': output_hash, 'entries': entries}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--export-index', type=int)
    parser.add_argument('--export-dir', type=Path)
    args = parser.parse_args()
    checkout = Path(__file__).resolve().parents[1]
    if args.export_index is not None:
        if args.export_dir is None:
            parser.error('--export-dir required with --export-index')
        export = args.export_dir.resolve()
        if any((p / '.git').exists() for p in [export, *export.parents]):
            parser.error('commercial export cannot be inside a Git checkout')
    if args.report.resolve() == args.source.resolve():
        parser.error('report cannot replace source')
    result = probe(args.source, args.export_index, args.export_dir)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in result.items() if key != 'entries'}, ensure_ascii=False))
    if result['decompression_counts'].get('failed') or not result['source_hash_unchanged']:
        raise SystemExit(1)

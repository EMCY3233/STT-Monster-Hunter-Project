"""Bounded metadata-only probe of NUL-delimited CP932-decodable kana regions.

Does not export strings, identify a complete format or infer game semantics.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata

MAX_BYTES = 65536


def probe(data):
    if type(data) is not bytes or len(data) > MAX_BYTES:
        raise ValueError('expected bytes within 64 KiB probe budget')
    regions = []
    for match in re.finditer(b'[^\x00]+', data):
        raw = match.group()
        try:
            decoded = raw.decode('cp932', errors='strict')
        except UnicodeDecodeError:
            continue
        kana = sum(0x3040 <= ord(c) <= 0x30ff for c in decoded)
        if not kana:
            continue
        try:
            raw.decode('utf-8', errors='strict')
            utf8 = True
        except UnicodeDecodeError:
            utf8 = False
        regions.append({'offset': match.start(), 'bytes': len(raw), 'decoded_codepoints': len(decoded),
                        'kana_block_codepoints': kana,
                        'cjk_ideograph_codepoints': sum(0x3400 <= ord(c) <= 0x4dbf or 0x4e00 <= ord(c) <= 0x9fff for c in decoded),
                        'control_codepoints': sum(unicodedata.category(c) == 'Cc' for c in decoded),
                        'utf8_strict_valid': utf8, 'nul_terminated': match.end() < len(data)})
    return {'source_bytes': len(data), 'source_sha256': hashlib.sha256(data).hexdigest(),
            'probe_budget_bytes': MAX_BYTES, 'matching_regions': len(regions),
            'bytes_in_regions': sum(r['bytes'] for r in regions),
            'control_free_regions': sum(r['control_codepoints'] == 0 for r in regions),
            'regions': regions, 'exports_text': False, 'format_identified': False,
            'encoding_declared_by_format_verified': False, 'semantics_verified': False,
            'rule': 'Maximal non-NUL spans, strict CP932 decode, at least one U+3040..U+30FF codepoint. Metadata only; not a string-table parser.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    with args.source.open('rb') as stream:
        data = stream.read(MAX_BYTES + 1)
    result = probe(data)
    with args.source.open('rb') as stream:
        result['source_hash_unchanged'] = hashlib.sha256(stream.read(MAX_BYTES + 1)).hexdigest() == result['source_sha256']
    if not result['source_hash_unchanged']:
        raise ValueError('source changed during read')
    with args.report.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'regions'}))

"""Decode one .code range using a pinned prior NCSD probe receipt.

No whole-image hash pass, extraction of other entries, or RomFS parsing.
Reuses GPL-2.0-or-later BLZ implementation inspect_ncch_code.py; license:
docs/research/stt-re-20261021/azahar-gpl2-license.md.
"""
import argparse
import hashlib
import json
from pathlib import Path
from inspect_ncch_code import blz_footer,decompress_blz
from map_ncch_entry_reference import map_reference


def sha(data):return hashlib.sha256(data).hexdigest()


def decode_range(read_at,file_bytes,baseline,expected_output):
    if not baseline['code_compressed'] or not baseline['compression_flag_byte']&1:
        raise ValueError('compression not established by receipt')
    if file_bytes!=baseline['original_bytes'] or not 0<expected_output<=64*1024*1024:
        raise ValueError('original size or exact budget')
    if expected_output!=baseline['declared_code_pages_bytes']:
        raise ValueError('exact budget differs from segment pages')
    ranges=[]
    def read(at,n,label):
        if at<0 or n<=0 or n>64*1024*1024 or at+n>file_bytes:
            raise ValueError('read range bounds')
        data=read_at(at,n)
        if len(data)!=n:raise ValueError('short range read')
        ranges.append(dict(label=label,offset=at,bytes=n,sha256=sha(data)))
        return data
    headers=baseline['read_ranges'][:4]
    if len(headers)!=4:raise ValueError('requires four verified header ranges')
    for r in headers:
        if sha(read(r['offset'],r['bytes'],r['label']))!=r['sha256']:
            raise ValueError('prior header range changed')
    entries=[r for r in baseline['exefs_entries'] if r['name']=='.code']
    if len(entries)!=1:raise ValueError('requires unique .code')
    entry=entries[0]
    code=read(entry['file_offset'],entry['bytes'],'.code before')
    if sha(code)!=entry['sha256']:raise ValueError('compressed .code hash differs')
    footer=blz_footer(code)
    if footer['output_bytes']!=expected_output or footer!=baseline['blz_footer']:
        raise ValueError('footer differs from exact budget or previous probe')
    output,meta=decompress_blz(code)
    if len(output)!=expected_output:raise ValueError('decoder output length differs')
    after=read(entry['file_offset'],entry['bytes'],'.code after')
    if sha(after)!=entry['sha256']:raise ValueError('compressed range changed during decode')
    return output,dict(compressed_range=entry,compressed_sha256_before=sha(code),
                       compressed_sha256_after=sha(after),compressed_range_unchanged=True,
                       decompression=meta,output_bytes=len(output),output_sha256=sha(output),
                       read_ranges=ranges,read_bytes=sum(r['bytes'] for r in ranges),
                       whole_image_hash_repeated=False,whole_image_unchanged_reverified=False,
                       original_sha256_from_prior_receipt=baseline['original_sha256_before'],
                       header_ranges_match_prior_receipt=True,exact_output_budget=expected_output,
                       independently_expected_decompressed_hash=False,code_executed=False,
                       instruction_state_verified=False,game_functions_identified=False,
                       romfs_parsed_or_extracted=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--receipt',type=Path,required=True)
    p.add_argument('--expected-receipt-sha256',required=True)
    p.add_argument('--expected-output-bytes',type=int,required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    a=p.parse_args()
    if a.out_dir.exists():raise ValueError('output directory must be new')
    raw=a.receipt.read_bytes()
    if len(raw)>1024*1024 or sha(raw)!=a.expected_receipt_sha256:
        raise ValueError('prior receipt hash differs')
    baseline=json.loads(raw.decode('utf-8'))
    # Validate the declared layout before allocation; actual backing is checked again below.
    map_reference(baseline['segments'],a.expected_output_bytes,baseline['segments'][0]['address'],4)
    before=a.input.stat()
    with a.input.open('rb') as f:
        def read_at(at,n):f.seek(at);return f.read(n)
        output,r=decode_range(read_at,before.st_size,baseline,a.expected_output_bytes)
    after=a.input.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise ValueError('original file stat changed')
    map_reference(baseline['segments'],len(output),baseline['segments'][0]['address'],4)
    r.update(prior_receipt_sha256=sha(raw),original_stat_unchanged=True,
             segments=[dict(s,file_backed_range_verified=True,
                            file_end=s['file_offset']+s['mapped_bytes']) for s in baseline['segments']],
             bss_bytes=baseline['bss_bytes'],bss_page_bytes=((baseline['bss_bytes']+4095)//4096)*4096,
             bss_in_output=False,stack_bytes=baseline['stack_bytes'])
    a.out_dir.mkdir(exist_ok=False)
    (a.out_dir/'code.bin').write_bytes(output)
    (a.out_dir/'receipt.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r))

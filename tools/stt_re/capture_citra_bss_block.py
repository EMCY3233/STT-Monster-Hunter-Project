"""Dense, bounded read of a verified BSS neighborhood; no pointer dereferencing."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from observe_citra_session import read_memory


def plan(mapping, image_size, address, size):
    data = next(s for s in mapping['segments'] if s['name'] == 'data')
    start = data['address'] + data['mapped_bytes']
    end = start + mapping['bss_bytes']
    if data['file_offset'] + data['mapped_bytes'] != image_size:
        raise ValueError('unexpected static layout')
    if (type(address) is not int or type(size) is not int or
            size < 32 or size > 8192 or size % 32 or address % 32 or
            not start <= address < address + size <= end):
        raise ValueError('range outside bounded verified BSS')
    return [(a, 32) for a in range(address, address + size, 32)]


def capture(image_path, mapping_path, address, size, out):
    image = Path(image_path).read_bytes()
    mapping = json.loads(Path(mapping_path).read_bytes())
    sha = lambda b: hashlib.sha256(b).hexdigest()
    if sha(image) != mapping['output_sha256']:
        raise ValueError('image identity mismatch')
    ranges = plan(mapping, len(image), address, size)
    code = next(s for s in mapping['segments'] if s['name'] == 'text')
    expected = image[code['file_offset']:code['file_offset'] + 4]
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    receipt = dict(address=address, size=size, atomic_snapshot=False,
                   maximum_requests_per_second=20, errors=0,
                   semantic_identity_verified=False, raw_bytes_private=True,
                   utc_start=time.time(), image_sha256=sha(image))
    chunks=[]; rows=[]
    try:
        if read_memory(code['address'], 4) != expected:
            raise ValueError('control mismatch before')
        receipt['control_before_matches'] = True
        for a, n in ranges:
            begun=time.monotonic(); utc=time.time()
            value=read_memory(a, n)
            chunks.append(value)
            rows.append(dict(address=a, utc_start=utc, sha256=sha(value)))
            time.sleep(max(0, 0.05-(time.monotonic()-begun)))
        receipt['control_after_matches'] = read_memory(code['address'], 4) == expected
        if not receipt['control_after_matches']:
            raise ValueError('control mismatch after')
        raw=b''.join(chunks); receipt['bytes']=len(raw)
        (out/'block.bin').write_bytes(raw)
        (out/'reads.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
        receipt.update(block_sha256=sha(raw),reads_sha256=sha((out/'reads.json').read_bytes()),status='complete')
    except BaseException as exc:
        receipt.update(errors=1,status='failed',error=str(exc))
        raise
    finally:
        receipt['utc_end']=time.time()
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('image','mapping','out'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--address',type=lambda x:int(x,0),required=True)
    p.add_argument('--size',type=int,default=4096)
    a=p.parse_args(); print(json.dumps(capture(a.image,a.mapping,a.address,a.size,a.out)))

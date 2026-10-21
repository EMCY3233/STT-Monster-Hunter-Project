"""Compare existing region offsets to bounded layout hypotheses, without strings."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

def inspect(data,regions):
    if not 20<=len(data)<=65536: raise ValueError('sample outside budget')
    previous=0; gaps=[]; windows=[]; anchors=set()
    for r in regions:
        at=r['offset']; size=r['bytes']; end=at+size
        if at<previous or size<=0 or end>=len(data) or data[end]!=0: raise ValueError('invalid region boundary')
        if b'\0' in data[at:end]: raise ValueError('NUL inside supplied region')
        gap=at-previous
        gaps.append(dict(start=previous,end=at,bytes=gap))
        if gap>=11: windows.append((data[at-11:at],size))
        anchors.add(at); previous=end+1
    if not regions: raise ValueError('no supplied regions')
    first=regions[0]['offset']; pointers=[]
    for width in (2,4):
        for endian in ('little','big'):
            for at in range(0,first-width+1,width):
                target=int.from_bytes(data[at:at+width],endian)
                if target in anchors: pointers.append(dict(at=at,width=width,endian=endian,target=target))
    lengths=[]
    for width in (1,2,4):
        for endian in ('little','big'):
            for at in range(12-width):
                for extra in (0,1):
                    hits=sum(int.from_bytes(w[at:at+width],endian)==size+extra for w,size in windows)
                    if hits: lengths.append(dict(relative_offset_from_text_start=at-11,width=width,endian=endian,includes_nul=bool(extra),matching_windows=hits,total_windows=len(windows)))
    c0,c1=struct.unpack_from('>II',data)
    return dict(source_bytes=len(data),region_count=len(regions),regions_revalidated=True,gaps=gaps,gap_sizes=dict(Counter(g['bytes'] for g in gaps)),trailing_bytes=len(data)-previous,scenario_outer=dict(chunk0=c0,chunk1=c1,chunk0_within_file=c0<=len(data)-8,combined_chunks_within_file=c0+c1<=len(data)-8),subheader_hypothesis=dict(padding_zero=data[1]==0,total_u16=struct.unpack_from('<H',data,2)[0],computed_strings_start=8+data[6],matches_first_supplied_region=8+data[6]==first),ftxt_magic_matches=struct.unpack_from('<I',data)[0]==0x000b0000,record_header_17_zero_padding_matches=not any(data[4:17]),aligned_absolute_pointer_matches_before_first_region=pointers,prefix_windows=dict(bytes_per_window=11,count=len(windows),distinct_values_per_column=[len(set(w[i] for w,_ in windows)) for i in range(11)],length_field_candidates=lengths),semantics_verified=False,grammar_verified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--regions',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args(); out=a.out.resolve(); source=a.input.resolve(strict=True)
    if out.is_relative_to(source.parent): raise ValueError('keep output outside source evidence folder')
    if source.stat().st_size>65536: raise ValueError('input budget')
    data=source.read_bytes(); metadata=json.loads(a.regions.read_text())
    digest=hashlib.sha256(data).hexdigest()
    if digest!=metadata['source_sha256'] or len(data)!=metadata['source_bytes']: raise ValueError('region source mismatch')
    report=inspect(data,metadata['regions'])
    report.update(source_sha256=digest,region_report_sha256=hashlib.sha256(a.regions.read_bytes()).hexdigest(),source_unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==digest,scope='supplied anchors only; no CP932 rescan, strings, decryption or decompression')
    out.mkdir(parents=True,exist_ok=False)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

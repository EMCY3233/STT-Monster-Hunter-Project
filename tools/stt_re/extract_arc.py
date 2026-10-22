"""Complete bounded extraction/verification for plain ARC LE v17 with zlib entries.

Original paths are metadata, never destination paths. Commercial outputs stay local.
No encrypted containers, DRM/key handling, format conversion or game execution.
"""
import argparse,hashlib,json,re
from pathlib import Path
from probe_arc import MAX_ARCHIVE,MAX_ENTRY,MAX_TOTAL,parse_table,decode_entry,classify


def sha(data):return hashlib.sha256(data).hexdigest()


def read_source(path):
    path=Path(path)
    if not path.is_file():raise ValueError('source must be a regular file')
    with path.open('rb') as f:data=f.read(MAX_ARCHIVE+1)
    if len(data)>MAX_ARCHIVE:raise ValueError('archive size limit exceeded')
    return data


def inspect(data):
    entries=parse_table(data);results=[]
    for entry in entries:
        decoded=decode_entry(data,entry)
        candidate=classify(decoded);ext=candidate.removesuffix('_candidate').lower() if candidate!='unclassified' else 'bin'
        results.append(dict(entry,output_file=f"entries/{entry['index']:05d}.{ext}",
            observed_bytes=len(decoded),sha256=sha(decoded),signature_candidate=candidate,
            name_bytes_hex=data[12+entry['index']*80:12+entry['index']*80+64].hex(),
            semantic_format_verified=False))
    return results


def private_destination(out):
    out=Path(out)
    if out.exists() or out.is_symlink():raise FileExistsError('output must be a new directory')
    resolved=out.resolve()
    publication_tree=Path(__file__).resolve().parents[2]
    if resolved==publication_tree or publication_tree in resolved.parents:
        raise ValueError('commercial output must not be in the publication tree')
    if any((p/'.git').exists() for p in (resolved,*resolved.parents)):
        raise ValueError('commercial output must not be inside a Git checkout')
    return resolved


def extract(source,out,expected_sha256=None):
    source=Path(source);out=private_destination(out)
    data=read_source(source);digest=sha(data)
    if expected_sha256 is not None and digest!=expected_sha256:raise ValueError('source hash differs from expected')
    entries=inspect(data)  # Validate every entry before creating destination.
    out.mkdir(parents=True,exist_ok=False);(out/'entries').mkdir()
    try:
        for entry in entries:
            decoded=decode_entry(data,entry)
            if sha(decoded)!=entry['sha256']:raise ValueError('second decode disagrees')
            target=out/entry['output_file']
            with target.open('xb') as f:f.write(decoded)
            if sha(target.read_bytes())!=entry['sha256']:raise ValueError('export readback hash mismatch')
        if sha(read_source(source))!=digest:raise ValueError('source changed during extraction')
        manifest=dict(schema=1,status='complete',format='ARC_LE_v17_zlib',source_name=source.name,
            source_bytes=len(data),source_sha256=digest,source_hash_after=digest,
            entry_count=len(entries),extracted_bytes=sum(e['observed_bytes'] for e in entries),
            entry_paths_used_as_destinations=False,original_path_metadata_preserved=True,
            semantic_conversion=False,entries=entries)
        encoded=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
        with (out/'manifest.json').open('xb') as f:f.write(encoded)
        with (out/'manifest.sha256').open('x',encoding='ascii') as f:f.write(sha(encoded)+'\n')
        return verify(out,source)
    except BaseException as exc:
        with (out/'failure.json').open('x',encoding='utf-8') as f:json.dump(dict(status='failed',error=str(exc)),f)
        raise


def verify(folder,source=None):
    folder=Path(folder)
    if (folder/'failure.json').exists():raise ValueError('failed export rejected')
    raw=(folder/'manifest.json').read_bytes()
    if (folder/'manifest.sha256').read_text().strip()!=sha(raw):raise ValueError('manifest hash mismatch')
    m=json.loads(raw)
    if m['schema']!=1 or m['status']!='complete' or m['format']!='ARC_LE_v17_zlib':raise ValueError('unsupported manifest')
    if len(m['entries'])!=m['entry_count']:raise ValueError('entry count mismatch')
    if not 0<=m['entry_count']<=65535 or not 0<=m['extracted_bytes']<=MAX_TOTAL:raise ValueError('manifest budgets exceeded')
    names=set();total=0
    for i,e in enumerate(m['entries']):
        name=e['output_file']
        if e['index']!=i or not re.fullmatch(r'entries/[0-9]{5}\.(bin|tex|mod|lmt|gmd|rcn|mrl)',name) or name in names:
            raise ValueError('unsafe or duplicate export identity')
        names.add(name);target=folder/name
        if int(Path(name).stem)!=i:raise ValueError('filename index mismatch')
        if not 0<=e['observed_bytes']<=MAX_ENTRY or e['observed_bytes']!=e['declared_bytes']:raise ValueError('entry size budget or declaration mismatch')
        if target.is_symlink() or (folder/'entries').is_symlink():raise ValueError('symlink export rejected')
        if target.stat().st_size!=e['observed_bytes']:raise ValueError('export hash/size mismatch')
        data=target.read_bytes()
        if len(data)!=e['observed_bytes'] or sha(data)!=e['sha256']:raise ValueError('export hash/size mismatch')
        total+=len(data)
    if total!=m['extracted_bytes']:raise ValueError('total size mismatch')
    extras={p.name for p in (folder/'entries').iterdir()}-{Path(n).name for n in names}
    if extras:raise ValueError('unexpected entry files')
    source_verified=False
    if source is not None:
        data=read_source(source)
        if sha(data)!=m['source_sha256'] or len(data)!=m['source_bytes']:raise ValueError('original source identity mismatch')
        original=inspect(data)
        if original!=m['entries']:raise ValueError('manifest disagrees with freshly decoded source')
        source_verified=True
    return dict(status='verified',source_name=m['source_name'],source_sha256=m['source_sha256'],
        entry_count=m['entry_count'],extracted_bytes=total,manifest_sha256=sha(raw),
        exports_verified=True,fresh_source_decode_verified=source_verified,
        signature_counts={kind:sum(e['signature_candidate']==kind for e in m['entries']) for kind in sorted({e['signature_candidate'] for e in m['entries']})},
        semantic_conversion=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);s=p.add_subparsers(dest='command',required=True)
    x=s.add_parser('extract');x.add_argument('source',type=Path);x.add_argument('--out',type=Path,required=True);x.add_argument('--expect-sha256')
    v=s.add_parser('verify');v.add_argument('folder',type=Path);v.add_argument('--source',type=Path)
    l=s.add_parser('list');l.add_argument('source',type=Path)
    a=p.parse_args()
    if a.command=='extract':r=extract(a.source,a.out,a.expect_sha256)
    elif a.command=='verify':r=verify(a.folder,a.source)
    else:
        data=read_source(a.source);r=dict(source_sha256=sha(data),entries=inspect(data))
    print(json.dumps(r,ensure_ascii=False))

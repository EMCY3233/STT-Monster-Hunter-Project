"""Read-only aggregate audit of a resource-links index; never opens asset blobs."""
import argparse
from collections import Counter,defaultdict
import hashlib,json,re,sqlite3,zlib
from pathlib import Path

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk:=stream.read(1024*1024):h.update(chunk)
    return h.hexdigest()

def normalize(path):return path.replace('\\','/').casefold()

def analyze(db):
    db.row_factory=sqlite3.Row
    required={'assets':{'sha256'},'resources':{'id','path','sha256','type_id'},
              'resource_links':{'source_sha256','target_path','match_kind','occurrences','semantic_verified'},
              'resource_types':{'type_id','class_name_candidate'}}
    for table,columns in required.items():
        actual={row['name'] for row in db.execute(f'PRAGMA table_info({table})')}
        if not columns<=actual:raise ValueError('required relation-audit schema absent')
    assets=[r['sha256'] for r in db.execute('SELECT sha256 FROM assets')]
    aset=set(assets);resources=list(db.execute('SELECT id,path,sha256,type_id FROM resources'))
    by_path=defaultdict(set);by_norm=defaultdict(set);norm_names=defaultdict(set);occ=Counter()
    for r in resources:
        by_path[r['path']].add(r['sha256']);by_norm[normalize(r['path'])].add(r['sha256'])
        norm_names[normalize(r['path'])].add(r['path']);occ[r['path']]+=1
    result=dict(resource_rows=len(resources),asset_rows=len(assets),
        invalid_resource_ids=sum(type(r['id']) is not int or r['id']<0 for r in resources),
        empty_resource_paths=sum(not r['path'] for r in resources),
        duplicate_resource_ids=len(resources)-len({r['id'] for r in resources}),
        duplicate_asset_hash_rows=len(assets)-len(aset),
        invalid_asset_hash_rows=sum(not isinstance(s,str) or not re.fullmatch('[0-9a-f]{64}',s) for s in assets),
        resource_rows_missing_asset=sum(r['sha256'] not in aset for r in resources),
        resource_rows_invalid_hash=sum(not isinstance(r['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',r['sha256']) for r in resources),
        distinct_paths=len(by_path),repeated_paths=sum(n>1 for n in occ.values()),
        paths_with_multiple_contents=sum(len(v)>1 for v in by_path.values()),
        normalized_paths_with_multiple_contents=sum(len(v)>1 for v in by_norm.values()),
        normalized_alias_groups=sum(len(v)>1 for v in norm_names.values()))
    any_source={r['sha256'] for r in resources}
    counts=Counter();keys=Counter();normalized_keys=Counter();kinds=Counter();recorded_flags=Counter();sources=set();targets=set();ambiguous_targets=set()
    for row in db.execute('SELECT * FROM resource_links'):
        source,target,kind=row['source_sha256'],row['target_path'],row['match_kind']
        counts['links']+=1;sources.add(source);targets.add(target);kinds[kind]+=1
        keys[(source,target,kind)]+=1;normalized_keys[(source,normalize(target),kind)]+=1
        counts['source_missing_asset']+=source not in aset
        counts['source_missing_resource_occurrence']+=source not in any_source
        counts['target_missing_exact_path']+=target not in by_path
        counts['target_missing_normalized_path']+=normalize(target) not in by_norm
        counts['target_exact_multiple_contents']+=len(by_path.get(target,()))>1
        if len(by_path.get(target,()))>1:ambiguous_targets.add(target)
        counts['target_normalized_multiple_contents']+=len(by_norm.get(normalize(target),()))>1
        counts['self_content_reference_candidates']+=source in by_path.get(target,())
        counts['invalid_occurrence_counts']+=type(row['occurrences']) is not int or row['occurrences']<1
        flag=row['semantic_verified'];recorded_flags[str(flag)]+=1
        counts['invalid_semantic_flags']+=type(flag) is not int or flag not in (0,1)
    for key in ('links','source_missing_asset','source_missing_resource_occurrence','target_missing_exact_path','target_missing_normalized_path','target_exact_multiple_contents','target_normalized_multiple_contents','self_content_reference_candidates','invalid_occurrence_counts','invalid_semantic_flags'):counts.setdefault(key,0)
    counts['duplicate_link_groups']=sum(n>1 for n in keys.values())
    counts['duplicate_link_excess_rows']=sum(n-1 for n in keys.values())
    counts['normalized_duplicate_link_groups']=sum(n>1 for n in normalized_keys.values())
    counts['normalized_duplicate_link_excess_rows']=sum(n-1 for n in normalized_keys.values())
    counts['distinct_ambiguous_exact_targets']=len(ambiguous_targets)
    types=list(db.execute('SELECT * FROM resource_types'))
    mismatches=0
    for row in types:
        expected=f"{(zlib.crc32(row['class_name_candidate'].encode())^0xffffffff)&0x7fffffff:08X}"
        mismatches+=row['type_id']!=expected
    result.update(links=dict(counts),match_kind_counts=dict(kinds),recorded_semantic_flag_counts=dict(recorded_flags),distinct_link_sources=len(sources),distinct_link_targets=len(targets),type_name_crc_candidates=len(types),type_name_crc_formula_mismatches=mismatches,independently_confirmed_semantic_links=0,asset_payloads_opened=0)
    return result

def audit(database):
    database=Path(database).resolve()
    sidecars=[Path(str(database)+suffix) for suffix in ('-wal','-journal')]
    if any(p.exists() and p.stat().st_size for p in sidecars):raise ValueError('closed index without active journal/WAL required')
    before=digest(database)
    db=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
    try:
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        result=analyze(db)
        result['sqlite_integrity_check']=[r[0] for r in db.execute('PRAGMA integrity_check')]
        result['sqlite_foreign_key_check_rows']=len(list(db.execute('PRAGMA foreign_key_check')))
        result['declared_foreign_keys']=sum(len(list(db.execute(f'PRAGMA foreign_key_list({t})'))) for t in ('assets','resources','resource_links','resource_types'))
    finally:db.close()
    after=digest(database)
    if before!=after:raise ValueError('index changed during audit')
    result.update(index_sha256_before=before,index_sha256_after=after,index_unchanged=True,read_only=True,
                  semantics_note='Path and CRC matches are candidates. Stored semantic flags are not independently verified by this audit.')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--database',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.resolve()==a.database.resolve() or a.database.resolve().parent in a.out.resolve().parents:raise ValueError('write report outside the historical bank')
    report=audit(a.database)
    with a.out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(report))

"""One aggregate hierarchy/matrix coherence property; never exports matrices.

Reference RevilLib e17f9718 common.cpp/external converter, Spike e83f3855
matrix44.cpp. Column-major as in the reference glTF/GLM path, no axis/scale
conversion. This checks a source-derived model, not native game bind semantics.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

TOLERANCE=0.0001


def sha(data):return hashlib.sha256(data).hexdigest()


def matrix(flat):
    if len(flat)!=16 or not all(math.isfinite(x) for x in flat):raise ValueError('nonfinite or wrong matrix size')
    return [[float(flat[4*c+r]) for c in range(4)] for r in range(4)]


def multiply(a,b):
    return [[math.fsum(a[r][k]*b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]


def check(parents,local_flat,inverse_flat):
    n=len(parents)
    if not 0<n<=255 or len(local_flat)!=n or len(inverse_flat)!=n:raise ValueError('family counts')
    if any(p!=255 and not 0<=p<n for p in parents):raise ValueError('parent bounds')
    local=[matrix(m) for m in local_flat];inverse=[matrix(m) for m in inverse_flat]
    global_mats={};active=set()
    def global_for(i):
        if i in global_mats:return global_mats[i]
        if i in active:raise ValueError('parent cycle')
        active.add(i)
        g=local[i] if parents[i]==255 else multiply(global_for(parents[i]),local[i])
        if not all(math.isfinite(v) for row in g for v in row):raise ValueError('nonfinite global product')
        global_mats[i]=g;active.remove(i)
        return g
    errors=[]
    for i in range(n):
        product=multiply(global_for(i),inverse[i])
        if not all(math.isfinite(v) for row in product for v in row):raise ValueError('nonfinite identity product')
        errors.append(max(abs(product[r][c]-(1.0 if r==c else 0.0)) for r in range(4) for c in range(4)))
    roots=[i for i,p in enumerate(parents) if p==255]
    return dict(property='max(abs(G_i * B_i - I)) <= absolute tolerance',
                hierarchy_composition='G_root=L_root; G_child=G_parent*L_child',
                storage_interpretation='column-major, source exporter convention',
                absolute_tolerance=TOLERANCE,pairs_checked=n,scalar_residuals_checked=n*16,
                pairs_within_tolerance=sum(e<=TOLERANCE for e in errors),
                root_pairs_within_tolerance=sum(errors[i]<=TOLERANCE for i in roots),
                nonroot_pairs_within_tolerance=sum(errors[i]<=TOLERANCE for i in range(n) if i not in roots),
                max_absolute_residual=max(errors),property_holds_for_all_pairs=all(e<=TOLERANCE for e in errors),
                arithmetic='float32 source promoted to Python float64; fsum dot products',
                alternative_order_or_transpose_search=False,axis_units_scale_conversion=False,
                matrices_exported=False,native_bind_pose_semantics_verified=False,
                rig_functional_verified=False,skinning_performed=False,lmt_association=False)


def inspect(read_at,total,baseline):
    if total!=baseline['source_bytes'] or total>1024*1024:raise ValueError('source length')
    wanted={r['label']:r for r in baseline['ranges']}
    blocks={};ranges=[]
    for label in ['bones','ref_poses','transforms']:
        r=wanted[label];at=r['offset'];size=r['bytes']
        if at<0 or size<0 or at+size>total or size>65536:raise ValueError('range bounds')
        data=read_at(at,size)
        if len(data)!=size or sha(data)!=r['sha256']:raise ValueError('range differs from prior receipt')
        blocks[label]=data;ranges.append(dict(label=label,offset=at,bytes=size,sha256=sha(data)))
    n=baseline['bone_count']
    if len(blocks['bones'])!=n*24 or len(blocks['ref_poses'])!=n*64 or len(blocks['transforms'])!=n*64:
        raise ValueError('family range/count mismatch')
    parents=[blocks['bones'][i*24+1] for i in range(n)]
    local=[struct.unpack_from('<16f',blocks['ref_poses'],i*64) for i in range(n)]
    inverse=[struct.unpack_from('<16f',blocks['transforms'],i*64) for i in range(n)]
    result=check(parents,local,inverse)
    result.update(read_ranges=ranges,property_read_bytes=sum(r['bytes'] for r in ranges),
                  property_model_source='reference API/exporter; not a native SDK declaration')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--prior-receipt',type=Path,required=True)
    p.add_argument('--expected-receipt-sha256',required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();raw=a.prior_receipt.read_bytes()
    if len(raw)>1024*1024 or sha(raw)!=a.expected_receipt_sha256:raise ValueError('prior receipt identity')
    baseline=json.loads(raw.decode('utf-8'))
    if a.input.stat().st_size>1024*1024:raise ValueError('source budget')
    before=sha(a.input.read_bytes())
    if before!=baseline['source_sha256_before']:raise ValueError('source identity')
    with a.input.open('rb') as f:
        def read_at(at,n):f.seek(at);return f.read(n)
        r=inspect(read_at,a.input.stat().st_size,baseline)
    after=sha(a.input.read_bytes())
    if before!=after:raise ValueError('source changed')
    r.update(source_sha256_before=before,source_sha256_after=after,source_unchanged=True,
             prior_receipt_sha256=sha(raw),source_bytes=a.input.stat().st_size,full_file_hash_passes=2)
    with a.out.open('x',encoding='utf-8') as f:f.write(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))

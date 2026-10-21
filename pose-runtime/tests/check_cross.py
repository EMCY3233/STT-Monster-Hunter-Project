"""Build and execute portable C reader against Python exports and hostile JSON."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'asset-lab'))
from stt_asset_lab import bridge, model

def main():
    compiler = shlex.split(os.environ.get('CC', 'cc'))
    flags = shlex.split(os.environ.get('POSE_CFLAGS', ''))
    with tempfile.TemporaryDirectory(prefix='stt-pose-') as temp:
        directory = Path(temp)
        exe = directory/('probe.exe' if os.name == 'nt' else 'probe')
        subprocess.run([*compiler, '-std=c99','-Wall','-Wextra','-Werror',*flags,
                        '-I'+str(ROOT/'pose-runtime'),str(ROOT/'pose-runtime/stt_pose.c'),
                        str(ROOT/'pose-runtime/tests/pose_probe.c'),'-lm','-o',str(exe)],check=True)
        count = 0
        memory = None
        def run(raw, expected):
            nonlocal count
            path = directory/'input.json'
            path.write_bytes(raw)
            result = subprocess.run([str(exe),str(path)],capture_output=True,text=True)
            if result.returncode != expected:
                raise AssertionError((result.returncode, expected, result.stderr[:4000]))
            count += 1
            return result.stdout

        asset = model.load(ROOT/'asset-lab/samples/practice-dummy.stt.json')
        sample = bridge.bake(asset)
        # Exercise an asymmetric, rotated parent/child anchor and exact integer limits.
        anchor = copy.deepcopy(sample)
        anchor['clips'] = [dict(name='Anchor', frames=[dict(joints=[[1000,2000,3000],[1000,2250,3000]],
            vertices=[[1000,2250,3000],[1000,3250,3000],[0,2250,3000]])])]
        anchor['parents']=[-1,0]; anchor['triangles']=[[0,1,2]]
        limits=copy.deepcopy(anchor)
        limits['clips'][0]['frames'][0]['vertices'][0]=[-1000000,0,1000000]
        for value in [sample,anchor,limits]:
            raw=bridge.runtime_dumps(value)
            imported=bridge.loads(raw)
            output=run(raw,0).splitlines()
            info=list(map(int,output[0].split()))
            memory=info[:2]
            expected=[]
            for clip in imported['clips']:
                for f in clip['frames']:
                    expected.append([n for p in f['joints']+f['vertices'] for n in p])
            actual=[list(map(int,line.split())) for line in output[1:] if not line.startswith('mesh ')]
            assert actual==expected
            assert info[2:]==[len(value['parents']),len(value['clips'][0]['frames'][0]['vertices']),
                             len(value['triangles']),len(value['clips']),len(expected)]
            emitted=[line.split() for line in output if line.startswith('mesh ')]
            assert len(emitted)==len(imported['clips'])
            for c,line in enumerate(emitted):
                assert int(line[1])==c and int(line[2])==len(value['triangles'])
                expected_sum=[0.,0.,0.]
                for triangle in imported['triangles']:
                    for index in triangle:
                        x,y,z=imported['clips'][c]['frames'][0]['vertices'][index]
                        for j,n in enumerate([4+z*.001,y*.001,5-x*.001]): expected_sum[j]+=n
                for a,b in zip(map(float,line[3:]),expected_sum):
                    # Float32 transform, summed as double: account for ±1000 m boundaries.
                    assert abs(a-b) <= .001*max(1,len(value['triangles']))
        raw=bridge.runtime_dumps(anchor)
        malformed=[b'',raw+b'0',raw.replace(b'"version":1',b'"version":2'),
                   raw.replace(b'"hz":60',b'"hz":30'), raw.replace(b'"parents":[-1,0]',b'"parents":[-1,1]'),
                   raw.replace(b'[0,1,2]',b'[0,1,3]'),raw.replace(b'[0,1,2]',b'[0,0,2]'),
                   raw.replace(b'1000',b'2147483648',1),raw.replace(b'1000',b'-2147483649',1),
                   raw.replace(b'1000',b'1e3',1),raw.replace(b'1000',b'true',1),
                   raw.replace(b'1000',b'NaN',1),raw.replace(b'1000',b'01000',1),
                   raw.replace(b'1000',b'1000001',1),raw.replace(b'"hz":60',b'"hz":60,"hz":60'),
                   raw.replace(b'"Anchor"',b'"\\u0041nchor"'),b' '* (bridge.MAX_BYTES+1)]
        # Every truncation of the small two-bone document, including token boundaries.
        malformed.extend(raw[:i] for i in range(1,len(raw)))
        for bad in malformed: run(bad,2)
        for mutate in [lambda d:d['clips'][0].__setitem__('frames',[]),
                       lambda d:d['clips'][0].__setitem__('frames',d['clips'][0]['frames']*601),
                       lambda d:d.__setitem__('parents',[-1]+list(range(32))),
                       lambda d:d['clips'][0]['frames'][0]['joints'].pop(),
                       lambda d:d.__setitem__('triangles',[[0,1,2]]*513),
                       lambda d:d.__setitem__('clips',d['clips']*9)]:
            bad=copy.deepcopy(anchor); mutate(bad)
            run(json.dumps(bad,separators=(',',':')).encode(),2)
        report=dict(cases=count, sample_bytes=len(bridge.runtime_dumps(sample)),
                    sample_sha256=hashlib.sha256(bridge.runtime_dumps(sample)).hexdigest(),
                    sizeof_index=memory[0],sizeof_frame=memory[1],
                    scope='PC C/Python; no GUI, Vita execution, FTP or installation')
        print(json.dumps(report,indent=2))

if __name__ == '__main__': main()

import copy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from stt_asset_lab.model import AssetError, export, load, loads, pose, validate, MAX_BYTES
from generate_sample import make_sample
from stt_asset_lab.projection import project

class AssetTests(unittest.TestCase):
    def setUp(self): self.data=make_sample()
    def bad(self, change):
        change(self.data)
        with self.assertRaises(AssetError): validate(self.data)
    def test_sample_regenerated_exactly(self):
        self.assertEqual(load(Path(__file__).parents[1]/'samples/practice-dummy.stt.json'),self.data)
    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'asset.json'; export(self.data,path)
            self.assertEqual(load(path),self.data)
    def test_original_animation_and_loop(self):
        a,b=pose(self.data,1,0); c,d=pose(self.data,1,0.3)
        self.assertNotEqual(b,d)
        self.assertEqual((a,b),pose(self.data,1,1.2))
        self.assertEqual(a[:3],c[:3]); self.assertNotEqual(a[3],c[3])
    def test_interpolation(self):
        # arm-local vertex endpoint has rotation pi/2 half way through a pi swing.
        self.data['clips'][0]['tracks']=[{'bone':2,'keys':[[0,0],[2,math.pi]]}]
        joints,vertices=pose(self.data,0,1)
        arm=self.data['vertices'][32]['position']; joint=joints[2]
        self.assertAlmostEqual(vertices[32][0],joint[0]-arm[1])
        self.assertAlmostEqual(vertices[32][1],joint[1]+arm[0])
    def test_projection_mesh_and_skeleton_finite(self):
        for clip in range(len(self.data['clips'])):
            for frame in range(121):
                joints, vertices=pose(self.data,clip,frame/60)
                for yaw in (0,math.pi/2,math.pi):
                    for point in joints+vertices:
                        result=project(point,yaw,120,800,600)
                        self.assertTrue(all(math.isfinite(v) for v in result))
                        self.assertTrue(0 <= result[0] <= 800)
                        self.assertTrue(0 <= result[1] <= 600)
                # Root is shared by geometry hierarchy and overlay, independent of yaw.
                self.assertEqual(project(joints[0],0,120,800,600),(400,444,0))
    def test_projection_preserves_distance_and_orbits(self):
        a,b=[0.2,0.5,-0.3],[1.2,1.5,0.7]
        for yaw in (0,0.4,math.pi/2,math.pi):
            pa,pb=project(a,yaw,100,800,600),project(b,yaw,100,800,600)
            distance=((pa[0]-pb[0])/100)**2+((pa[1]-pb[1])/100)**2+(pa[2]-pb[2])**2
            self.assertAlmostEqual(distance,sum((x-y)**2 for x,y in zip(a,b)))
        self.assertAlmostEqual(project([1,0,0],math.pi/2,100,800,600)[0],400)
        self.assertGreater(project([0,1,0],0,100,800,600)[2],0)
    def test_bad_parent_and_cycle(self): self.bad(lambda d:d['bones'][1].update(parent=1))
    def test_multiple_roots(self): self.bad(lambda d:d['bones'][1].update(parent=-1))
    def test_duplicate_names(self): self.bad(lambda d:d['bones'][1].update(name='root'))
    def test_invalid_bone(self): self.bad(lambda d:d['vertices'][0].update(bone=999))
    def test_bool_index_rejected(self): self.bad(lambda d:d['vertices'][0].update(bone=True))
    def test_bad_triangle(self): self.bad(lambda d:d['triangles'].__setitem__(0,[0,1,999]))
    def test_degenerate_triangle(self): self.bad(lambda d:d['triangles'].__setitem__(0,[0,0,1]))
    def test_unknown_fields(self): self.bad(lambda d:d.update(external_url='http://example.invalid'))
    def test_wrong_version(self): self.bad(lambda d:d.update(version=2))
    def test_nonfinite(self): self.bad(lambda d:d['vertices'][0].update(position=[math.nan,0,0]))
    def test_overlong_vector(self): self.bad(lambda d:d['vertices'][0].update(position=[0]*4))
    def test_out_of_order_keys(self): self.bad(lambda d:d['clips'][0]['tracks'][0].update(keys=[[0,0],[2,1],[1,0]]))
    def test_missing_duration_endpoint(self): self.bad(lambda d:d['clips'][0]['tracks'][0].update(keys=[[0,0],[1,1]]))
    def test_duplicate_track(self): self.bad(lambda d:d['clips'][0]['tracks'].append(copy.deepcopy(d['clips'][0]['tracks'][0])))
    def test_bounded(self):
        with self.assertRaises(AssetError): loads(b' '*(MAX_BYTES+1))
        self.bad(lambda d:d.update(bones=[{}]*129))
    def test_bad_json(self):
        for raw in (b'{}',b'[]',b'null',b'\xff',b'{',b'{"x":1,"x":2}',b'{"x":NaN}', b'['*2000, b'{"x":'+b'9'*5000+b'}'):
            with self.subTest(raw=raw[:40]),self.assertRaises(AssetError): loads(raw)
    def test_cli(self):
        cwd=Path(__file__).parents[1]
        result=subprocess.run([sys.executable,'-m','stt_asset_lab','samples/practice-dummy.stt.json','--validate'],cwd=cwd,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['bones'],4)
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'bad.json'; path.write_text('{}')
            result=subprocess.run([sys.executable,'-m','stt_asset_lab',str(path),'--validate'],cwd=cwd,capture_output=True)
            self.assertEqual(result.returncode,2); self.assertIn(b'Asset error',result.stderr)

if __name__=='__main__': unittest.main()

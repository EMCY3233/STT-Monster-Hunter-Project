import copy
import math
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]))
from stt_asset_lab import bridge, model

class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.asset = model.load(Path(__file__).parents[1] / 'samples/practice-dummy.stt.json')

    def test_sample_roundtrip_error_and_loop(self):
        baked = bridge.loads(bridge.dumps(bridge.bake(self.asset)))
        self.assertEqual([len(c['frames']) for c in baked['clips']], [120, 72])
        for i, clip in enumerate(baked['clips']):
            for tick, f in enumerate(clip['frames']):
                joints, vertices = model.pose(self.asset, i, tick/60)
                for key, original in [('joints', joints), ('vertices', vertices)]:
                    for a, b in zip(f[key], original):
                        for x, y in zip(a,b):
                            self.assertLessEqual(abs(x-y*1000), .50000001)
            self.assertEqual(bridge.frame(baked,i,len(clip['frames'])), clip['frames'][0])

    def test_rounding_and_range(self):
        self.assertEqual([bridge.mm(x) for x in [0,1,-1,.0005,-.0005]], [0,1000,-1000,1,-1])
        for x in [math.inf, math.nan, 1000.001]:
            with self.assertRaises(model.AssetError): bridge.mm(x)

    def test_asymmetric_anchor_and_winding(self):
        a = dict(format='STT Asset',version=1,name='anchor',
                 bones=[dict(name='root',parent=-1,offset=[1,2,3]),
                        dict(name='child',parent=0,offset=[.25,0,0])],
                 vertices=[dict(bone=1,position=p) for p in [[0,0,0],[1,0,0],[0,1,0]]],
                 triangles=[[0,1,2]], clips=[dict(name='turn',duration=1,tracks=[dict(bone=0,keys=[[0,math.pi/2],[1,math.pi/2]])])])
        b = bridge.bake(a)
        f = bridge.frame(b,0,0)
        self.assertEqual(f['joints'], [[1000,2000,3000],[1000,2250,3000]])
        self.assertEqual(f['vertices'], [[1000,2250,3000],[1000,3250,3000],[0,2250,3000]])
        self.assertEqual(b['triangles'], [[0,1,2]])
        # Cross product remains +Z: no reflected basis or reversed winding.
        p,q,r=f['vertices']; self.assertGreater((q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0]),0)

    def test_offgrid_keys_resampled_duration_rejected(self):
        a = copy.deepcopy(self.asset)
        track = a['clips'][0]['tracks'][0]
        track['keys'].insert(1,[.001,.1])
        bridge.bake(a)  # continuous evaluator, no key truncation
        a['clips'][0]['duration'] += .001
        with self.assertRaises(model.AssetError): bridge.bake(a)

    def test_bad_hierarchy_indices_types_and_bounds(self):
        b = bridge.bake(self.asset)
        mutations = [lambda d:d['parents'].__setitem__(1,1),
                     lambda d:d['triangles'][0].__setitem__(0,999),
                     lambda d:d['clips'][0]['frames'][0]['vertices'][0].__setitem__(0,True),
                     lambda d:d['clips'][0]['frames'][0]['vertices'][0].__setitem__(0,1000001),
                     lambda d:d['clips'][0]['frames'][0]['vertices'].pop()]
        for mutate in mutations:
            d=copy.deepcopy(b); mutate(d)
            with self.assertRaises(model.AssetError): bridge.dumps(d)

    def test_input_budgets_and_duplicate_fields(self):
        for raw in [b'{"format":1,"format":2}', b'\xff', b' '* (bridge.MAX_BYTES+1)]:
            with self.assertRaises(model.AssetError): bridge.loads(raw)
        a=copy.deepcopy(self.asset); a['clips'][0]['duration']=600
        with self.assertRaises(model.AssetError): bridge.bake(a)

    def test_c_profile_canonicalizes_order_and_restricts_names(self):
        data=bridge.bake(self.asset)
        canonical=bridge.runtime_dumps(data)
        self.assertEqual(bridge.runtime_dumps(dict(reversed(list(data.items())))),canonical)
        self.assertEqual(bridge.loads(canonical),data)
        for name in ['caf\u00e9', 'quote"', 'slash\\']:
            data['clips'][0]['name']=name
            bridge.dumps(data)  # still valid general Pose/1
            with self.assertRaises(model.AssetError): bridge.runtime_dumps(data)

if __name__ == '__main__': unittest.main()

import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).parent))
from evaluate_models import obj,cluster,normal,dot,bridge,model

class EvaluationTests(unittest.TestCase):
    def test_convex_quad_and_negative_indices(self):
        v,t=obj(b'v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nf -4 -3 -2 -1\n')
        self.assertEqual(t,[[0,1,2],[0,2,3]])
        self.assertGreater(normal(v,t[0])[2],0)

    def test_malformed_and_unsupported_obj(self):
        for raw in [b'v nan 0 0', b'v 0 0 0\nf 1 2 3',b'v 0 0 0\nf 0 0 0',
                    b'call evil.obj',b'v 1 2',b'v 0 0 0\nf 1 1 1']:
            with self.assertRaises(ValueError):obj(raw)

    def test_concave_quad_rejected(self):
        with self.assertRaises(ValueError):obj(b'v 0 0 0\nv 2 0 0\nv 0.5 0.5 0\nv 0 2 0\nf 1 2 3 4')

    def test_cluster_deterministic_and_no_mutation(self):
        v=[[0,0,0],[1,0,0],[0,1,0],[0,0,1]];t=[[0,1,2],[0,3,1]]
        before=json.dumps([v,t]);a=cluster(v,t,[4,4,4]);b=cluster(v,t,[4,4,4])
        self.assertEqual(a,b);self.assertEqual(json.dumps([v,t]),before)
        self.assertEqual(a[2]['max_source_vertex_displacement'],0)

    def test_prepared_pose_geometry_and_quantization(self):
        # Installed next to tools in repository; local evaluation uses prepared/.
        local=Path(__file__).parent/'prepared'
        root=local if local.exists() else Path(__file__).resolve().parents[1]/'samples/cc0-sword-study'
        asset=model.load(root/'quaternius-sword-study.stt.json')
        raw=(root/'quaternius-sword-study.pose.json').read_bytes()
        self.assertEqual(bridge.runtime_dumps(bridge.bake(asset)),raw)
        pose=bridge.loads(raw)
        self.assertEqual((len(asset['vertices']),len(asset['triangles'])),(199,394))
        points=pose['clips'][0]['frames'][0]['vertices']
        original=[p['position'] for p in asset['vertices']]
        for triangle in pose['triangles']:
            n=normal(points,triangle)
            self.assertGreater(dot(n,n),0)
            self.assertGreater(dot(n,normal(original,triangle)),0)
        self.assertLessEqual(len(raw),163840)

if __name__=='__main__':unittest.main()

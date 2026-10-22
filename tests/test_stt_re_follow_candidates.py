from pathlib import Path
import sys,json,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from follow_citra_candidates import select_candidates,literal_hits,follow,digest


class FollowTests(unittest.TestCase):
    def test_candidate_must_match_prior_plan(self):
        protocol=dict(windows=[dict(address=4096,size=32,file_offset=0)])
        bad=dict(window=0,address=4097,file_offset=0)
        with self.assertRaises(ValueError):select_candidates(dict(static_mismatches=[bad]),protocol)
        good=dict(window=0,address=4096,file_offset=0)
        with self.assertRaises(ValueError):select_candidates(dict(static_mismatches=[good,good]),protocol)

    def test_literals_are_aligned_and_range_bounded(self):
        image=(8193).to_bytes(4,'little')+(8224).to_bytes(4,'little')+b'xxx'
        hits=literal_hits(image,[dict(name='text',file_offset=0,code_bytes=11,address=4096)],[dict(window=3,address=8192,size=32)])
        self.assertEqual(hits,[dict(segment='text',file_offset=0,source_address=4096,candidate_window=3,target_byte_offset=1)])

    def fixture(self,tmp):
        root=Path(tmp);prior=root/'prior';prior.mkdir()
        image=root/'image';image.write_bytes(b'abcd'+bytes(8))
        mapping=root/'map';mapping.write_text(json.dumps(dict(output_sha256=digest(image.read_bytes()),segments=[dict(name='text',file_offset=0,code_bytes=4,address=4096),dict(name='data',file_offset=4,code_bytes=8,address=8192)])))
        protocol=dict(static_image_sha256=digest(image.read_bytes()),mapping_sha256=digest(mapping.read_bytes()),control=dict(address=4096,size=4,file_offset=0),windows=[dict(address=8192,size=8,file_offset=4)])
        (prior/'protocol.json').write_text(json.dumps(protocol))
        (prior/'windows.bin').write_bytes(b'');(prior/'reads.jsonl').write_bytes(b'')
        receipt=dict(protocol_sha256=digest((prior/'protocol.json').read_bytes()),binary_sha256=digest(b''),reads_sha256=digest(b''))
        (prior/'receipt.json').write_text(json.dumps(receipt))
        (prior/'analysis.json').write_text(json.dumps(dict(receipt=receipt,static_mismatches=[dict(window=0,address=8192,file_offset=4)])))
        return prior,image,mapping,root/'out'

    def test_follow_retains_delta_and_bounded_binary(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(tmp);values=iter([b'abcd',bytes(8),b'abcd',b'\1'+bytes(7)])
            with patch('follow_citra_candidates.read_memory',side_effect=lambda *a,**k:next(values)),patch('follow_citra_candidates.time.sleep'):
                r=follow(*args,cycles=2)
            self.assertEqual(r['successes'],4);self.assertEqual(r['completed_cycles'],2)
            self.assertEqual(r['extracted_bytes'],24)
            self.assertEqual(r['candidates'][0]['changed_byte_indices'],[0])
            self.assertEqual(r['candidates'][0]['distinct_digests'],2)

    def test_wrong_prior_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(tmp);(args[0]/'windows.bin').write_bytes(b'changed')
            with self.assertRaises(ValueError):follow(*args,cycles=2)
            self.assertFalse(args[3].exists())

    def test_control_stops_before_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(tmp)
            with patch('follow_citra_candidates.read_memory',return_value=b'xxxx') as read:
                r=follow(*args,cycles=2)
            self.assertEqual(read.call_count,1);self.assertEqual(r['stop_reason'],'control_mismatch')
            self.assertEqual(r['candidates'][0]['successful_samples'],0)


if __name__=='__main__':unittest.main()

from pathlib import Path
import sys,json,hashlib,tempfile,unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from sample_citra_data_windows import plan_windows,compare_windows,capture


class SparseTests(unittest.TestCase):
    def fixture(self,tmp,length=4097):
        image=Path(tmp)/'image';image.write_bytes(b'abcdxxxx'+bytes(length))
        mapping=Path(tmp)/'map.json'
        mapping.write_text(json.dumps(dict(output_sha256=hashlib.sha256(image.read_bytes()).hexdigest(),segments=[dict(name='text',address=0x100000,file_offset=0),dict(name='data',address=0x200000,code_bytes=length,file_offset=8)])))
        return mapping,image

    def test_windows_clip_end_and_exclude_gaps(self):
        self.assertEqual(plan_windows(dict(address=8192,code_bytes=4097,file_offset=0)),[dict(address=8192,size=32,file_offset=0),dict(address=12288,size=1,file_offset=4096)])

    def test_invalid_ranges(self):
        for segment in [dict(address=2**32-1,code_bytes=2,file_offset=0),dict(address=0,code_bytes=0,file_offset=0),dict(address=-1,code_bytes=32,file_offset=0)]:
            with self.assertRaises(ValueError):plan_windows(segment)
        with self.assertRaises(ValueError):plan_windows(dict(address=0,code_bytes=100,file_offset=0),stride=1)

    def test_missing_read_does_not_imply_stable(self):
        r=compare_windows({0:b'ab',1:b'x'},{0:b'ac'})
        self.assertEqual(r['unpaired_windows'],1)
        self.assertEqual(r['changed_windows'],[dict(window=0,changed_byte_indices=[1])])

    def test_two_sweeps_binary_offsets_and_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping,image=self.fixture(tmp);calls=[]
            def read(address,size,**kw):
                calls.append(address)
                if address==0x100000:return b'abcd'
                return (b'\x01' if len(calls)>3 else b'\0')*size
            with patch('sample_citra_data_windows.read_memory',side_effect=read),patch('sample_citra_data_windows.time.sleep'):
                r=capture(mapping,image,Path(tmp)/'out')
            self.assertEqual(r['successes'],6);self.assertEqual(r['extracted_bytes'],74)
            self.assertEqual(r['completed_sweeps'],2)
            self.assertEqual(len(r['comparison']['changed_windows']),2)
            rows=[json.loads(x) for x in (Path(tmp)/'out/reads.jsonl').read_text().splitlines()]
            self.assertEqual([x['binary_offset'] for x in rows],[0,4,36,37,41,73])

    def test_wrong_static_hash_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping,image=self.fixture(tmp);image.write_bytes(b'changed')
            with self.assertRaises(ValueError):capture(mapping,image,Path(tmp)/'out')
            self.assertFalse((Path(tmp)/'out').exists())

    def test_control_mismatch_stops_before_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping,image=self.fixture(tmp)
            with patch('sample_citra_data_windows.read_memory',return_value=b'zzzz') as read:
                r=capture(mapping,image,Path(tmp)/'out')
            self.assertEqual(read.call_count,1);self.assertEqual(r['stop_reason'],'control_mismatch')
            self.assertEqual(r['completed_sweeps'],0)

    def test_four_errors_abort_and_keep_partial_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            mapping,image=self.fixture(tmp,16385)
            with patch('sample_citra_data_windows.read_memory',side_effect=TimeoutError),patch('sample_citra_data_windows.time.sleep'):
                r=capture(mapping,image,Path(tmp)/'out')
            self.assertEqual(r['errors'],4);self.assertEqual(r['stop_reason'],'four_consecutive_errors')
            self.assertEqual(r['extracted_bytes'],0)


if __name__=='__main__':unittest.main()

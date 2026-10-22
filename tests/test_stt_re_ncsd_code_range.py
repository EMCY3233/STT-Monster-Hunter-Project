from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from decode_ncsd_code_range import decode_range,sha
from inspect_ncch_code import blz_footer
from test_stt_re_ncch_code import packed


def fixture():
    code=packed();headers=b'HEAD'*4;data=headers+code
    baseline=dict(code_compressed=True,compression_flag_byte=1,original_bytes=len(data),
                  declared_code_pages_bytes=24,original_sha256_before=sha(data),
                  read_ranges=[dict(label=str(i),offset=i*4,bytes=4,sha256=sha(b'HEAD')) for i in range(4)],
                  exefs_entries=[dict(name='.code',file_offset=16,bytes=len(code),sha256=sha(code))],
                  blz_footer=blz_footer(code))
    return data,baseline


class CodeRangeTests(unittest.TestCase):
    def test_one_range_exact_output_and_prefix(self):
        data,b=fixture();out,r=decode_range(lambda at,n:data[at:at+n],len(data),b,24)
        self.assertEqual(out,b'PRE'+b'CBA'*7)
        self.assertTrue(r['compressed_range_unchanged'])
        self.assertFalse(r['whole_image_hash_repeated'])

    def test_no_compression_flag(self):
        data,b=fixture();b['compression_flag_byte']=0
        with self.assertRaisesRegex(ValueError,'compression'):decode_range(lambda at,n:data[at:at+n],len(data),b,24)

    def test_exact_budget_before_decoder(self):
        data,b=fixture();b['declared_code_pages_bytes']=25
        with patch('decode_ncsd_code_range.decompress_blz') as decoder:
            with self.assertRaisesRegex(ValueError,'budget'):decode_range(lambda at,n:data[at:at+n],len(data),b,25)
            decoder.assert_not_called()

    def test_changed_header(self):
        data,b=fixture();data=b'FAIL'+data[4:]
        with self.assertRaisesRegex(ValueError,'header'):decode_range(lambda at,n:data[at:at+n],len(data),b,24)

    def test_bad_compressed_hash(self):
        data,b=fixture();b['exefs_entries'][0]['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'hash differs'):decode_range(lambda at,n:data[at:at+n],len(data),b,24)

    def test_range_changes_after_decode(self):
        data,b=fixture();reads=0
        def read(at,n):
            nonlocal reads
            if at==16:
                reads+=1
                if reads==2:return b'X'*n
            return data[at:at+n]
        with self.assertRaisesRegex(ValueError,'changed during'):decode_range(read,len(data),b,24)

    def test_short_read(self):
        data,b=fixture()
        with self.assertRaisesRegex(ValueError,'short range'):decode_range(lambda at,n:b'',len(data),b,24)


if __name__=='__main__':unittest.main()

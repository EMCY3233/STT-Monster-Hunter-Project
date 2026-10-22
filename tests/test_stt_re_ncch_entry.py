from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/stt_re'))
from map_ncch_entry_reference import map_reference


def segments():
    return [dict(name=n,address=0x100000+i*4096,mapped_bytes=4096,
                 code_bytes=4000,file_offset=i*4096) for i,n in enumerate(['text','ro','data'])]


class EntryMappingTests(unittest.TestCase):
    def test_start_maps_to_zero_rx(self):
        r=map_reference(segments(),12288,0x100000,4)
        self.assertEqual((r['file_offset'],r['segment'],r['permissions_from_azahar']),(0,'text','r-x'))

    def test_offset_and_segment(self):
        r=map_reference(segments(),12288,0x101020,4)
        self.assertEqual((r['file_offset'],r['segment'],r['segment_delta']),(4128,'ro',32))

    def test_padding_is_not_declared_code(self):
        with self.assertRaises(ValueError):map_reference(segments(),12288,0x100fa0,4)

    def test_crossing_declared_end(self):
        with self.assertRaises(ValueError):map_reference(segments(),12288,0x100f9f,4)

    def test_bss_is_not_file_backed(self):
        with self.assertRaises(ValueError):map_reference(segments(),12288,0x103000,4)

    def test_overlap_rejected(self):
        s=segments();s[1]['address']=s[0]['address']
        with self.assertRaises(ValueError):map_reference(s,12288,0x100000,4)

    def test_truncated_file_rejected(self):
        with self.assertRaises(ValueError):map_reference(segments(),12287,0x100000,4)

    def test_zero_width_rejected(self):
        with self.assertRaises(ValueError):map_reference(segments(),12288,0x100000,0)


if __name__=='__main__':unittest.main()

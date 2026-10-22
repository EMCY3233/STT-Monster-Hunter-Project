import os,sys,struct,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from find_arm_literal_accesses import scan
dependency=os.environ.get('STT_CAPSTONE_PATH')
if dependency:sys.path.insert(0,dependency)
try:
    import capstone
except ImportError:
    capstone=None


def segments(n):
    return [dict(name='text',address=0x1000,file_offset=0,code_bytes=n)]


@unittest.skipIf(capstone is None,'set STT_CAPSTONE_PATH to the isolated Capstone 5.0.6 installation')
class LiteralTests(unittest.TestCase):
    def arm(self,words):
        raw=struct.pack('<'+'I'*len(words),*words)
        return scan(raw,segments(len(raw)),[0x2004],capstone)

    def test_arm_literal_then_store(self):
        r=self.arm([0xe59f0008,0xe5801004,0xe12fff1e,0,0x2000])
        self.assertEqual(len(r['access_candidates']),1)
        self.assertEqual(r['access_candidates'][0]['access'],'write')
        self.assertFalse(r['runtime_execution_verified'])

    def test_register_clobber_rejects(self):
        r=self.arm([0xe59f000c,0xe3a00000,0xe5801004,0xe12fff1e,0,0x2000])
        self.assertEqual(r['access_candidates'],[])

    def test_conditional_access_not_followed(self):
        r=self.arm([0xe59f0008,0x05801004,0xe12fff1e,0,0x2000])
        self.assertEqual(r['access_candidates'],[])

    def test_thumb_literal_then_store(self):
        raw=struct.pack('<4HI',0x4801,0x6041,0x4770,0xbf00,0x2000)
        r=scan(raw,segments(len(raw)),[0x2004],capstone,thumb=True)
        self.assertEqual(len(r['access_candidates']),1)
        self.assertEqual(r['access_candidates'][0]['instruction_address'],0x1002)

    def test_literal_outside_backing(self):
        r=self.arm([0xe59f0ffc,0xe5801004])
        self.assertEqual(r['access_candidates'],[])

    def test_immediate_address_adjustment(self):
        r=self.arm([0xe59f000c,0xe2800004,0xe5901000,0xe12fff1e,0,0x2000])
        self.assertEqual(r['access_candidates'][0]['access'],'read')

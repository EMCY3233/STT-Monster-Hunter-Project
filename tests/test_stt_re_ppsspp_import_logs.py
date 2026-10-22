import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location('logs',Path(__file__).parents[1]/'tools/stt_re/compare_ppsspp_import_logs.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
EXPECTED={'.rodata.sceNid':(0x0890ec78,3200)}
class LogEvidence(unittest.TestCase):
    def test_exact_announcement(self): self.assertEqual(m.announcements('prefix Data Section found: .rodata.sceNid Sitting at 0890ec78, size 00000c80',EXPECTED)[0]['bytes'],3200)
    def test_same_address_other_section_is_not_evidence(self): self.assertEqual(m.announcements('Data Section found: .other Sitting at 0890ec78, size 00000c80',EXPECTED),[])
    def test_wrong_size_is_not_evidence(self): self.assertEqual(m.announcements('Data Section found: .rodata.sceNid Sitting at 0890ec78, size 00000c81',EXPECTED),[])
    def test_unstructured_address_is_not_evidence(self): self.assertEqual(m.announcements('Read address 0890ec78',EXPECTED),[])
if __name__=='__main__': unittest.main()

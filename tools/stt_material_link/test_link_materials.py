import struct
import unittest
from link_materials import material_names, mrl_evidence

class LinkTests(unittest.TestCase):
    def model(self):
        d=bytearray(192)
        d[:4]=b'MOD\0'
        struct.pack_into('<H',d,4,230)
        struct.pack_into('<H',d,10,1)
        struct.pack_into('<I',d,48,64)
        d[64:77]=b'XfBAW_1__m00_'
        return d

    def test_known_crc_relation(self):
        self.assertEqual(material_names(self.model())[0]['complement_crc32'],'813e69ea')

    def test_truncated_material_rejected(self):
        with self.assertRaises(ValueError): material_names(self.model()[:-1])

    def test_unterminated_name_rejected(self):
        d=self.model(); d[64:]=b'A'*128
        with self.assertRaises(ValueError): material_names(d)

    def test_exact_reference_not_prefix(self):
        d=bytearray(40);d[:4]=b'MRL\0';struct.pack_into('<I',d,4,32)
        d.extend(b'effect\\base\\a\0effect\\base\\ab\0')
        r=mrl_evidence(d,{'effect\\base\\a':[7]})
        self.assertEqual([x['exact_archive_matches'] for x in r],[[7],[]])

    def test_unterminated_reference_ignored(self):
        d=bytearray(40);d[:4]=b'MRL\0';struct.pack_into('<I',d,4,32)
        d.extend(b'effect\\base\\a')
        self.assertEqual(mrl_evidence(d,{}),[])

    def test_unknown_version_rejected(self):
        d=self.model();struct.pack_into('<H',d,4,229)
        with self.assertRaises(ValueError): material_names(d)

if __name__=='__main__': unittest.main()

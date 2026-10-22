import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools/stt_re'))
from probe_mh4u_cheat_reference import parse,derive,guarded


def reference():
    parts=[]
    for version,root,delta in [('1.0',0x081c7720,0),('1.1',0x081c8140,0xa20)]:
        def add(name,lines):parts.append('['+name+' v'+version+']\n'+'\n'.join(lines))
        add('Max Money',[f'{0x08368e60+delta:08X} 0098967F'])
        add('Max Caravan',[f'{0x083776cc+delta:08X} 0098967F'])
        guard=[f'{0x40000000|root:08X} 08800000',f'{0x30000000|root:08X} 08D00000',f'{0xb0000000|root:08X} 00000000']
        add('Infinite Health',guard+['00001184 00960096','10001188 00000096','10001194 00000096'])
        add('Infinite Stamina',guard+['0000118C 44610000','00001190 44610000'])
        add('Inventory Items 255x',[f'{0xa0000000|0x08375940+delta:08X} 00000000'])
        add('1st Item Box Slot Item 99x',[f'{0x20000000|0x08368f8c+delta:08X} 00000063'])
    parts.append('[Better Cycle First Item (Y + L/R) v1.1]\nB81C8440 00000000')
    return '\n\n'.join(parts)


class ReferenceTests(unittest.TestCase):
    def test_derive_versions_and_discrepancy(self):
        r=derive(reference());self.assertEqual(r['versions'][0]['player_root'],0x081c7720)
        self.assertEqual(r['versions'][1]['player_root'],0x081c8140)
        self.assertEqual(r['alternate_v11_roots'],[0x081c8440])
        self.assertFalse(r['cheats_executed'])

    def test_guard_null_alignment_and_bounds(self):
        v=derive(reference())['versions'][0]
        for root in (0,0x08800000,0x08800001,0x08cffffc):self.assertFalse(guarded(root,v))
        self.assertTrue(guarded(0x08800004,v))

    def test_duplicate_section_rejected(self):
        with self.assertRaises(ValueError):parse('[x]\n00000000 00000000\n[x]')

    def test_arbitrary_text_rejected(self):
        with self.assertRaises(ValueError):parse('[x]\nrun something')

    def test_unexpected_guard_rejected(self):
        with self.assertRaises(ValueError):derive(reference().replace('08800000','00000000'))

    def test_stamina_root_mismatch_rejected(self):
        s=reference().replace('[Infinite Stamina v1.0]\n481C7720','[Infinite Stamina v1.0]\n481C7724')
        # Alter the B root too to force the independent root check.
        section=s.index('[Infinite Stamina v1.0]');end=s.index('\n\n',section)
        s=s[:section]+s[section:end].replace('B81C7720','B81C7724')+s[end:]
        with self.assertRaises(ValueError):derive(s)

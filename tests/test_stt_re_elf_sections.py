"""Synthetic ELF bounds and entry mapping, no game bytes."""
import importlib.util
from pathlib import Path
import struct
import unittest

spec=importlib.util.spec_from_file_location('elf_sections',Path(__file__).parents[1]/'tools/stt_re/inspect_elf_sections.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def fixture():
    b=bytearray(512)
    b[:7]=b'\x7fELF\x01\x01\x01'
    struct.pack_into('<HHIIIIIHHHHHH',b,16,2,8,1,0x1000,52,128,0,52,32,1,40,3,1)
    struct.pack_into('<8I',b,52,1,300,0x1000,0x1000,8,16,5,4)
    names=b'\0.shstrtab\0.text\0'
    b[260:260+len(names)]=names
    struct.pack_into('<10I',b,168,1,3,0,0,260,len(names),0,0,1,0)
    struct.pack_into('<10I',b,208,11,1,6,0x1000,300,8,0,0,4,0)
    return b

class ElfTests(unittest.TestCase):
    def test_entry_mapping(self):
        r=m.inspect(fixture())
        self.assertEqual(r['entry_file_offsets'],[300])
        self.assertEqual(r['sections'][2]['name'],'.text')
    def test_memory_only_entry_is_not_file_backed(self):
        b=fixture()
        struct.pack_into('<I',b,24,0x100c)
        self.assertFalse(m.inspect(b)['entry_in_file_backed_executable_load'])
    def test_table_outside(self):
        b=fixture()
        struct.pack_into('<I',b,32,500)
        with self.assertRaises(ValueError): m.inspect(b)
    def test_section_outside(self):
        b=fixture()
        struct.pack_into('<I',b,208+20,300)
        with self.assertRaises(ValueError): m.inspect(b)
    def test_bad_name(self):
        b=fixture()
        struct.pack_into('<I',b,208,999)
        with self.assertRaises(ValueError): m.inspect(b)
    def test_file_size_exceeds_memory(self):
        b=fixture()
        struct.pack_into('<I',b,52+20,4)
        with self.assertRaises(ValueError): m.inspect(b)
    def test_big_endian_rejected(self):
        b=fixture()
        b[5]=2
        with self.assertRaises(ValueError): m.inspect(b)

if __name__=='__main__': unittest.main()

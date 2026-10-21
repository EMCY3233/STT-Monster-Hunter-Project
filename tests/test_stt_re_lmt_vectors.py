"""Synthetic quantized vectors and LMT bounds; no game resources."""
import importlib.util
from pathlib import Path
import math
import struct
import unittest

spec=importlib.util.spec_from_file_location('vectors',Path(__file__).parents[1]/'tools/stt_re/decode_lmt_vectors.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def vector_data(bits=8):
    b=bytearray(64)
    struct.pack_into('<8f',b,32,2,4,6,0,10,20,30,0)
    struct.pack_into('<4B' if bits==8 else '<4H',b,8,0,255 if bits==8 else 65535,0,3)
    return b

def lmt():
    b=bytearray(160)
    struct.pack_into('<4sHHI',b,0,b'LMT\0',67,1,16)
    struct.pack_into('<IIIi',b,16,80,1,30,-1)
    struct.pack_into('<4BfII4fI',b,80,1,1,0,2,1,0,0,1,2,3,0,0)
    return b

class VectorTests(unittest.TestCase):
    def test_8bit_affine_bounds(self):
        r=m.vector_keys(vector_data(),5,8,4,32)
        self.assertEqual(r[0]['xyz'],[10,24,30])
    def test_16bit_affine_bounds(self):
        r=m.vector_keys(vector_data(16),4,8,8,32)
        self.assertEqual(r[0]['xyz'],[10,24,30])
    def test_additive_frame_indices(self):
        b=vector_data()
        struct.pack_into('<4B',b,12,255,0,255,0)
        r=m.vector_keys(b,5,8,8,32)
        self.assertEqual([k['frame_index_without_reference'] for k in r],[0,3])
    def test_nonintegral_stride(self):
        with self.assertRaises(ValueError): m.vector_keys(vector_data(),4,8,7,32)
    def test_missing_extremes(self):
        with self.assertRaises(ValueError): m.vector_keys(vector_data(),5,8,4,0)
    def test_unsupported_codec(self):
        with self.assertRaises(ValueError): m.vector_keys(vector_data(),6,8,4,32)
    def test_nan_bounds(self):
        b=vector_data()
        struct.pack_into('<f',b,32,math.nan)
        with self.assertRaises(ValueError): m.vector_keys(b,5,8,4,32)
    def test_reference_only(self):
        r=m.inspect(lmt())
        self.assertEqual(r[0]['status'],'reference_vector_read')
        self.assertEqual(r[0]['reference_xyz'],[1,2,3])
    def test_track_table_outside(self):
        b=lmt()
        struct.pack_into('<I',b,16,150)
        with self.assertRaises(ValueError): m.inspect(b)
    def test_version_rejected(self):
        b=lmt()
        struct.pack_into('<H',b,4,68)
        with self.assertRaises(ValueError): m.inspect(b)
    def test_nonfinite_weight(self):
        b=lmt()
        struct.pack_into('<f',b,84,math.inf)
        with self.assertRaises(ValueError): m.inspect(b)

if __name__=='__main__': unittest.main()

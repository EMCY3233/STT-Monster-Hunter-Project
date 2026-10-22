import hashlib
import pathlib
import struct
import subprocess
import sys
import tempfile
import unittest

EXE = sys.argv.pop(1)
def put(b, p, v):
    struct.pack_into("<I", b, p, v)
def ncch():
    b = bytearray(2048)
    b[256:260] = b"NCCH"
    put(b, 0x104, 4)
    b[0x18f] = 4
    put(b, 0x1b0, 1)
    put(b, 0x1b4, 3)
    put(b, 0x1b8, 1)
    return b
def ncsd():
    b = bytearray(4096)
    b[256:260] = b"NCSD"
    put(b, 0x104, 8)
    put(b, 0x120, 4)
    put(b, 0x124, 4)
    b[2048:] = ncch()
    return b

class Inspector(unittest.TestCase):
    def run_image(self, b, valid=True):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "synthetic.cci"
            p.write_bytes(b)
            before = hashlib.sha256(b).hexdigest()
            r = subprocess.run([EXE, str(p)], capture_output=True, text=True)
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), before)
            self.assertEqual(r.returncode, 0 if valid else 1, r.stderr)
            if valid:
                self.assertIn("file_sha256=" + before, r.stdout)
            else:
                self.assertEqual(r.stdout, "")
            return r.stdout
    def test_ncch(self):
        self.assertIn("encrypted_declared=0", self.run_image(ncch()))
    def test_ncsd(self):
        self.assertIn("partition=0 offset=2048", self.run_image(ncsd()))
    def test_encryption_flags(self):
        b = ncch()
        b[0x18f] = 0x21
        b[0x18b] = 0x0b
        out = self.run_image(b)
        for s in ["encrypted_declared=1", "fixed_key_flag=1", "seed_flag=1", "crypto_method=11"]:
            self.assertIn(s, out)
    def test_all_header_truncations(self):
        b = ncch()
        for i in range(512):
            with self.subTest(i=i):
                self.run_image(b[:i], False)
    def test_partition_truncation(self):
        self.run_image(ncsd()[:-1], False)
    def test_trimmed_tail(self):
        b = ncsd()
        put(b, 0x104, 16)
        self.assertIn("trimmed=1", self.run_image(b))
    def test_invalid_mutations(self):
        mutations = [(0x104,0), (0x104,0xffffffff), (0x1b0,0), (0x1b4,0),
                     (0x1b0,4), (0x1b8,4), (0x180,1),
                     (0x190,1), (0x194,1)]
        for p,v in mutations:
            b = ncch()
            put(b,p,v)
            with self.subTest(p=p,v=v):
                self.run_image(b,False)
    def test_exponent(self):
        b = ncch()
        b[0x18e] = 255
        self.run_image(b,False)
    def test_scaled_units(self):
        b = ncch() + bytearray(2048)
        b[0x18e] = 1
        self.assertIn("romfs offset=1024 size=3072",self.run_image(b))
    def test_overlapping_partitions(self):
        b = ncsd()
        put(b,0x128,4)
        put(b,0x12c,4)
        self.run_image(b,False)
    def test_partition_metadata(self):
        for p,v in [(0x120,0),(0x124,0),(0x120,0xffffffff),(0x104,1)]:
            b = ncsd()
            put(b,p,v)
            self.run_image(b,False)
    def test_magic(self):
        self.run_image(bytearray(2048),False)
        b=ncsd()
        b[2304:2308]=b"FAIL"
        self.run_image(b,False)
    def test_missing_input(self):
        r=subprocess.run([EXE,"does-not-exist.cci"],capture_output=True)
        self.assertEqual(r.returncode,1)
    def test_usage(self):
        self.assertEqual(subprocess.run([EXE],capture_output=True).returncode,2)

if __name__ == "__main__":
    unittest.main()

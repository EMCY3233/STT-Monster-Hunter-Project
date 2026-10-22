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


def deep_image():
    b = bytearray(8192)
    b[256:260] = b"NCCH"
    put(b, 0x104, 16)
    b[0x18f] = 4
    put(b, 0x1b0, 1)
    put(b, 0x1b4, 15)
    put(b, 0x1b8, 1)
    iv = 512
    b[iv:iv+4] = b"IVFC"
    put(b, iv+4, 0x10000)
    put(b, iv+8, 32)
    put(b, iv+0x4c, 9)
    struct.pack_into("<Q", b, iv+0x44, 512)
    lv = 1024
    struct.pack_into("<10I", b, lv, 40, 40, 4, 44, 24, 68, 4, 72, 36, 112)
    put(b, lv+40, 0)
    struct.pack_into("<6I", b, lv+44, 0, 0xffffffff, 0xffffffff, 0, 0xffffffff, 0)
    put(b, lv+68, 0)
    struct.pack_into("<IIQQII", b, lv+72, 0, 0xffffffff, 0, 3, 0xffffffff, 2)
    b[lv+104:lv+106] = "a".encode("utf-16le")
    b[lv+112:lv+115] = b"abc"
    b[0x1e0:0x200] = hashlib.sha256(b[iv:iv+512]).digest()
    return b


def tree_image(names=(), filename="a"):
    offsets=[0]
    d=bytearray(24)
    for name in names:
        offsets.append(len(d))
        raw=name.encode("utf-16le")
        d+=bytearray(24+(len(raw)+3)//4*4)
    for i,pos in enumerate(offsets):
        raw=(names[i-1] if i else "").encode("utf-16le")
        child=offsets[i+1] if i+1<len(offsets) else 0xffffffff
        struct.pack_into("<6I",d,pos,offsets[i-1] if i else 0,
                         0xffffffff,child,0 if i==len(offsets)-1 and filename is not None else 0xffffffff,
                         0xffffffff,len(raw))
        d[pos+24:pos+24+len(raw)]=raw
    file=bytearray()
    if filename is not None:
        raw=filename.encode("utf-16le")
        file=bytearray(32+(len(raw)+3)//4*4)
        struct.pack_into("<IIQQII",file,0,offsets[-1],0xffffffff,0,3,0xffffffff,len(raw))
        file[32:32+len(raw)]=raw
    dm=44; fh=dm+len(d); fm=fh+4; data=(fm+len(file)+15)//16*16
    lvsize=(data+3+511)//512*512
    b=bytearray(1024+lvsize)
    b[256:260]=b"NCCH"; put(b,0x104,len(b)//512); b[0x18f]=4
    put(b,0x1b0,1); put(b,0x1b4,(len(b)-512)//512); put(b,0x1b8,1)
    b[512:516]=b"IVFC"; put(b,516,0x10000); put(b,520,32); put(b,512+0x4c,9)
    struct.pack_into("<Q",b,512+0x44,lvsize)
    struct.pack_into("<10I",b,1024,40,40,4,dm,len(d),fh,4,fm,len(file),data)
    b[1024+dm:1024+dm+len(d)]=d
    b[1024+fm:1024+fm+len(file)]=file
    b[1024+data:1024+data+3]=b"abc"
    b[0x1e0:0x200]=hashlib.sha256(b[512:1024]).digest()
    return b


def integrity_image(lvsize=512):
    src=tree_image()
    block=512
    ceil=lambda n:(n+block-1)//block*block
    body=bytes(src[1024:])+bytes(max(0,ceil(lvsize)-512))
    body=body[:ceil(lvsize)]
    h2=b"".join(hashlib.sha256(body[i:i+block]).digest() for i in range(0,len(body),block))
    l2=h2+bytes(ceil(len(h2))-len(h2))
    h1=b"".join(hashlib.sha256(l2[i:i+block]).digest() for i in range(0,len(l2),block))
    l1=h1+bytes(ceil(len(h1))-len(h1))
    master=b"".join(hashlib.sha256(l1[i:i+block]).digest() for i in range(0,len(l1),block))
    b=bytearray(1024+len(body)+len(l1)+len(l2))
    b[:512]=src[:512]
    put(b,0x104,len(b)//512); put(b,0x1b4,(len(b)-512)//512)
    b[512:516]=b"IVFC"; put(b,516,0x10000); put(b,520,len(master))
    for i,(logical,n) in enumerate([(0,len(h1)),(len(l1),len(h2)),(len(l1)+len(l2),lvsize)]):
        struct.pack_into("<QQII",b,512+12+24*i,logical,n,9,0)
    b[608:608+len(master)]=master
    b[1024:1024+len(body)]=body
    at=1024+len(body)
    b[at:at+len(l1)]=l1
    b[at+len(l1):]=l2
    b[0x1e0:0x200]=hashlib.sha256(b[512:1024]).digest()
    return b
def exefs_image():
    b=bytearray(2048)
    b[256:260]=b"NCCH"; put(b,0x104,4); b[0x18f]=4
    put(b,0x1a0,1); put(b,0x1a4,3); put(b,0x1a8,1)
    for i,(name,offset,data) in enumerate([(b".code",0,b"abc"),(b"icon",512,b"xyz")]):
        b[512+16*i:512+16*i+len(name)]=name
        put(b,512+16*i+8,offset); put(b,512+16*i+12,len(data))
        b[1024+offset:1024+offset+len(data)]=data
        b[512+0x1e0-i*32:512+0x200-i*32]=hashlib.sha256(data).digest()
    b[0x1c0:0x1e0]=hashlib.sha256(b[512:1024]).digest()
    return b

class Inspector(unittest.TestCase):
    def run_image(self, b, valid=True, options=()):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "synthetic.cci"
            p.write_bytes(b)
            before = hashlib.sha256(b).hexdigest()
            r = subprocess.run([EXE, str(p), *options], capture_output=True, text=True)
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

    def test_deep_valid(self):
        out=self.run_image(deep_image(),options=("--verify","--list-romfs"))
        self.assertIn("romfs_superblock_hash=verified bytes=512",out)
        self.assertIn('path="/a" size=3 absolute_offset=1136',out)
        self.assertIn("directories=1 files=1 file_bytes=3",out)
    def test_hash_mismatch(self):
        b=deep_image()
        b[0x1e0] ^= 1
        self.run_image(b,False,("--verify",))
    def test_encrypted_skip(self):
        b=deep_image()
        b[0x18f]=0
        b[512:516]=b"NOPE"
        out=self.run_image(b,options=("--verify","--list-romfs"))
        self.assertIn("content_hashes=skipped_encrypted",out)
        self.assertIn("romfs_listing=skipped_encrypted",out)
    def test_deep_mutations(self):
        # Metadata corruption is outside the NCCH superblock hash region.
        changes=[(1024,39),(1024+12,36),(1024+36,80),
                 (1024+44,4),(1024+48,0),(1024+52,0),
                 (1024+56,4),(1024+72,4),(1024+76,0),
                 (1024+100,3),(1024+88,0xffffffff),
                 (512+0x4c,255),(512+4,0),(512+8,0xffffffff)]
        for p,v in changes:
            b=deep_image()
            put(b,p,v)
            with self.subTest(p=p,v=v):
                self.run_image(b,False,("--list-romfs",))
    def test_unsafe_name(self):
        for value in [0,ord("/"),ord("\\")]:
            b=deep_image()
            struct.pack_into("<H",b,1128,value)
            self.run_image(b,False,("--list-romfs",))
    def test_logo_exheader_exefs_hashes(self):
        b=bytearray(8192)
        b[256:260]=b"NCCH"
        put(b,0x104,16)
        b[0x18f]=4
        put(b,0x180,0x400)
        put(b,0x198,5)
        put(b,0x19c,1)
        put(b,0x1a0,6)
        put(b,0x1a4,1)
        put(b,0x1a8,1)
        for start,n,target in [(512,1024,0x160),(2560,512,0x130),(3072,512,0x1c0)]:
            b[target:target+32]=hashlib.sha256(b[start:start+n]).digest()
        out=self.run_image(b,options=("--verify",))
        for label in ["logo","exheader","exefs"]:
            self.assertIn(label+"_hash=verified",out)
        for pos in [512,2560,3072]:
            broken=b.copy()
            broken[pos]^=1
            self.run_image(broken,False,("--verify",))
    def test_unknown_option(self):
        self.assertEqual(subprocess.run([EXE,"unused","--bad"],capture_output=True).returncode,2)


    def test_nested_unicode_tree(self):
        out=self.run_image(tree_image(["sub","deep"],"ñ"),options=("--verify","--list-romfs"))
        self.assertIn('path="/sub/deep/\\u00f1" size=3',out)
        self.assertIn("directories=3 files=1",out)
    def test_empty_tree(self):
        self.assertIn("files=0",self.run_image(tree_image(filename=None),options=("--list-romfs",)))
    def test_complete_path_budget(self):
        self.run_image(tree_image(["a"*500]*16,"b"*500),False,("--list-romfs",))
    def test_missing_hash_range_not_absent(self):
        b=deep_image()
        put(b,0x1b8,0)
        self.assertIn("romfs_superblock_hash=not_verified_empty_hash_range",
                      self.run_image(b,options=("--verify",)))
    def test_report_comparison_state(self):
        out=self.run_image(deep_image(),options=("--verify",))
        self.assertNotIn("stored_hashes=reported_only",out)
    def test_metadata_budget(self):
        b=deep_image()
        put(b,1024+16,64*1024*1024+4)
        self.run_image(b,False,("--list-romfs",))


    def test_ivfc_integrity(self):
        for size in [115,512,777,16385]:
            out=self.run_image(integrity_image(size),options=("--verify-integrity","--list-romfs"))
            self.assertIn("ivfc_tree=verified levels=3",out)
    def test_ivfc_corrupted_levels(self):
        for p in [1024+112,1536,2048]:
            b=integrity_image()
            b[p]^=1
            self.run_image(b,False,("--verify-integrity",))
    def test_ivfc_corrupted_padding(self):
        b=integrity_image(115); b[1024+115]=1
        self.run_image(b,False,("--verify-integrity",))
    def test_ivfc_bad_layout(self):
        for p,v in [(512+8,0),(512+0x1c,63),(512+0x34,0),(512+0xc,1),
                    (512+0x24,1),(512+0x2c,0),(512+0x3c,1)]:
            b=integrity_image(); put(b,p,v)
            b[0x1e0:0x200]=hashlib.sha256(b[512:1024]).digest()
            self.run_image(b,False,("--verify-integrity",))
    def test_exefs_files(self):
        out=self.run_image(exefs_image(),options=("--verify-integrity",))
        self.assertIn("exefs_files=verified count=2",out)
    def test_exefs_corruption(self):
        for p in [1024,1536]:
            b=exefs_image(); b[p]^=1
            self.run_image(b,False,("--verify-integrity",))
    def test_exefs_hash_order(self):
        b=exefs_image()
        b[512+0x1c0:512+0x1e0],b[512+0x1e0:512+0x200]=b[512+0x1e0:512+0x200],b[512+0x1c0:512+0x1e0]
        b[0x1c0:0x1e0]=hashlib.sha256(b[512:1024]).digest()
        self.run_image(b,False,("--verify-integrity",))
    def test_exefs_invalid_entries(self):
        for p,v in [(512+8,0xffffffff),(512+12,0xffffffff),(512+16+8,0)]:
            b=exefs_image(); put(b,p,v)
            b[0x1c0:0x1e0]=hashlib.sha256(b[512:1024]).digest()
            self.run_image(b,False,("--verify-integrity",))
    def test_integrity_encrypted_skip(self):
        b=integrity_image(); b[0x18f]=0
        self.assertIn("file_integrity=skipped_encrypted",self.run_image(b,options=("--verify-integrity",)))

    def test_usage(self):
        self.assertEqual(subprocess.run([EXE],capture_output=True).returncode,2)

if __name__ == "__main__":
    unittest.main()

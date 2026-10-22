import hashlib
import secrets
import math
import zlib
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


def integrity_image(lvsize=512, level3=None):
    src=tree_image()
    block=512
    ceil=lambda n:(n+block-1)//block*block
    body=bytes(src[1024:] if level3 is None else level3)
    body=(body+bytes(max(0,ceil(lvsize)-len(body))))[:ceil(lvsize)]
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


def indexed_image(names=(), filename="a", buckets=3):
    src=tree_image(names,filename)
    hdr=struct.unpack_from("<10I",src,1024)
    dirs=bytearray(src[1024+hdr[3]:1024+hdr[3]+hdr[4]])
    files=bytearray(src[1024+hdr[7]:1024+hdr[7]+hdr[8]])
    def make_table(raw,fixed):
        heads=[0xffffffff]*buckets
        at=0
        while at<len(raw):
            parent=struct.unpack_from("<I",raw,at)[0]
            n=struct.unpack_from("<I",raw,at+fixed-4)[0]
            value=parent^123456789
            for unit in struct.unpack_from("<"+"H"*(n//2),raw,at+fixed):
                value=(((value>>5)|(value<<27))^unit)&0xffffffff
            i=value%buckets
            put(raw,at+(16 if fixed==24 else 24),heads[i])
            heads[i]=at
            at+=fixed+(n+3)//4*4
        return struct.pack("<"+"I"*buckets,*heads)
    dh=make_table(dirs,24); fh=make_table(files,32)
    dm=40+len(dh); fhoff=dm+len(dirs); fm=fhoff+len(fh)
    data=(fm+len(files)+15)//16*16
    lv=bytearray((data+3+511)//512*512)
    struct.pack_into("<10I",lv,0,40,40,len(dh),dm,len(dirs),fhoff,len(fh),fm,len(files),data)
    lv[40:dm]=dh; lv[dm:fhoff]=dirs
    lv[fhoff:fm]=fh; lv[fm:fm+len(files)]=files
    lv[data:data+3]=b"abc"
    return integrity_image(len(lv),lv)
def rehash_index_image(b):
    n=struct.unpack_from("<Q",b,512+0x44)[0]
    return integrity_image(n,b[1024:1024+n])


_EPHEMERAL_RSA=None
def synthetic_rsa():
    global _EPHEMERAL_RSA
    if _EPHEMERAL_RSA:return _EPHEMERAL_RSA
    def probable_prime(n):
        small=[2,3,5,7,11,13,17,19,23,29,31,37]
        if any(n%p==0 for p in small):return False
        d=n-1;s=0
        while d%2==0:s+=1;d//=2
        for a in small:
            x=pow(a,d,n)
            if x in (1,n-1):continue
            for _ in range(s-1):
                x=x*x%n
                if x==n-1:break
            else:return False
        return True
    def prime():
        while True:
            n=secrets.randbits(1024)|(1<<1023)|1
            if math.gcd(n-1,65537)==1 and probable_prime(n):return n
    while True:
        p,q=prime(),prime()
        n=p*q
        if p!=q and n.bit_length()==2048:break
    _EPHEMERAL_RSA=(n,pow(65537,-1,(p-1)*(q-1)))
    return _EPHEMERAL_RSA
def signed_synthetic_image():
    n,d=synthetic_rsa()
    b=bytearray(4096);b[256:260]=b"NCCH"
    put(b,0x104,8);put(b,0x180,0x400);b[0x18f]=4;b[0x18d]=2
    b[0x700:0x800]=n.to_bytes(256,"big")
    em=bytes.fromhex("0001"+"ff"*202+"00"+"3031300d060960864801650304020105000420")+hashlib.sha256(b[256:512]).digest()
    b[:256]=pow(int.from_bytes(em,"big"),d,n).to_bytes(256,"big")
    return b
def resource_image(payload):
    b=indexed_image()
    lvsize=struct.unpack_from("<Q",b,512+0x44)[0]
    lv=bytearray(b[1024:1024+lvsize])
    fm=struct.unpack_from("<I",lv,28)[0]
    data=struct.unpack_from("<I",lv,36)[0]
    if data+len(payload)>len(lv):lv+=bytes((data+len(payload)+511)//512*512-len(lv))
    struct.pack_into("<Q",lv,fm+16,len(payload))
    lv[data:data+len(payload)]=payload
    return integrity_image(len(lv),lv)
def arc19():
    b=bytearray(100)
    b[:4]=b"ARC"+bytes(1);struct.pack_into("<HH",b,4,19,1)
    b[12:16]=b"test";struct.pack_into("<4I",b,76,123,8,10,92)
    return b


def compressed_arc(payload, compressed=None, expected=None):
    packed=zlib.compress(payload) if compressed is None else compressed
    b=bytearray(92+len(packed))
    b[:4]=b"ARC"+bytes(1);struct.pack_into("<HH",b,4,19,1)
    b[12:16]=b"test"
    struct.pack_into("<4I",b,76,123,len(packed),len(payload) if expected is None else expected,92)
    b[92:]=packed
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

    def test_integrity_requires_master_coverage(self):
        b=integrity_image(); put(b,0x1b8,0)
        self.run_image(b,False,("--verify-integrity",))
    def test_integrity_requires_exefs_header_coverage(self):
        b=exefs_image(); put(b,0x1a8,0)
        self.run_image(b,False,("--verify-integrity",))


    def test_romfs_index_valid(self):
        out=self.run_image(indexed_image(["sub","ñ","𐐀"]),options=("--verify-romfs-index",))
        self.assertIn("type=directories hash_buckets=verified",out)
        self.assertIn("entries=4",out)
        self.assertIn("hash_buckets=verified",out)
        self.assertNotIn("romfs_file path=",out)
    def test_romfs_index_and_listing(self):
        out=self.run_image(indexed_image(["sub"]),options=("--verify-romfs-index","--list-romfs"))
        self.assertIn('path="/sub/a"',out)
    def test_romfs_index_empty_files(self):
        out=self.run_image(indexed_image(filename=None),options=("--verify-romfs-index",))
        self.assertIn("type=files hash_buckets=verified buckets=3 used=0 entries=0",out)
    def test_romfs_index_collisions(self):
        out=self.run_image(indexed_image(["x","y","z"],buckets=1),options=("--verify-romfs-index",))
        self.assertIn("entries=4 max_chain=4",out)
    def test_romfs_index_missing_record(self):
        b=indexed_image()
        dh=struct.unpack_from("<I",b,1028)[0]
        for i in range(3): put(b,1024+dh+4*i,0xffffffff)
        self.run_image(rehash_index_image(b),False,("--verify-romfs-index",))
    def test_romfs_index_wrong_bucket(self):
        b=indexed_image()
        dh=struct.unpack_from("<I",b,1028)[0]
        heads=list(struct.unpack_from("<3I",b,1024+dh))
        heads=heads[1:]+heads[:1]
        struct.pack_into("<3I",b,1024+dh,*heads)
        self.run_image(rehash_index_image(b),False,("--verify-romfs-index",))
    def test_romfs_index_invalid_bucket_link(self):
        for value in [1,0xfffffffe]:
            b=indexed_image()
            dh=struct.unpack_from("<I",b,1028)[0]
            put(b,1024+dh,value)
            self.run_image(rehash_index_image(b),False,("--verify-romfs-index",))
    def test_romfs_index_cycles(self):
        for table,field in [(3,16),(7,24)]:
            b=indexed_image()
            off=struct.unpack_from("<I",b,1024+4*table)[0]
            put(b,1024+off+field,0)
            self.run_image(rehash_index_image(b),False,("--verify-romfs-index",))
    def test_romfs_index_shared_record(self):
        b=indexed_image()
        dh=struct.unpack_from("<I",b,1028)[0]
        for i in range(3):put(b,1024+dh+4*i,0)
        self.run_image(rehash_index_image(b),False,("--verify-romfs-index",))
    def test_romfs_index_encrypted_skip(self):
        b=indexed_image(); b[0x18f]=0
        self.assertIn("romfs_index=skipped_encrypted",self.run_image(b,options=("--verify-romfs-index",)))


    def test_signature_valid_embedded_untrusted(self):
        out=self.run_image(signed_synthetic_image(),options=("--inspect-signatures",))
        self.assertIn("ncch_header_signature=valid_with_embedded_key",out)
        self.assertIn("trust=not_established",out)
    def test_signature_invalid(self):
        b=signed_synthetic_image();b[0x120]^=1
        self.assertIn("ncch_header_signature=invalid_with_embedded_key",
                      self.run_image(b,options=("--inspect-signatures",)))
    def test_signature_invalid_signature_bytes(self):
        b=signed_synthetic_image();b[0]^=1
        self.assertIn("ncch_header_signature=invalid_with_embedded_key",
                      self.run_image(b,options=("--inspect-signatures",)))
    def test_signature_invalid_modulus(self):
        b=signed_synthetic_image();b[0x700:0x800]=bytes(256)
        self.assertIn("not_checked_invalid_embedded_modulus",
                      self.run_image(b,options=("--inspect-signatures",)))
    def test_signature_skip_profiles(self):
        self.assertIn("not_checked_no_embedded_key",self.run_image(ncch(),options=("--inspect-signatures",)))
        b=signed_synthetic_image();b[0x18f]=0
        self.assertIn("not_checked_encrypted_exheader",self.run_image(b,options=("--inspect-signatures",)))
    def test_resource_arc19(self):
        out=self.run_image(resource_image(arc19()),options=("--inspect-resources",))
        self.assertIn("arc=1 arc19_entries=1",out)
        self.assertIn("arc_version=19 files=1",out)
    def test_resource_arc19_ranges(self):
        for p,v in [(80,99),(88,11),(88,1000)]:
            b=arc19();put(b,p,v)
            self.run_image(resource_image(b),False,("--inspect-resources",))
        overlapping=bytearray(180);overlapping[:4]=b"ARC"+bytes(1)
        struct.pack_into("<HH",overlapping,4,19,2)
        struct.pack_into("<4I",overlapping,76,1,8,8,172)
        struct.pack_into("<4I",overlapping,156,2,8,8,172)
        self.run_image(resource_image(overlapping),False,("--inspect-resources",))
        oversized=bytearray(12);oversized[:4]=b"ARC"+bytes(1)
        struct.pack_into("<HH",oversized,4,19,65535)
        self.run_image(resource_image(oversized),False,("--inspect-resources",))
    def test_resource_arc_table_truncated(self):
        self.run_image(resource_image(arc19()[:80]),False,("--inspect-resources",))
    def test_resource_arc_unsupported(self):
        b=arc19();struct.pack_into("<H",b,4,17)
        out=self.run_image(resource_image(b),options=("--inspect-resources",))
        self.assertIn("unsupported=1",out)
    def test_resource_tex_header(self):
        b=bytearray(16);b[:4]=b"TEX"+bytes(1)
        put(b,4,165);put(b,8,1|(16<<6)|(32<<19));b[12]=1
        self.assertIn("tex=1",self.run_image(resource_image(b),options=("--inspect-resources",)))
        put(b,8,1)
        self.run_image(resource_image(b),False,("--inspect-resources",))
    def test_resource_truncated_magic(self):
        for payload in [b"ARC"+bytes(1),b"TEX"+bytes(1)]:
            self.run_image(resource_image(payload),False,("--inspect-resources",))

    def test_signature_outside_modulus(self):
        b=signed_synthetic_image();b[:256]=bytes([255])*256
        self.assertIn("ncch_header_signature=invalid_with_embedded_key",
                      self.run_image(b,options=("--inspect-signatures",)))


    def test_arc_zlib_valid_prefix(self):
        payload=b"MOD"+bytes(1)+struct.pack("<H",230)+bytes(range(256))*1024
        out=self.run_image(resource_image(compressed_arc(payload)),options=("--validate-arc-zlib",))
        self.assertIn("validated_entries=1",out)
        self.assertIn("kind=MOD version_field16=230 entries=1",out)
    def test_arc_zlib_input_chunks(self):
        payload=secrets.token_bytes(150000)
        out=self.run_image(resource_image(compressed_arc(payload)),options=("--validate-arc-zlib",))
        self.assertIn("decoded_bytes=150000",out)
    def test_arc_zlib_empty_output(self):
        out=self.run_image(resource_image(compressed_arc(b"")),options=("--validate-arc-zlib",))
        self.assertIn("validated_entries=1 decoded_bytes=0",out)
    def test_arc_zlib_corruption(self):
        payload=b"TEX"+bytes(1)+struct.pack("<H",165)+b"abc"*1000
        packed=zlib.compress(payload)
        bad_checksum=bytearray(packed);bad_checksum[-1]^=1
        for broken in [bytes(bad_checksum),packed[:-1],b"bad",packed+b"junk",packed+packed,packed[2:-4]]:
            self.run_image(resource_image(compressed_arc(payload,broken)),False,("--validate-arc-zlib",))
    def test_arc_zlib_size_mismatch(self):
        for size in [0,9,11,64*1024*1024+1]:
            self.run_image(resource_image(compressed_arc(b"0123456789",expected=size)),False,("--validate-arc-zlib",))
    def test_arc_zlib_expansion_limit(self):
        self.run_image(resource_image(compressed_arc(bytes(1000000),expected=8)),False,("--validate-arc-zlib",))
    def test_arc_zlib_dictionary_rejected(self):
        c=zlib.compressobj(zdict=b"some dictionary")
        payload=b"some dictionary repeated"
        packed=c.compress(payload)+c.flush()
        self.run_image(resource_image(compressed_arc(payload,packed)),False,("--validate-arc-zlib",))
    def test_arc_zlib_empty_input_rejected(self):
        self.run_image(resource_image(compressed_arc(b"",b"")),False,("--validate-arc-zlib",))

    def test_usage(self):
        self.assertEqual(subprocess.run([EXE],capture_output=True).returncode,2)

if __name__ == "__main__":
    unittest.main()

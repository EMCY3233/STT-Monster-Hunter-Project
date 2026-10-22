import copy
import io
import json
from pathlib import Path
import socket
import struct
import tempfile
import threading
import unittest
import zlib
from stt_monitor.visual_protocol import Assembler, HEADER, PIXELS, CHUNK, png_rgb565
from stt_monitor.visual_receiver import receive


def fixture(frame=0):
    scene = json.loads(Path('contracts/examples/snapshot.json').read_text())
    scene.update(session='vita-perf-1234', seq=frame)
    meta = dict(version=1, width=240, height=136, format='rgb565le', frame=frame,
                equipment=0, ground_mode=1, target=dict(id=1,pos_mm=[0,0,0],hp=100,reaction_ticks=0),scene=scene)
    encoded = json.dumps(meta, separators=(',', ':')).encode()
    body = encoded + b'\x00\xf8'*(PIXELS//2)
    return [HEADER.pack(b'STV1', 0x1234, frame, len(body), offset, min(CHUNK, len(body)-offset),len(encoded))+
            body[offset:offset+CHUNK] for offset in range(0,len(body),CHUNK)]


class VisualTests(unittest.TestCase):
    def test_out_of_order_duplicate_scene_pair_and_png_pixels(self):
        packets = fixture()
        a = Assembler()
        self.assertIsNone(a.feed(packets[-1], '127.0.0.1', 0))
        self.assertIsNone(a.feed(packets[-1], '127.0.0.1', 0))
        result = None
        for raw in reversed(packets[:-1]):
            result = a.feed(raw,'127.0.0.1',1)
        stream, frame, meta, pixels = result
        self.assertEqual((stream,frame), (0x1234,0))
        self.assertEqual(meta['scene']['session'], 'vita-perf-1234')
        png = png_rgb565(pixels)
        self.assertEqual(png[:8], b'\x89PNG\r\n\x1a\n')
        offset = 8
        compressed = b''
        while offset<len(png):
            length = struct.unpack_from('!I',png,offset)[0]
            kind=png[offset+4:offset+8];data=png[offset+8:offset+8+length]
            self.assertEqual(struct.unpack_from('!I',png,offset+8+length)[0],zlib.crc32(kind+data))
            if kind==b'IDAT': compressed+=data
            offset+=12+length
        row=b'\x00'+b'\xff\x00\x00'*240
        self.assertEqual(zlib.decompress(compressed),row*136)
        self.assertIsNone(a.feed(packets[0],'127.0.0.1',2))
        self.assertEqual(a.stats['duplicates'],2)

    def test_bad_headers_conflicts_and_memory_timeout(self):
        raw=fixture()[0]
        for bad in (b'',raw[:-1],b'NOPE'+raw[4:],raw+b'x'):
            with self.subTest(size=len(bad)),self.assertRaises(ValueError):
                Assembler().feed(bad,'p',0)
        a=Assembler();a.feed(raw,'p',0)
        changed=raw[:-1]+bytes([raw[-1]^1])
        with self.assertRaises(ValueError): a.feed(changed,'p',1)
        self.assertFalse(a.pending)
        for frame in range(1,4): a.feed(fixture(frame)[0],'p',1)
        self.assertEqual(len(a.pending),2)
        self.assertEqual(a.stats['evicted'],1)
        a.expire(6)
        self.assertFalse(a.pending)
        self.assertEqual(a.stats['expired'],2)
        self.assertLessEqual(len(a.finished),128)

    def test_udp_receiver_pairs_files_and_limits(self):
        with tempfile.TemporaryDirectory() as folder, socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock, socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sender:
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,256*1024)
            sock.bind(('127.0.0.1',0));result={}
            def run(): result.update(receive(sock,Path(folder),duration=3,idle_timeout=2,max_frames=1))
            thread=threading.Thread(target=run);thread.start()
            sender.sendto(b'invalid',sock.getsockname())
            for raw in fixture(): sender.sendto(raw,sock.getsockname())
            thread.join(5);self.assertFalse(thread.is_alive())
            self.assertEqual(result['frames'],1)
            self.assertEqual(result['rejected_datagrams'],1)
            self.assertEqual(result['stop_reason'],'max_frames')
            data=json.loads((Path(folder)/'frame-0000.json').read_text())
            self.assertEqual(data['metadata']['scene']['source'],'simulator')
            self.assertTrue((Path(folder)/data['image']).read_bytes().startswith(b'\x89PNG'))
            self.assertTrue((Path(folder)/'index.html').exists())

    def test_rejects_mismatched_scene_and_cross_peer_fragments(self):
        from stt_monitor.visual_protocol import validate_metadata
        first = fixture()[0]
        # Validate scene separately without inventing a second wire schema.
        scene = json.loads(Path('contracts/examples/snapshot.json').read_text())
        scene.update(session='vita-perf-1234', seq=0)
        meta = dict(version=1,width=240,height=136,format='rgb565le',frame=0,
                    equipment=0,ground_mode=1,target=dict(id=1,pos_mm=[0,0,0],hp=100,reaction_ticks=0),scene=scene)
        mutations = [lambda m:m.update(width=480),lambda m:m.update(version=True),
                     lambda m:m['scene'].update(session='another'),
                     lambda m:m.update(extra=1),lambda m:m.update(equipment=4)]
        for mutate in mutations:
            m=copy.deepcopy(meta);mutate(m)
            with self.assertRaises(ValueError):
                validate_metadata(json.dumps(m).encode(),0x1234,0)
        a=Assembler();packets=fixture()
        for raw in packets[:-1]: self.assertIsNone(a.feed(raw,'peer-a',0))
        self.assertIsNone(a.feed(packets[-1],'peer-b',0))
        self.assertEqual(len(a.pending),2)
        a.expire(5)
        self.assertEqual(a.stats['expired'],2)

    def test_rejects_quota_before_writing_an_image(self):
        import unittest.mock
        class Input:
            def __init__(self): self.packets=iter(fixture())
            def settimeout(self,value): pass
            def recvfrom(self,size): return next(self.packets),('127.0.0.1',1234)
        with tempfile.TemporaryDirectory() as folder:
            result=receive(Input(),Path(folder),max_bytes=1)
            self.assertEqual(result['stop_reason'],'max_bytes')
            self.assertEqual(result['frames'],0)
            self.assertFalse(list(Path(folder).glob('*.png')))

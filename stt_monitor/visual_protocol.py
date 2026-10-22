"""STV/1 visual companion: bounded fragments, immutable RGB565 + STT/3 scene."""
import json
import struct
import zlib
from collections import OrderedDict
from .play_protocol import validate_play, obj, integer

WIDTH, HEIGHT = 240, 136
PIXELS = WIDTH * HEIGHT * 2
CHUNK, META_MAX = 1000, 1536
HEADER = struct.Struct('!4sQIIIHH')
MAX_DATAGRAM = HEADER.size + CHUNK


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate metadata field')
        result[key] = value
    return result


def validate_metadata(raw, stream, frame):
    try:
        m = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    except (UnicodeError, RecursionError) as exc:
        raise ValueError('invalid scene JSON') from exc
    keys = {'version', 'width', 'height', 'format', 'frame', 'equipment', 'ground_mode', 'target', 'scene'}
    if type(m) is not dict or set(m) != keys:
        raise ValueError('invalid visual fields')
    for key, value in [('version', 1), ('width', WIDTH), ('height', HEIGHT), ('frame', frame)]:
        if type(m[key]) is not int or m[key] != value:
            raise ValueError('invalid visual identity')
    if m['format'] != 'rgb565le':
        raise ValueError('unsupported pixel format')
    for key, high in [('equipment', 3), ('ground_mode', 1)]:
        if type(m[key]) is not int or not 0 <= m[key] <= high:
            raise ValueError('invalid scene mode')
    target=m['target']
    obj(target,'id pos_mm hp reaction_ticks')
    integer(target['id'],1,4294967295)
    integer(target['hp'],0,1000000)
    integer(target['reaction_ticks'],0,65535)
    if type(target['pos_mm']) is not list or len(target['pos_mm'])!=3:
        raise ValueError('invalid target position')
    for value in target['pos_mm']: integer(value,-100000000,100000000)
    scene = validate_play(m['scene'])
    if scene['session'] != f'vita-perf-{stream:x}' or scene['seq'] != frame:
        raise ValueError('scene/image identity mismatch')
    return m


class Assembler:
    """At most two ~67 KiB images; expire incomplete images after five seconds."""
    def __init__(self):
        self.pending = OrderedDict()
        self.finished = OrderedDict()
        self.stats = dict(duplicates=0, expired=0, evicted=0)

    def expire(self, now):
        for key, state in list(self.pending.items()):
            if now - state['started'] >= 5:
                del self.pending[key]
                self.stats['expired'] += 1
                self.remember(key)

    def remember(self, key):
        self.finished[key] = None
        if len(self.finished) > 128:
            self.finished.popitem(last=False)

    def feed(self, raw, peer, now):
        self.expire(now)
        if len(raw) < HEADER.size or len(raw) > MAX_DATAGRAM:
            raise ValueError('invalid visual datagram size')
        magic, stream, frame, total, offset, count, meta = HEADER.unpack_from(raw)
        if (magic != b'STV1' or not 0 < meta < META_MAX or total != PIXELS + meta or
                offset >= total or offset % CHUNK or count != min(CHUNK, total-offset) or
                len(raw) != HEADER.size + count):
            raise ValueError('invalid fragment header')
        key = (peer, stream, frame)
        if key in self.finished:
            self.stats['duplicates'] += 1
            return None
        state = self.pending.get(key)
        if state is None:
            if len(self.pending) == 2:
                old, _ = self.pending.popitem(last=False)
                self.remember(old)
                self.stats['evicted'] += 1
            state = self.pending[key] = dict(started=now, total=total, meta=meta,
                                             data=bytearray(total), seen=set())
        if state['total'] != total or state['meta'] != meta:
            del self.pending[key]
            self.remember(key)
            raise ValueError('conflicting frame size')
        body = raw[HEADER.size:]
        if offset in state['seen']:
            if state['data'][offset:offset+count] != body:
                del self.pending[key]
                self.remember(key)
                raise ValueError('conflicting duplicate')
            self.stats['duplicates'] += 1
            return None
        state['data'][offset:offset+count] = body
        state['seen'].add(offset)
        if len(state['seen']) != (total + CHUNK - 1)//CHUNK:
            return None
        del self.pending[key]
        self.remember(key)
        metadata = validate_metadata(bytes(state['data'][:meta]), stream, frame)
        return stream, frame, metadata, bytes(state['data'][meta:])


def png_rgb565(pixels):
    if len(pixels) != PIXELS:
        raise ValueError('invalid complete image length')
    rows = bytearray()
    for y in range(HEIGHT):
        rows.append(0)
        for x in range(WIDTH):
            i = (y*WIDTH+x)*2
            v = pixels[i] | pixels[i+1] << 8
            r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
            rows.extend(((r*255+15)//31, (g*255+31)//63, (b*255+15)//31))
    def chunk(kind, data):
        return struct.pack('!I', len(data)) + kind + data + struct.pack('!I', zlib.crc32(kind+data))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('!IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(rows)) + chunk(b'IEND', b''))

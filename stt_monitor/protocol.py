"""Strict, bounded STT/1 and STT/2 datagrams. Standard library only."""
import json
import math
import re

MAX_BYTES = 1024
FIELDS = {'version', 'session', 'source', 'seq', 'uptime_ms', 'battery_pct'}


def validate(packet):
    if not isinstance(packet, dict):
        raise ValueError('expected object')
    version = packet.get('version')
    if type(version) is int and version in (4, 5):
        from .perf_protocol import validate_perf
        return validate_perf(packet)
    if type(version) is int and version == 3:
        from .play_protocol import validate_play
        return validate_play(packet)
    if type(version) is not int or version not in (1, 2):
        raise ValueError('unsupported version')
    expected = FIELDS if version == 1 else FIELDS | {'diagnostics'}
    if set(packet) != expected:
        raise ValueError('unexpected or missing fields')
    if not isinstance(packet['session'], str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', packet['session']):
        raise ValueError('invalid session')
    if packet['source'] not in ('simulator', 'vita'):
        raise ValueError('invalid source')
    for key in ('seq', 'uptime_ms'):
        if type(packet[key]) is not int or not 0 <= packet[key] <= 2**53 - 1:
            raise ValueError('invalid ' + key)
    battery = packet['battery_pct']
    if battery is not None and (type(battery) not in (int, float) or not math.isfinite(battery) or not 0 <= battery <= 100):
        raise ValueError('invalid battery_pct')
    if version == 2:
        d = packet['diagnostics']
        if not isinstance(d, dict) or set(d) != {'send_ok', 'send_errors', 'last_result', 'net_errno'}:
            raise ValueError('invalid diagnostics fields')
        for key in ('send_ok', 'send_errors'):
            if type(d[key]) is not int or not 0 <= d[key] <= packet['seq']:
                raise ValueError('invalid diagnostics counter')
        if d['send_ok'] + d['send_errors'] != packet['seq']:
            raise ValueError('diagnostics counters must describe prior attempts')
        for key in ('last_result', 'net_errno'):
            if type(d[key]) is not int or not -(2**31) <= d[key] < 2**31:
                raise ValueError('invalid diagnostics code')
    return packet


def encode(packet):
    raw = json.dumps(validate(packet), separators=(',', ':'), allow_nan=False).encode('utf-8')
    if len(raw) > MAX_BYTES:
        raise ValueError('packet too large')
    return raw


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate field')
        result[key] = value
    return result


def decode(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('packet too large')
    try:
        return validate(json.loads(raw.decode('utf-8'), object_pairs_hook=_unique))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('invalid JSON/UTF-8') from exc

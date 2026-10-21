"""Strict STT/3 original prototype snapshots; STT/1 and /2 remain unchanged."""
import re

STATES = ('idle', 'move', 'windup', 'active', 'recovery', 'stunned')
LIMIT = 2**53 - 1


def obj(value, keys):
    if type(value) is not dict or set(value) != set(keys.split()):
        raise ValueError('invalid object fields')


def integer(value, low=0, high=LIMIT):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('invalid integer')


def validate_play(packet):
    obj(packet, 'version session source seq uptime_ms battery_pct play')
    integer(packet['version'], 3, 3)
    if type(packet['session']) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', packet['session']):
        raise ValueError('invalid session')
    if packet['source'] not in ('simulator', 'vita'):
        raise ValueError('invalid source')
    for k in ('seq', 'uptime_ms'):
        integer(packet[k])
    if packet['battery_pct'] is not None:
        integer(packet['battery_pct'], 0, 100)
    p = packet['play']
    obj(p, 'version tick origin hunter camera attack hits perf aquatic')
    integer(p['version'], 1, 1)
    integer(p['tick'])
    if p['origin'] != 'original-prototype' or p['aquatic'] is not None:
        raise ValueError('unsupported origin or aquatic extension')
    h = p['hunter']
    obj(h, 'state pos_mm yaw_mdeg hp')
    if h['state'] not in STATES:
        raise ValueError('invalid state')
    if type(h['pos_mm']) is not list or len(h['pos_mm']) != 3:
        raise ValueError('invalid position')
    for v in h['pos_mm']:
        integer(v, -100000000, 100000000)
    integer(h['yaw_mdeg'], -180000, 180000)
    integer(h['hp'], 0, 1000000)
    c = p['camera']
    obj(c, 'yaw_mdeg pitch_mdeg distance_mm')
    integer(c['yaw_mdeg'], -180000, 180000)
    integer(c['pitch_mdeg'], -89000, 89000)
    integer(c['distance_mm'], 1, 1000000)
    a = p['attack']
    obj(a, 'id phase_tick')
    integer(a['id'], 0, 4294967295)
    integer(a['phase_tick'], 0, 65535)
    if type(p['hits']) is not list or len(p['hits']) > 2:
        raise ValueError('too many hits')
    targets = set()
    for hit in p['hits']:
        obj(hit, 'attack target damage hp')
        integer(hit['attack'], 1, 4294967295)
        integer(hit['target'], 1, 4294967295)
        integer(hit['damage'], 0, 1000000)
        integer(hit['hp'], 0, 1000000)
        key = hit['attack'], hit['target']
        if key in targets:
            raise ValueError('duplicate hit')
        targets.add(key)
    f = p['perf']
    obj(f, 'frame_us update_us dropped')
    integer(f['frame_us'], 0, 10000000)
    integer(f['update_us'], 0, 10000000)
    integer(f['dropped'], 0, 4294967295)
    return packet

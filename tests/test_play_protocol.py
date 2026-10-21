import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from stt_monitor.protocol import decode, encode, validate
from stt_monitor.analyze import summarize

ROOT = Path(__file__).resolve().parents[1]


class PlayProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample = json.loads((ROOT / 'contracts/examples/snapshot.json').read_text())

    def test_roundtrip_and_analysis(self):
        p = decode(encode(self.sample))
        self.assertEqual(p, self.sample)
        self.assertLessEqual(len(encode(p)), 1024)
        result = summarize([json.dumps(dict(packet=p, peer_ip='127.0.0.1'))])
        self.assertEqual(result['invalid_lines'], 0)
        self.assertEqual(result['sessions'][0]['unique_packets'], 1)

    def test_c_cross_validation(self):
        cc = shutil.which('cc')
        if not cc:
            self.skipTest('portable C compiler not available')
        with tempfile.TemporaryDirectory() as d:
            exe = str(Path(d) / 'encoder')
            subprocess.run([cc, '-std=c99', '-Wall', '-Wextra', '-Werror', '-Icontracts',
                            'contracts/stt_play.c', 'contracts/tests/encode.c', '-o', exe], cwd=ROOT, check=True)
            packets = subprocess.check_output([exe]).splitlines()
        self.assertEqual(len(packets), 2)
        for raw in packets:
            self.assertEqual(encode(decode(raw)), raw)

    def test_malformed(self):
        mutations = [lambda p: p.update(version=True), lambda p: p.update(extra=1),
                     lambda p: p['play'].update(aquatic={}),
                     lambda p: p['play']['hunter'].update(hp=True),
                     lambda p: p['play']['hunter'].update(pos_mm=[0, 0]),
                     lambda p: p['play']['camera'].update(pitch_mdeg=90000),
                     lambda p: p['play'].update(hits=[dict(attack=1,target=1,damage=1,hp=1)]*2),
                     lambda p: p['play'].update(hits=[{}]*3),
                     lambda p: p['play'].update(origin='commercial'),
                     lambda p: p.update(seq=2**53)]
        for mutation in mutations:
            p = copy.deepcopy(self.sample)
            mutation(p)
            with self.assertRaises(ValueError):
                validate(p)
        for raw in (b'{"version":3,"version":3}', b'x'*1025, b'\xff', b'[]'):
            with self.assertRaises(ValueError):
                decode(raw)

    def test_existing_versions(self):
        p = dict(version=1, session='legacy', source='vita', seq=0, uptime_ms=0, battery_pct=None)
        self.assertEqual(decode(encode(p)), p)
        p.update(version=2, diagnostics=dict(send_ok=0,send_errors=0,last_result=0,net_errno=0))
        self.assertEqual(decode(encode(p)), p)

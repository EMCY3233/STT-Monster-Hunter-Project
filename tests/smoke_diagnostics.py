"""Synthetic end-to-end check: python tests/smoke_diagnostics.py (loopback only)."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stt_monitor.analyze import summarize

# This sender runs as the second child process. All data is synthetic, including
# source=vita: that field exercises the contract and is not proof of hardware.
SENDER = '''
import socket
from stt_monitor.protocol import encode
from stt_monitor.simulator import packet
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    address = ('127.0.0.1', 32110)
    sock.sendto(b'{', address)
    sock.sendto(b'not-json', address)
    for session, seq in [('synthetic-a',0), ('synthetic-a',2), ('synthetic-a',2),
                         ('synthetic-a',1), ('synthetic-restart',0)]:
        p = packet(session, seq, seq*1000)
        errors = 1 if seq else 0
        p.update(source='vita', version=2, diagnostics=dict(send_ok=seq-errors,
                 send_errors=errors, last_result=0x804101CD-2**32, net_errno=205))
        sock.sendto(encode(p), address)
'''

with tempfile.TemporaryDirectory() as folder:
    output = Path(folder) / 'synthetic.jsonl'
    command = [sys.executable, '-m', 'stt_monitor.receiver', '--port', '32110',
               '--live', '--max-packets', '5', '--idle-timeout', '5',
               '--duration', '10', '--output', str(output)]
    receiver = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True)
    try:
        assert receiver.stdout.readline().startswith('Listening'), 'receiver not ready'
        assert receiver.stdout.readline().startswith('Vista de recepcion:'), 'live not ready'
        subprocess.run([sys.executable, '-c', SENDER], check=True, timeout=10)
        stdout, stderr = receiver.communicate(timeout=15)
        assert receiver.returncode == 0, stderr
        lines = stdout.splitlines()
        assert len([x for x in lines if x.startswith('Recibido ')]) == 5, stdout
        assert json.loads(lines[-1]) == {'accepted': 5, 'rejected': 2}, stdout
        assert 'sesion=synthetic-restart muestra=0' in lines[-2], stdout
        assert 'intentos previos: env=0 err=0' in lines[-2], stdout
        assert 'ultimo error conservado=0x804101CD' in lines[-2], stdout
        records = [json.loads(x) for x in output.read_text(encoding='utf-8').splitlines()]
        assert [r['packet']['seq'] for r in records] == [0, 2, 2, 1, 0]
        # Change only in-memory copies to inject PC clock behavior deterministically.
        stamps = ['2026-10-21T06:00:00Z', '2026-10-21T06:00:20Z',
                  '2026-10-21T06:00:19Z', None, '2026-10-21T06:00:40Z']
        for record, stamp in zip(records, stamps):
            record['received_at'] = stamp
        report = summarize([json.dumps(r) for r in records] + ['{"packet":', 'invalid'])
        assert report['invalid_lines'] == 2
        first, restarted = report['sessions']
        assert first['duplicates'] == 1 and first['out_of_order'] == 1
        assert first['missing_between_observed'] == 0
        timing = first['reception_timing']
        assert timing['clock_regressions'] == 1 and timing['unusable_timestamps'] == 1
        assert timing['largest_gap'] == dict(seconds=20.0, from_seq=0, to_seq=2,
                                             process_uptime_delta_ms=2000)
        assert first['diagnostics_latest']['send_errors'] == 1
        assert restarted['first_seq'] == restarted['last_seq'] == 0
        assert restarted['diagnostics_latest']['send_errors'] == 0
        assert restarted['reception_timing']['largest_gap'] is None
        print('PASS: synthetic STT/2, live + analysis, restart, duplicate, reordering, '
              'invalid/truncated input, forward/backward PC clock, clean receiver exit')
    finally:
        if receiver.poll() is None:
            receiver.kill()
            receiver.communicate()

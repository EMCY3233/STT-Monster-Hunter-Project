"""Run from repository root: python tests/smoke_cli.py (loopback only)."""
import json
import pathlib
import subprocess
import sys
import tempfile

with tempfile.TemporaryDirectory() as folder:
    output = pathlib.Path(folder) / 'smoke.jsonl'
    command = [sys.executable, '-m', 'stt_monitor.receiver', '--port', '32109',
               '--max-packets', '10', '--idle-timeout', '10', '--output', str(output)]
    receiver = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert receiver.stdout.readline().startswith('Listening'), 'receiver not ready'
        subprocess.run([sys.executable, '-m', 'stt_monitor.simulator', '--port', '32109',
                        '--count', '10', '--interval', '0.02'], check=True, timeout=10)
        stdout, stderr = receiver.communicate(timeout=15)
        assert receiver.returncode == 0, stderr
        assert json.loads(stdout) == {'accepted': 10, 'rejected': 0}, stdout
        records = [json.loads(line) for line in output.read_text().splitlines()]
        assert [r['packet']['seq'] for r in records] == list(range(10))
        assert all(r['packet']['source'] == 'simulator' for r in records)
        print('PASS: two CLI processes, 10 simulated samples, sequences 0..9')
    finally:
        if receiver.poll() is None:
            receiver.kill()
            receiver.communicate()

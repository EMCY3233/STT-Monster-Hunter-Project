"""Exercise actual file byte quota and partial CLI reports; loopback only."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / 'quota.jsonl'
    prefix = b'original-prefix\r\n'
    path.write_bytes(prefix)
    command = [sys.executable, '-m', 'stt_monitor.receiver', '--port', '32112',
               '--max-bytes', '900', '--duration', '5', '--idle-timeout', '5',
               '--output', str(path)]
    receiver = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        assert receiver.stdout.readline().startswith('Listening')
        subprocess.run([sys.executable, '-m', 'stt_monitor.simulator', '--port', '32112',
                        '--count', '20', '--interval', '0.01'], check=True, timeout=10)
        stdout, stderr = receiver.communicate(timeout=10)
        assert receiver.returncode == 0, stderr
        status = json.loads(stdout)
        assert status['stop_reason'] == 'max_bytes', status
        raw = path.read_bytes()
        assert raw.startswith(prefix) and len(raw) <= 900
        assert len(raw) == len(prefix) + status['bytes_written']
        rows = raw[len(prefix):].splitlines()
        assert len(rows) == status['accepted'] and len(rows) > 1
        assert status['not_recorded'] in (0, 1) and status['rejected'] == 0
        assert [json.loads(x)['packet']['seq'] for x in rows] == list(range(len(rows)))
        # Existing data is already over this new cap: append nothing.
        command[command.index('900')] = '1'
        second = subprocess.run(command, capture_output=True, text=True, timeout=5)
        assert second.returncode == 0, second.stderr
        assert json.loads(second.stdout.splitlines()[-1])['accepted'] == 0
        assert path.read_bytes() == raw
        analyzed = subprocess.run([sys.executable, '-m', 'stt_monitor.analyze', str(path),
                                   '--max-unique', '1'], capture_output=True, text=True,
                                  check=True, timeout=5)
        report = json.loads(analyzed.stdout)
        assert report['partial'] and report['stop_reason'] == 'max_unique'
        assert report['invalid_lines'] == 1  # Preserved original prefix, not a record.
        assert report['processed_packets'] == 1
        print('PASS: continuous synthetic traffic, actual UTF-8/LF file quota, '
              'existing CRLF prefix preserved, over-cap no append, partial CLI report')
    finally:
        if receiver.poll() is None:
            receiver.kill()
            receiver.communicate()

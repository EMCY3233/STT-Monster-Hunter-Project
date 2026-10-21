"""Bounded, read-only log/RPC observer. Raw commercial data stays local."""
import argparse
import hashlib
import json
from pathlib import Path
import secrets
import socket
import struct
import time


def read_memory(address, size, port=45987, timeout=0.25):
    """Citra bundled scripting protocol v1; only request type 1 (ReadMemory)."""
    if not (0 <= address <= 0xFFFFFFFF and 1 <= size <= 32
            and address + size <= 0x100000000 and 1 <= port <= 65535):
        raise ValueError('invalid bounded memory range or port')
    ident = secrets.randbits(32)
    packet = struct.pack('<6I', 1, ident, 1, 8, address, size)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.connect(('127.0.0.1', port))
        sock.send(packet)
        reply = sock.recv(49)
    if len(reply) != 16 + size:
        raise ValueError('unexpected RPC reply length')
    if struct.unpack('<4I', reply[:16]) != (1, ident, 1, size):
        raise ValueError('unexpected RPC reply header')
    return reply[16:]


class LogTail:
    """Bound reads, handle truncation, and preserve incomplete UTF-8 lines."""
    def __init__(self, path):
        self.path = Path(path)
        self.offset = 0
        self.pending = b''

    def poll(self):
        try:
            with self.path.open('rb') as stream:
                truncated = stream.seek(0, 2) < self.offset
                if truncated:
                    self.offset = 0
                    self.pending = b''
                stream.seek(self.offset)
                data = stream.read(65536)
                self.offset = stream.tell()
        except FileNotFoundError:
            return []
        parts = (self.pending + data).split(b'\n')
        self.pending = parts.pop()
        # A malformed log without newlines must not grow memory indefinitely.
        if len(self.pending) > 65536:
            parts.append(self.pending[:65536])
            self.pending = self.pending[65536:]
        return [part.decode('utf-8', 'replace').rstrip('\r') for part in parts]


def observe(log, out, seconds=10, interval=0.5, address=None, size=4, port=45987):
    if not 0 < seconds <= 60 or not 0.1 <= interval <= 5:
        raise ValueError('duration must be <=60 seconds; interval 0.1..5')
    if address is not None and not (0 <= address <= 0xFFFFFFFF and
                                   1 <= size <= 32 and address + size <= 2**32):
        raise ValueError('invalid bounded range')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    tail = LogTail(log)
    started = time.monotonic()
    started_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    samples = successes = failures = lines = 0
    previous = None
    with (out / 'events.jsonl').open('x', encoding='utf-8') as events:
        while True:
            elapsed = time.monotonic() - started
            if elapsed >= seconds:
                break
            for line in tail.poll():
                events.write(json.dumps(dict(kind='log', observed_seconds=elapsed,
                    text=line, timing='observer arrival; existing lines may predate session')) + '\n')
                lines += 1
            if address is not None:
                samples += 1
                try:
                    data = read_memory(address, size, port, min(0.25, seconds-elapsed))
                    digest = hashlib.sha256(data).hexdigest()
                    event = dict(kind='memory', observed_seconds=elapsed,
                                 sha256=digest, changed=None if previous is None else digest != previous)
                    previous = digest
                    successes += 1
                except (OSError, ValueError) as exc:
                    event = dict(kind='memory_error', observed_seconds=elapsed,
                                 error_type=type(exc).__name__)
                    failures += 1
                events.write(json.dumps(event) + '\n')
            events.flush()
            time.sleep(min(interval, max(0, seconds-(time.monotonic()-started))))
    receipt = dict(schema=1, started_utc=started_utc, elapsed_seconds=time.monotonic()-started,
                   log_lines=lines, memory_attempts=samples, memory_successes=successes,
                   memory_failures=failures, address=address, size=size if address is not None else None,
                   loopback_port=port if address is not None else None,
                   writes_to_emulated_memory=False, game_actions_observed=False,
                   log_timestamps_are_observer_arrival=True,
                   incomplete_log_bytes=len(tail.pending),
                   events_sha256=hashlib.sha256((out/'events.jsonl').read_bytes()).hexdigest())
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=10)
    parser.add_argument('--interval', type=float, default=0.5)
    parser.add_argument('--address', type=lambda text: int(text, 0))
    parser.add_argument('--size', type=int, default=4)
    parser.add_argument('--port', type=int, default=45987)
    args = parser.parse_args()
    print(json.dumps(observe(args.log, args.out, args.seconds, args.interval,
                             args.address, args.size, args.port)))

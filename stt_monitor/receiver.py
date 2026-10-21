"""Receive telemetry only; never sends commands to a console."""
import argparse
import json
import socket
import time
from datetime import datetime, timezone
from .protocol import MAX_BYTES, decode


def receive(sock, output, *, idle_timeout=5.0, max_packets=0):
    """Stop after inactivity or max valid packets; bounded memory, append-only output."""
    accepted = rejected = 0
    deadline = time.monotonic() + idle_timeout
    while not max_packets or accepted < max_packets:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        sock.settimeout(remaining)
        try:
            raw, peer = sock.recvfrom(MAX_BYTES + 1)
        except socket.timeout:
            break
        except OSError as exc:
            # Windows reports oversized UDP datagrams as WSAEMSGSIZE.
            if getattr(exc, 'winerror', None) == 10040:
                rejected += 1
                continue
            raise
        try:
            packet = decode(raw)
        except ValueError:
            rejected += 1
            continue
        record = {'received_at': datetime.now(timezone.utc).isoformat(),
                  'peer_ip': peer[0], 'packet': packet}
        output.write(json.dumps(record, allow_nan=False) + '\n')
        output.flush()
        accepted += 1
        deadline = time.monotonic() + idle_timeout
    return {'accepted': accepted, 'rejected': rejected}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=32100)
    parser.add_argument('--output', default='telemetry.jsonl')
    parser.add_argument('--idle-timeout', type=float, default=5)
    parser.add_argument('--max-packets', type=int, default=0)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 0 < args.idle_timeout <= 3600 or args.max_packets < 0:
        parser.error('invalid port, timeout or packet limit')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((args.bind, args.port))
            print(f'Listening on {args.bind}:{args.port}', flush=True)
            with open(args.output, 'a', encoding='utf-8') as output:
                print(json.dumps(receive(sock, output, idle_timeout=args.idle_timeout,
                                         max_packets=args.max_packets)))
    except KeyboardInterrupt:
        print('Stopped')


if __name__ == '__main__':
    main()

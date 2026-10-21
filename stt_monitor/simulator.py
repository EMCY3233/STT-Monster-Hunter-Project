"""Send finite, explicitly simulated telemetry to a PC receiver."""
import argparse
import socket
import time
import uuid
from .protocol import encode


def packet(session, seq, uptime_ms):
    return dict(version=1, session=session, source='simulator', seq=seq,
                uptime_ms=uptime_ms, battery_pct=75)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=32100)
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--interval', type=float, default=1)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 1 <= args.count <= 100000 or not 0.01 <= args.interval <= 60:
        parser.error('invalid port, count or interval')
    session = uuid.uuid4().hex
    start = time.monotonic()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for seq in range(args.count):
            sock.sendto(encode(packet(session, seq, int((time.monotonic()-start)*1000))), (args.host, args.port))
            if seq + 1 < args.count:
                time.sleep(args.interval)
    print(f'Sent {args.count} simulated packets; session={session}')


if __name__ == '__main__':
    main()

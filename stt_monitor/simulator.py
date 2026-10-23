"""Send finite, explicitly simulated telemetry to a PC receiver."""
import argparse
import socket
import time
import uuid
from .protocol import encode

# Arbitrary, clearly synthetic code for skipped attempts; not a real console error.
SIMULATED_ERROR = -0x7FFF0001


def packet(session, seq, uptime_ms, *, version=1, diagnostics=None):
    result = dict(version=version, session=session, source='simulator', seq=seq,
                  uptime_ms=uptime_ms, battery_pct=75)
    if version == 2:
        result['diagnostics'] = dict(diagnostics)
    return result


def attempts(count, fail_every=0):
    """Yield (seq, send, diagnostics) like the Vita agent: counters describe prior attempts.

    With fail_every=N, every Nth attempt is a simulated failure and is not sent.
    """
    ok = errors = last_result = net_errno = 0
    for seq in range(count):
        diagnostics = dict(send_ok=ok, send_errors=errors,
                           last_result=last_result, net_errno=net_errno)
        failed = fail_every > 0 and (seq + 1) % fail_every == 0
        yield seq, not failed, diagnostics
        if failed:
            errors += 1
            last_result = SIMULATED_ERROR
            net_errno = 1
        else:
            ok += 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=32100)
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--interval', type=float, default=1)
    parser.add_argument('--version', type=int, choices=(1, 2), default=1,
                        help='protocol version to emit (2 adds simulated diagnostics)')
    parser.add_argument('--fail-every', type=int, default=0,
                        help='STT/2 only: every Nth attempt is a simulated failure and is not sent')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 1 <= args.count <= 100000 or not 0.01 <= args.interval <= 60:
        parser.error('invalid port, count or interval')
    if args.fail_every < 0 or (args.fail_every and args.version != 2):
        parser.error('--fail-every requires --version 2 and a non-negative value')
    session = uuid.uuid4().hex
    start = time.monotonic()
    sent = 0
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        for seq, send, diagnostics in attempts(args.count, args.fail_every):
            if send:
                raw = encode(packet(session, seq, int((time.monotonic() - start) * 1000),
                                    version=args.version, diagnostics=diagnostics))
                sock.sendto(raw, (args.host, args.port))
                sent += 1
            if seq + 1 < args.count:
                time.sleep(args.interval)
    print(f'Sent {sent} simulated packets of {args.count} attempts; '
          f'version={args.version}; session={session}')


if __name__ == '__main__':
    main()

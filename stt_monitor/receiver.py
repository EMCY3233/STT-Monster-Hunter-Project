"""Receive telemetry only; never sends commands to a console."""
import argparse
import json
import socket
import sys
import time
from datetime import datetime, timezone
from .protocol import MAX_BYTES, decode


def live_line(record):
    """Describe one received sample, never infer delivery or console stop state."""
    p = record['packet']
    battery = '?' if p['battery_pct'] is None else str(p['battery_pct'])
    text = (f"Recibido {record['received_at']} | {record['peer_ip']} | "
            f"{p['source']} sesion={p['session']} muestra={p['seq']} | bateria={battery}%")
    if p['version'] == 2:
        d = p['diagnostics']
        text += (f" | intentos previos: env={d['send_ok']} err={d['send_errors']}"
                 f" | ultimo error conservado=0x{d['last_result'] & 0xffffffff:08X}"
                 f" detalle=0x{d['net_errno'] & 0xffffffff:08X}")
    else:
        text += ' | STT/1: sin diagnostico de red'
    return text


def receive(sock, output, *, idle_timeout=5.0, max_packets=0, live_output=None):
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
        if live_output is not None:
            live_output.write(live_line(record) + '\n')
            live_output.flush()
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
    parser.add_argument('--live', action='store_true',
                        help='show each received sample and prior-attempt diagnostics')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 0 < args.idle_timeout <= 3600 or args.max_packets < 0:
        parser.error('invalid port, timeout or packet limit')
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((args.bind, args.port))
            print(f'Listening on {args.bind}:{args.port}', flush=True)
            if args.live:
                print('Vista de recepcion: contadores previos al envio actual; ultimo error puede ser historico. '
                      'Sin muestras no se puede confirmar parada ni desconexion.', flush=True)
            with open(args.output, 'a', encoding='utf-8') as output:
                print(json.dumps(receive(sock, output, idle_timeout=args.idle_timeout,
                                         max_packets=args.max_packets,
                                         live_output=sys.stdout if args.live else None)))
    except KeyboardInterrupt:
        print('Stopped')


if __name__ == '__main__':
    main()

"""Receive telemetry only; never sends commands to a console."""
import argparse
import json
import os
import socket
import sys
import time
from datetime import datetime, timezone
from .protocol import MAX_BYTES, decode

DEFAULT_MAX_CAPTURE_BYTES = 10 * 1024 * 1024


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
    elif p['version'] in (4,5,6):
        f=p['perf'];text += f" | FPS={f['frames']*1e6/f['window_us']:.1f} G{f['ground_mode']} render={f['render_us']}us"
    elif p['version'] == 3:
        text += ' | STT/3: juego'
    else:
        text += ' | STT/1: sin diagnostico de red'
    return text


def receive(sock, output, *, idle_timeout=5.0, max_packets=0, live_output=None, duration=None,
            max_bytes=DEFAULT_MAX_CAPTURE_BYTES, initial_bytes=0):
    """Stop at inactivity, packet count or total duration; append-only output."""
    if type(max_bytes) is not int or max_bytes < 1 or initial_bytes < 0:
        raise ValueError('invalid capture byte limit or initial size')
    accepted = rejected = written = 0
    if initial_bytes >= max_bytes:
        return {'accepted': 0, 'rejected': 0, 'stop_reason': 'max_bytes',
                'bytes_written': 0, 'not_recorded': 0}
    started = time.monotonic()
    deadline = started + idle_timeout
    capture_deadline = None if duration is None else started + duration
    while not max_packets or accepted < max_packets:
        limit = deadline if capture_deadline is None else min(deadline, capture_deadline)
        remaining = limit - time.monotonic()
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
        if capture_deadline is not None and time.monotonic() >= capture_deadline:
            break
        try:
            packet = decode(raw)
        except ValueError:
            rejected += 1
            continue
        record = {'received_at': datetime.now(timezone.utc).isoformat(),
                  'peer_ip': peer[0], 'packet': packet}
        line = json.dumps(record, allow_nan=False) + '\n'
        size = len(line.encode('utf-8'))
        if initial_bytes + written + size > max_bytes:
            return {'accepted': accepted, 'rejected': rejected, 'stop_reason': 'max_bytes',
                    'bytes_written': written, 'not_recorded': 1}
        output.write(line)
        output.flush()
        written += size
        if live_output is not None:
            live_output.write(live_line(record) + '\n')
            live_output.flush()
        accepted += 1
        if initial_bytes + written >= max_bytes:
            return {'accepted': accepted, 'rejected': rejected, 'stop_reason': 'max_bytes',
                    'bytes_written': written, 'not_recorded': 0}
        deadline = time.monotonic() + idle_timeout
    return {'accepted': accepted, 'rejected': rejected}


def check_append_boundary(path):
    """Do not join a new record to an unfinished existing physical line."""
    try:
        with open(path, 'rb') as source:
            source.seek(0, os.SEEK_END)
            if source.tell():
                source.seek(-1, os.SEEK_END)
                if source.read(1) != b'\n':
                    raise ValueError('capture ends without newline; choose a new --output; existing file unchanged')
    except FileNotFoundError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=32100)
    parser.add_argument('--output', default='telemetry.jsonl')
    parser.add_argument('--idle-timeout', type=float, default=5)
    parser.add_argument('--max-packets', type=int, default=0)
    parser.add_argument('--max-bytes', type=int, default=DEFAULT_MAX_CAPTURE_BYTES,
                        help='maximum total output file bytes including existing data (default 10 MiB)')
    parser.add_argument('--duration', type=float, default=None,
                        help='maximum capture seconds (0 < duration <= 3600), independent of traffic')
    parser.add_argument('--live', action='store_true',
                        help='show each received sample and prior-attempt diagnostics')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or not 0 < args.idle_timeout <= 3600 or args.max_packets < 0:
        parser.error('invalid port, timeout or packet limit')
    if args.max_bytes < 1:
        parser.error('capture byte limit must be positive')
    if args.duration is not None and not 0 < args.duration <= 3600:
        parser.error('invalid capture duration')
    try:
        check_append_boundary(args.output)
    except ValueError as exc:
        parser.error(str(exc))
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((args.bind, args.port))
            print(f'Listening on {args.bind}:{args.port}', flush=True)
            if args.live:
                print('Vista de recepcion: contadores previos al envio actual; ultimo error puede ser historico. '
                      'Sin muestras no se puede confirmar parada ni desconexion.', flush=True)
            with open(args.output, 'a', encoding='utf-8', newline='\n') as output:
                print(json.dumps(receive(sock, output, idle_timeout=args.idle_timeout,
                                         max_packets=args.max_packets, duration=args.duration,
                                         max_bytes=args.max_bytes, initial_bytes=os.fstat(output.fileno()).st_size,
                                         live_output=sys.stdout if args.live else None)))
    except KeyboardInterrupt:
        print('Stopped')


if __name__ == '__main__':
    main()

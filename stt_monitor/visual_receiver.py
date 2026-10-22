"""Receive prototype-owned images/scene only; no commands or console access."""
import argparse
import html
import json
from pathlib import Path
import socket
import time
from datetime import datetime, timezone
from .visual_protocol import Assembler, MAX_DATAGRAM, png_rgb565


def receive(sock, folder, *, duration=180, idle_timeout=10, max_frames=90, max_bytes=16*1024*1024):
    assembler = Assembler()
    start = last_complete = time.monotonic()
    frames = rejected = written = fragments = not_saved = 0
    reason = 'duration'
    while frames < max_frames:
        now = time.monotonic()
        remaining = min(start+duration, last_complete+idle_timeout)-now
        if remaining <= 0:
            reason = 'duration' if now >= start+duration else 'idle'
            break
        sock.settimeout(remaining)
        try:
            raw, peer = sock.recvfrom(MAX_DATAGRAM+1)
        except socket.timeout:
            continue
        except OSError as exc:
            if getattr(exc, 'winerror', None) == 10040:
                rejected += 1
                continue
            raise
        fragments += 1
        now = time.monotonic()
        if now >= start+duration:
            reason = 'duration'
            break
        try:
            item = assembler.feed(raw, peer[0], now)
        except (ValueError, TypeError, KeyError, RecursionError):
            rejected += 1
            continue
        if item is None:
            continue
        stream, frame, metadata, pixels = item
        png = png_rgb565(pixels)
        # Local names use reception index, never identifiers supplied over UDP.
        name = f'frame-{frames:04d}'
        record = dict(received_at=datetime.now(timezone.utc).isoformat(), peer_ip=peer[0],
                      stream_id=stream, metadata=metadata, image=name+'.png')
        scene = (json.dumps(record, indent=2, ensure_ascii=True)+'\n').encode('utf-8')
        if written+len(png)+len(scene) > max_bytes:
            reason = 'max_bytes'
            not_saved = 1
            break
        (folder/(name+'.png')).write_bytes(png)
        (folder/(name+'.json')).write_bytes(scene)
        written += len(png)+len(scene)
        frames += 1
        last_complete = now
        preview = ('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="2">'
                   '<title>STT visual capture</title><h1>Imagen recibida del prototipo</h1>'
                   '<p>Captura reducida RGB565; UDP sin autenticacion. No es video en directo garantizado.</p>'
                   f'<img width="720" src="{name}.png"><pre>{html.escape(scene.decode())}</pre>')
        (folder/'index.html').write_text(preview, encoding='utf-8')
        print(f'Recibido {name}: tick={metadata["scene"]["play"]["tick"]} source={metadata["scene"]["source"]}', flush=True)
    else:
        reason = 'max_frames'
    assembler.expire(time.monotonic())
    summary = dict(frames=frames, rejected_datagrams=rejected, fragments=fragments,
                   bytes_written=written, stop_reason=reason, complete_not_saved=not_saved,
                   incomplete=len(assembler.pending), **assembler.stats)
    (folder/'summary.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bind', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=32101)
    parser.add_argument('--output', required=True, help='new directory, never reused')
    parser.add_argument('--duration', type=float, default=180)
    parser.add_argument('--idle-timeout', type=float, default=10)
    parser.add_argument('--max-frames', type=int, default=90)
    parser.add_argument('--max-bytes', type=int, default=16*1024*1024)
    args = parser.parse_args()
    if (not 1 <= args.port <= 65535 or not 0 < args.duration <= 3600 or
            not 0 < args.idle_timeout <= 3600 or not 1 <= args.max_frames <= 1000 or args.max_bytes < 1):
        parser.error('invalid visual capture limits')
    folder = Path(args.output)
    if folder.exists():
        parser.error('output directory already exists; choose a new directory')
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 256*1024)
        sock.bind((args.bind, args.port))
        folder.mkdir(parents=True, exist_ok=False)
        print(f'Listening visual on {args.bind}:{args.port}', flush=True)
        try:
            print(json.dumps(receive(sock, folder, duration=args.duration, idle_timeout=args.idle_timeout,
                                     max_frames=args.max_frames, max_bytes=args.max_bytes)))
        except KeyboardInterrupt:
            (folder/'interrupted.txt').write_text('Capture interrupted by user. Existing images preserved.\n')
            print('Stopped; images preserved')


if __name__ == '__main__':
    main()

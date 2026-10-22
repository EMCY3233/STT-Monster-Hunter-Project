"""Summarize telemetry without assuming UDP delivery or device identity."""
import argparse
import json
from datetime import datetime, timezone
from .protocol import validate

MAX_LINE_BYTES = 4096
DEFAULT_MAX_SESSIONS = 1000
DEFAULT_MAX_UNIQUE = 100000


def reception_time(value):
    """Only timezone-aware receiver timestamps support interval comparisons."""
    if not isinstance(value, str):
        return None
    try:
        instant = datetime.fromisoformat(value)
        if instant.utcoffset() is None:
            return None
        return instant.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def bounded_lines(source):
    """Drain an oversized physical line in bounded chunks, report it once."""
    while True:
        chunk = source.readline(MAX_LINE_BYTES + 1)
        if not chunk:
            return
        if len(chunk) > MAX_LINE_BYTES:
            while not chunk.endswith(b'\n'):
                chunk = source.readline(MAX_LINE_BYTES + 1)
                if not chunk:
                    break
            yield None
        else:
            try:
                yield chunk.decode('utf-8')
            except UnicodeError:
                yield None


def summarize(lines, *, max_sessions=DEFAULT_MAX_SESSIONS, max_unique=DEFAULT_MAX_UNIQUE):
    if type(max_sessions) is not int or max_sessions < 1 or type(max_unique) is not int or max_unique < 1:
        raise ValueError('analysis limits must be positive integers')
    sessions = {}
    invalid = total_unique = processed = 0
    stop_reason = None
    for line in lines:
        try:
            if not isinstance(line, str) or len(line) > MAX_LINE_BYTES or len(line.encode('utf-8')) > MAX_LINE_BYTES:
                raise ValueError('oversized or invalid line')
            record = json.loads(line)
            packet = validate(record['packet'])
            peer = record['peer_ip']
            if not isinstance(peer, str):
                raise ValueError('invalid peer')
        except (ValueError, KeyError, TypeError, RecursionError, UnicodeError):
            invalid += 1
            continue
        key = (peer, packet['source'], packet['session'])
        seq = packet['seq']
        state = sessions.get(key)
        if state is None and len(sessions) >= max_sessions:
            stop_reason = 'max_sessions'
            break
        if (state is None or seq not in state['seen']) and total_unique >= max_unique:
            stop_reason = 'max_unique'
            break
        if state is None:
            state = sessions[key] = {'packets': 0, 'duplicates': 0,
                                     'out_of_order': 0, 'seen': set(), 'highest': -1}
        if seq not in state['seen']:
            total_unique += 1
        processed += 1
        timing = state.setdefault('reception_timing', {
            'timestamped_packets': 0, 'unusable_timestamps': 0,
            'clock_regressions': 0, 'first_received_at': None,
            'last_received_at': None, 'largest_gap': None})
        instant = reception_time(record.get('received_at'))
        previous = state.pop('_previous_reception', None)
        if instant is None:
            timing['unusable_timestamps'] += 1
        else:
            timing['timestamped_packets'] += 1
            if timing['first_received_at'] is None:
                timing['first_received_at'] = instant.isoformat()
            timing['last_received_at'] = instant.isoformat()
            if previous is not None:
                delta = (instant - previous[0]).total_seconds()
                if delta < 0:
                    timing['clock_regressions'] += 1
                elif timing['largest_gap'] is None or delta > timing['largest_gap']['seconds']:
                    timing['largest_gap'] = {
                        'seconds': delta, 'from_seq': previous[1], 'to_seq': seq,
                        'process_uptime_delta_ms': packet['uptime_ms'] - previous[2]}
            state['_previous_reception'] = (instant, seq, packet['uptime_ms'])
        if packet['version'] == 2 and seq >= state['highest']:
            state['diagnostics_latest'] = packet['diagnostics'].copy()
        state['packets'] += 1
        if seq in state['seen']:
            state['duplicates'] += 1
        elif seq < state['highest']:
            state['out_of_order'] += 1
        state['seen'].add(seq)
        state['highest'] = max(state['highest'], seq)
    result = []
    for (peer, source, session), state in sorted(sessions.items()):
        state.pop('_previous_reception', None)
        seen = state.pop('seen')
        highest = state.pop('highest')
        result.append(dict(peer_ip=peer, source=source, session=session,
                           first_seq=min(seen), last_seq=highest,
                           unique_packets=len(seen),
                           missing_between_observed=highest-min(seen)+1-len(seen), **state))
    return {'sessions': result, 'invalid_lines': invalid,
            'partial': stop_reason is not None, 'stop_reason': stop_reason,
            'processed_packets': processed,
            'limits': {'max_sessions': max_sessions, 'max_unique': max_unique,
                       'max_line_bytes': MAX_LINE_BYTES}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='JSONL recorded by the receiver')
    parser.add_argument('--max-sessions', type=int, default=DEFAULT_MAX_SESSIONS)
    parser.add_argument('--max-unique', type=int, default=DEFAULT_MAX_UNIQUE)
    args = parser.parse_args()
    if args.max_sessions < 1 or args.max_unique < 1:
        parser.error('analysis limits must be positive integers')
    with open(args.path, 'rb') as source:
        print(json.dumps(summarize(bounded_lines(source), max_sessions=args.max_sessions,
                                   max_unique=args.max_unique), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

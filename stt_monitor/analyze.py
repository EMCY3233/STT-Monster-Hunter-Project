"""Summarize telemetry without assuming UDP delivery or device identity."""
import argparse
import json
from datetime import datetime, timezone
from .protocol import validate


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


def summarize(lines):
    sessions = {}
    invalid = 0
    for line in lines:
        try:
            record = json.loads(line)
            packet = validate(record['packet'])
            peer = record['peer_ip']
            if not isinstance(peer, str):
                raise ValueError('invalid peer')
        except (ValueError, KeyError, TypeError, RecursionError):
            invalid += 1
            continue
        key = (peer, packet['source'], packet['session'])
        state = sessions.setdefault(key, {'packets': 0, 'duplicates': 0,
                                         'out_of_order': 0, 'seen': set(), 'highest': -1})
        seq = packet['seq']
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
    return {'sessions': result, 'invalid_lines': invalid}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', help='JSONL recorded by the receiver')
    args = parser.parse_args()
    with open(args.path, encoding='utf-8') as source:
        print(json.dumps(summarize(source), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

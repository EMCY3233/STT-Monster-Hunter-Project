"""Summarize telemetry without assuming UDP delivery or device identity."""
import argparse
import json
from .protocol import validate


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
        state['packets'] += 1
        if seq in state['seen']:
            state['duplicates'] += 1
        elif seq < state['highest']:
            state['out_of_order'] += 1
        state['seen'].add(seq)
        state['highest'] = max(state['highest'], seq)
    result = []
    for (peer, source, session), state in sorted(sessions.items()):
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

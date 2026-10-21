"""Synthetic, offline compatibility probe. Loads explicit project Python sources.

No sockets, game resources, installation or source modifications. Candidate
composition is hypothetical until its owning PRs are reviewed and integrated.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types

# Do not create bytecode caches in the other fronts' source directories.
sys.dont_write_bytecode = True


def load_package(name, directory):
    package = types.ModuleType(name)
    package.__path__ = [str(directory.resolve())]
    sys.modules[name] = package
    return load_module(name + '.protocol', directory / 'protocol.py')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check(baseline, candidate, snapshot, hit):
    old = load_package('stt_probe_baseline', baseline)
    new = load_package('stt_probe_candidate', candidate)
    old_analyzer = load_module('stt_probe_baseline.analyze', baseline / 'analyze.py')
    new_analyzer = load_module('stt_probe_candidate.analyze', baseline / 'analyze.py')
    results = []
    def accepted(label, module, packet, expected):
        try:
            raw = module.encode(packet)
            assert module.decode(raw) == packet
            observed = True
            detail = {'encoded_bytes': len(raw)}
        except ValueError as exc:
            observed = False
            detail = {'rejection': str(exc)}
        results.append({'case': label, 'expected_accept': expected, 'accepted': observed,
                        'passed': observed == expected, **detail})
    v1 = dict(version=1, session='synthetic', source='simulator', seq=0, uptime_ms=0, battery_pct=50.5)
    v2 = dict(v1, version=2, diagnostics=dict(send_ok=0, send_errors=0, last_result=0, net_errno=0))
    for version, packet in [(1, v1), (2, v2), (3, snapshot), (3, hit)]:
        suffix = 'hit' if packet is hit else 'snapshot'
        accepted(f'baseline_v{version}_{suffix}', old, packet, version != 3)
        accepted(f'candidate_v{version}_{suffix}', new, packet, True)
    maximum = copy.deepcopy(hit)
    maximum.update(session='s' * 64, seq=2**53-1, uptime_ms=2**53-1, battery_pct=100)
    p = maximum['play']
    p['tick'] = 2**53-1
    p['hunter'].update(pos_mm=[100000000, -100000000, 100000000], yaw_mdeg=-180000, hp=1000000)
    p['camera'].update(yaw_mdeg=-180000, pitch_mdeg=-89000, distance_mm=1000000)
    p['attack'].update(id=2**32-1, phase_tick=65535)
    p['hits'] = [dict(attack=2**32-1, target=t, damage=1000000, hp=1000000) for t in (2**32-1, 2**32-2)]
    p['perf'].update(frame_us=10000000, update_us=10000000, dropped=2**32-1)
    accepted('candidate_maximum_field_lengths', new, maximum, True)
    for label, module in [('baseline', old), ('candidate', new)]:
        for kind, raw in [('duplicate_key', b'{"version":1,"version":3}'), ('oversize', b' ' * 1025)]:
            try:
                module.decode(raw)
                rejected = False
            except ValueError:
                rejected = True
            results.append({'case': label + '_' + kind, 'passed': rejected})
    packets = [snapshot, dict(hit, seq=1)]
    lines = [json.dumps({'peer_ip': '127.0.0.1', 'packet': p}) for p in packets]
    before = old_analyzer.summarize(lines)
    after = new_analyzer.summarize(lines)
    results.append({'case': 'baseline_analyzer_rejects_v3', 'passed': before['invalid_lines'] == 2 and before['sessions'] == []})
    results.append({'case': 'prospective_analyzer_counts_v3', 'passed': after['invalid_lines'] == 0 and len(after['sessions']) == 1 and after['sessions'][0]['packets'] == 2})
    files = [baseline/'protocol.py', baseline/'analyze.py', candidate/'protocol.py', candidate/'play_protocol.py']
    return {'scope': 'Offline synthetic project-code composition only; no UDP, hardware, installation, gameplay or merged compatibility claim.',
            'cases': results, 'passed': sum(r['passed'] for r in results), 'failed': sum(not r['passed'] for r in results),
            'baseline_analyzer': before, 'prospective_analyzer': after,
            'source_hashes': [{'path': str(p), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--hit', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.baseline, args.candidate, json.loads(args.snapshot.read_text()), json.loads(args.hit.read_text()))
    with args.report.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result))
    if result['failed']:
        raise SystemExit(1)

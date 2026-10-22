"""Audit private input receipts; acceptance does not establish game movement."""
import argparse,json,math
from pathlib import Path

def audit(r):
    keys=r.get('keys') or [r.get('key')]
    if not keys or any(not isinstance(k,str) for k in keys) or len(set(keys))!=len(keys):
        raise ValueError('invalid key list')
    held=set();attempted=set();issues=[];last=-math.inf
    events=r.get('events',[])
    for e in events:
        key=e.get('key',keys[0] if len(keys)==1 else None)
        stamp=e.get('monotonic')
        if key not in keys or not isinstance(stamp,(int,float)) or not math.isfinite(stamp) or stamp<last:
            raise ValueError('invalid event identity or order')
        last=stamp
        if e.get('event') not in ('down','up'):raise ValueError('invalid event kind')
        if e.get('event')=='down':
            attempted.add(key)
            if key in held:issues.append('duplicate_down')
            if e.get('accepted')==1:held.add(key)
        elif e.get('accepted')==1:held.discard(key)
        if e.get('accepted')!=1:issues.append('rejected_event')
    if held:issues.append('release_not_confirmed')
    if r.get('status')=='completed' and r.get('executed') and attempted!=set(keys):
        issues.append('not_all_keys_attempted')
    if not r.get('executed') and events:issues.append('events_despite_not_executed')
    return dict(status=r.get('status'),executed=bool(r.get('executed')),
        keys=keys,event_count=len(events),accepted_event_count=sum(e.get('accepted')==1 for e in events),
        all_accepted_downs_released=not held,issues=sorted(set(issues)),
        game_effect_verified=False)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('receipt',type=Path);a=p.parse_args()
    print(json.dumps(audit(json.loads(a.receipt.read_text(encoding='utf-8')))))

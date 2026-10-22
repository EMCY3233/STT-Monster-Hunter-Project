"""Summarize real STT/4 capture windows separately per source/session/render mode."""
import argparse
import json
import re
from collections import defaultdict
from .protocol import validate

def analyze(records):
    groups=defaultdict(list);seen=set();duplicates=0
    for record in records:
        p=record['packet']
        if p.get('version') not in (4,5,6,7): continue
        validate(p)
        identity=(p['source'],p['session'],p['seq'])
        if identity in seen: duplicates+=1;continue
        seen.add(identity)
        groups[(p['source'],p['session'],p['perf']['ground_mode'],p['perf'].get('raster_mode',0),p['perf'].get('ceiling_mode'),p['perf'].get('target_fps'))].append(p)
    results=[]
    for (source,session,mode,raster,ceiling,target),packets in groups.items():
        trial=re.fullmatch(r'vita-0019-f(30|45)-[0-9a-f]+',session)
        roof_trial=re.fullmatch(r'vita-(0020|0021|0022|0023)-f(30|45)-c([012])-[0-9a-f]+',session)
        f=[p['perf'] for p in packets];frames=sum(p['frames'] for p in f)
        seconds=sum(p['window_us'] for p in f)/1e6
        avg=lambda k: sum(p[k]*p['frames'] for p in f)/frames
        results.append(dict(source=source,session=session,build=('00.'+roof_trial[1][2:]) if roof_trial else '00.19' if trial else None,target_fps=target if target is not None else int(trial[1]) if trial else None,ground_mode=mode,raster_mode=raster,ceiling_mode=ceiling,samples=len(f),
            fps=frames/seconds,update_us=avg('update_us'),render_us=avg('render_us'),
            present_us=avg('present_us'),telemetry_us=avg('telemetry_us'),
            minimum_free_bytes={k:min((p[k] for p in f if p[k] is not None),default=None)
                for k in ('ram_free','cdram_free','phy_free','cdlg_free')},
            render_stages_us={k:sum(p.get(k,0)*p['frames'] for p in f)/frames if all(k in p for p in f) else None for k in ('clear_us','ground_us','ceiling_us','body_us','weapon_us','target_us','hud_us')},
            unavailable=['cpu_load_pct','gpu_load_pct','fg_app','vnz']))
    return dict(groups=results,duplicate_packets_ignored=duplicates,
                limitation='FPS and phase times are application measurements; MHz is not load. Compare equivalent actions/camera.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('capture');args=p.parse_args()
    with open(args.capture,encoding='utf-8') as f:
        print(json.dumps(analyze(json.loads(line) for line in f if line.strip()),indent=2))
if __name__=='__main__': main()

"""STT/4: in-process performance readings, unavailable counters are explicit null."""
from .play_protocol import obj, integer
import re

def validate_perf(p):
    obj(p, 'version session source seq uptime_ms battery_pct perf')
    integer(p['version'], 4, 6)
    if type(p['session']) is not str or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', p['session']):
        raise ValueError('invalid session')
    if p['source'] not in ('vita', 'simulator'):
        raise ValueError('invalid source')
    for k in ('seq', 'uptime_ms'): integer(p[k])
    if p['battery_pct'] is not None: integer(p['battery_pct'], 0, 100)
    f=p['perf']
    fields='tick frames window_us update_us render_us present_us telemetry_us equipment ground_mode cpu_mhz gpu_mhz xbar_mhz ram_free cdram_free phy_free cdlg_free cpu_load_pct gpu_load_pct fg_app vnz send_ok send_errors'
    if p['version']>=5: fields+=' raster_mode clear_us ground_us body_us weapon_us target_us hud_us'
    obj(f,fields)
    if p['version']>=5:
        integer(f['raster_mode'],0,1)
        for k in ('clear_us','ground_us','body_us','weapon_us','target_us','hud_us'): integer(f[k],0,4294967295)
    integer(f['tick'])
    integer(f['frames'], 1, 1000000)
    integer(f['window_us'], 1, 4294967295)
    for k in ('update_us','render_us','present_us','telemetry_us','send_ok','send_errors'):
        integer(f[k], 0, 4294967295)
    integer(f['equipment'], 0, 3);integer(f['ground_mode'], 0, 2 if p['version']==6 else 1)
    for k in ('cpu_mhz','gpu_mhz','xbar_mhz'):
        if f[k] is not None: integer(f[k], 0, 1000)
    for k in ('ram_free','cdram_free','phy_free','cdlg_free'):
        if f[k] is not None: integer(f[k], 0, 2147483647)
    for k in ('cpu_load_pct','gpu_load_pct','fg_app','vnz'):
        if f[k] is not None: raise ValueError('counter not supported by this producer')
    return p

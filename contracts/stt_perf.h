#ifndef STT_PERF_H
#define STT_PERF_H
#include <stddef.h>
#include <stdint.h>
typedef struct {
 const char *session;uint64_t seq,uptime_ms,tick;
 unsigned frames,window_us,update_us,render_us,present_us,telemetry_us;
 unsigned equipment,ground_mode,raster_mode,send_ok,send_errors;
 unsigned clear_us,ground_us,body_us,weapon_us,target_us,hud_us;
 int cpu_mhz,gpu_mhz,xbar_mhz,ram_free,cdram_free,phy_free,cdlg_free,battery_pct;
} SttPerfSample;
/* Negative reads become null. No fabricated utilization or privileged counters. */
int stt_perf_encode(char *out,size_t capacity,const SttPerfSample *sample);
#endif

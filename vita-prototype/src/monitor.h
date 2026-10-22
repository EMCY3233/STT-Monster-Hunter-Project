#ifndef STT_PROTOTYPE_MONITOR_H
#define STT_PROTOTYPE_MONITOR_H
#include <stdint.h>
#include "stt_perf.h"
#include "visual.h"
typedef struct {
 int socket,module,network,active,last_result;void *memory;char session[65];
 unsigned sent,errors,frames,last_ground;uint64_t started,window_start,next,seq;
 uint64_t update_sum,render_sum,present_sum,telemetry_sum;
 SttVisual *visual;uint64_t visual_next;unsigned visual_errors,visual_frame;
 unsigned char address[32];
} SttPrototypeMonitor;
void stt_monitor_init(SttPrototypeMonitor *m);
void stt_monitor_close(SttPrototypeMonitor *m);
void stt_monitor_toggle(SttPrototypeMonitor *m,uint64_t now);
void stt_monitor_frame(SttPrototypeMonitor *m,const char *session,uint64_t now,uint64_t tick,
 unsigned equipment,unsigned ground_mode,unsigned update_us,unsigned render_us,unsigned present_us,unsigned telemetry_us);
void stt_monitor_visual(SttPrototypeMonitor *m,uint64_t now,const uint32_t *pixels,size_t pitch,
 SttPlaySample *scene,unsigned equipment,unsigned ground,const SttTarget *target);
#endif

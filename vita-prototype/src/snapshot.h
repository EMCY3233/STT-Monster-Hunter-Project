#ifndef STT_SNAPSHOT_H
#define STT_SNAPSHOT_H
#include "stt_play.h"
#include "stt_combat.h"
#include "control.h"
void stt_vita_snapshot(SttPlaySample *sample,const SttCombat *combat,SttCamera camera,const char *session,uint64_t seq,uint64_t uptime_ms,unsigned frame_us,unsigned update_us,unsigned dropped);
#endif

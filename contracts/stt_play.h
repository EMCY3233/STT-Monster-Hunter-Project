#ifndef STT_PLAY_H
#define STT_PLAY_H
#include <stddef.h>
#include <stdint.h>
#define STT_PLAY_MAX_BYTES 1024
#define STT_PLAY_MAX_HITS 2
typedef struct { uint32_t attack, target, damage, hp; } SttPlayHit;
typedef struct {
 const char *session; int vita; uint64_t seq, uptime_ms, tick;
 int battery_pct; /* -1 = unavailable */
 unsigned state; /* idle move windup active recovery stunned */
 int32_t pos_mm[3], yaw_mdeg, camera_yaw_mdeg, camera_pitch_mdeg;
 uint32_t hp, camera_distance_mm, attack_id, phase_tick;
 unsigned hit_count; SttPlayHit hits[STT_PLAY_MAX_HITS];
 uint32_t frame_us, update_us, dropped;
} SttPlaySample;
/* Returns byte count or -1; never truncates a usable packet. No allocations/network. */
int stt_play_encode(char *out, size_t capacity, const SttPlaySample *s);
/* Latest-only mailbox: overwrite increments dropped; take clears it. No threads. */
typedef struct { SttPlaySample latest; int ready; uint32_t dropped; } SttPlayMailbox;
void stt_play_offer(SttPlayMailbox *m, const SttPlaySample *s);
int stt_play_take(SttPlayMailbox *m, SttPlaySample *s);
#endif

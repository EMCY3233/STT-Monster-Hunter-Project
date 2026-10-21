#ifndef STT_DEADLINE_CLOCK_H
#define STT_DEADLINE_CLOCK_H
#include <stdint.h>

typedef struct SttDeadlineClock {
    uint64_t process_start_us, process_last_us;
    uint64_t rtc_start_ticks, rtc_last_ticks;
    uint32_t ticks_per_second;
    int valid;
} SttDeadlineClock;

int stt_clock_start(SttDeadlineClock *clock, uint64_t process_us,
                    uint64_t rtc_ticks, uint32_t ticks_per_second);
int stt_clock_sample(SttDeadlineClock *clock, uint64_t process_us,
                     uint64_t rtc_ticks, int rtc_ok, uint64_t *elapsed_ms);
#endif

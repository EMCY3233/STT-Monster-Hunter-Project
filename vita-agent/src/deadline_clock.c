#include "deadline_clock.h"

int stt_clock_start(SttDeadlineClock *clock, uint64_t process_us,
                    uint64_t rtc_ticks, uint32_t ticks_per_second) {
    if (!clock) return -1;
    clock->valid = 0;
    if (!ticks_per_second) return -1;
    clock->process_start_us = clock->process_last_us = process_us;
    clock->rtc_start_ticks = clock->rtc_last_ticks = rtc_ticks;
    clock->ticks_per_second = ticks_per_second;
    clock->valid = 1;
    return 0;
}

int stt_clock_sample(SttDeadlineClock *clock, uint64_t process_us,
                     uint64_t rtc_ticks, int rtc_ok, uint64_t *elapsed_ms) {
    if (!clock || !elapsed_ms || !clock->valid) return -1;
    if (!rtc_ok || process_us < clock->process_last_us || rtc_ticks < clock->rtc_last_ticks) {
        clock->valid = 0;
        return -1;
    }
    uint64_t delta = rtc_ticks - clock->rtc_start_ticks;
    uint64_t seconds = delta / clock->ticks_per_second;
    /* Saturate beyond this app's deadline: no overflow on large forward jumps. */
    uint64_t rtc_ms = seconds >= 181 ? 181000 : seconds * 1000 +
        (delta % clock->ticks_per_second) * 1000 / clock->ticks_per_second;
    uint64_t process_ms = (process_us - clock->process_start_us) / 1000;
    if (process_ms > 181000) process_ms = 181000;
    *elapsed_ms = process_ms > rtc_ms ? process_ms : rtc_ms;
    clock->process_last_us = process_us;
    clock->rtc_last_ticks = rtc_ticks;
    return 0;
}

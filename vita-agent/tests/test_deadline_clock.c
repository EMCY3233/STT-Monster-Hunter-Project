#include "deadline_clock.h"
#include "recovery.h"
#include <assert.h>
#include <stdio.h>

int main(void) {
    SttDeadlineClock clock;
    SttRecovery recovery;
    uint64_t elapsed = 0;
    assert(stt_clock_start(&clock, 1000000, 5000000, 1000000) == 0);
    stt_recovery_start(&recovery, 0);
    assert(stt_clock_sample(&clock, 11000000, 15000000, 1, &elapsed) == 0 && elapsed == 10000);
    /* RTC advances during suspension while process clock barely advances. */
    assert(stt_clock_sample(&clock, 12000000, 65000000, 1, &elapsed) == 0 && elapsed == 60000);
    assert(stt_recovery_step(&recovery, elapsed, 1, 10) == STT_OPEN_SOCKET);
    assert(stt_clock_sample(&clock, 13000000, 185000000, 1, &elapsed) == 0 && elapsed == 180000);
    assert(stt_recovery_step(&recovery, elapsed, 1, 10) == STT_STOP_DEADLINE);

    /* Offline grace also includes elapsed RTC time. */
    assert(stt_clock_start(&clock, 0, 0, 1000) == 0);
    stt_recovery_start(&recovery, 0);
    assert(stt_clock_sample(&clock, 1000000, 1000, 1, &elapsed) == 0);
    assert(stt_recovery_step(&recovery, elapsed, 0, 1) == STT_WAIT);
    assert(stt_clock_sample(&clock, 1000000, 31000, 1, &elapsed) == 0 && elapsed == 31000);
    assert(stt_recovery_step(&recovery, elapsed, 1, 1) == STT_STOP_OFFLINE);

    /* An RTC that stalls cannot slow an advancing process clock. */
    assert(stt_clock_start(&clock, 0, 0, 1) == 0);
    assert(stt_clock_sample(&clock, 1500000, 0, 1, &elapsed) == 0 && elapsed == 1500);
    assert(stt_clock_sample(&clock, 1500000, UINT64_MAX, 1, &elapsed) == 0 && elapsed == 181000);

    /* Backward adjustments and failed readings stop until a fresh manual start. */
    assert(stt_clock_start(&clock, 100, 100, 1) == 0);
    assert(stt_clock_sample(&clock, 101, 99, 1, &elapsed) == -1);
    assert(stt_clock_sample(&clock, 102, 102, 1, &elapsed) == -1);
    assert(stt_clock_start(&clock, 100, 100, 1) == 0);
    assert(stt_clock_sample(&clock, 99, 100, 1, &elapsed) == -1);
    assert(stt_clock_start(&clock, 100, 100, 1) == 0);
    assert(stt_clock_sample(&clock, 101, 101, 0, &elapsed) == -1);
    assert(stt_clock_start(&clock, 0, 0, 0) == -1);

    /* Fractional ticks and very large resolutions remain bounded. */
    assert(stt_clock_start(&clock, 0, 0, 3) == 0);
    assert(stt_clock_sample(&clock, 0, 2, 1, &elapsed) == 0 && elapsed == 666);
    assert(stt_clock_start(&clock, 0, 0, UINT32_MAX) == 0);
    assert(stt_clock_sample(&clock, 0, UINT32_MAX - 1, 1, &elapsed) == 0 && elapsed == 999);
    puts("PASS: suspend deadlines, offline grace, clock faults, jumps and conversion bounds");
    return 0;
}

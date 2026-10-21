#include "recovery.h"
#include <assert.h>
#include <stdio.h>

int main(void) {
    SttRecovery s;
    stt_recovery_start(&s, 1000);
    assert(stt_recovery_step(&s, 1000, 1, 0) == STT_OPEN_SOCKET);
    stt_recovery_opened(&s, 1);
    assert(stt_recovery_step(&s, 2000, 1, 1) == STT_SEND);
    /* Link disappears, then returns without a new manual trial. */
    assert(stt_recovery_step(&s, 3000, 0, 2) == STT_WAIT);
    assert(stt_recovery_step(&s, 13000, 0, 2) == STT_WAIT);
    assert(stt_recovery_step(&s, 14000, 1, 2) == STT_OPEN_SOCKET);
    stt_recovery_opened(&s, 1);
    assert(stt_recovery_step(&s, 15000, 1, 2) == STT_SEND);
    /* A stale socket may fail even when the link reports connected. */
    stt_recovery_sent(&s, 0);
    assert(stt_recovery_step(&s, 16000, 1, 3) == STT_OPEN_SOCKET);
    stt_recovery_opened(&s, 1);
    stt_recovery_sent(&s, 1);
    assert(s.failures == 0);
    assert(stt_recovery_step(&s, 17000, 1, 4) == STT_SEND);
    assert(stt_recovery_step(&s, 18000, 1, 60) == STT_DONE);

    /* No endless retry: opening a socket is not evidence of delivery. */
    stt_recovery_start(&s, 0);
    for (unsigned int i = 0; i < 5; i++) {
        assert(stt_recovery_step(&s, i*1000, 1, i) == STT_OPEN_SOCKET);
        stt_recovery_opened(&s, 1);
        stt_recovery_sent(&s, 0);
    }
    assert(stt_recovery_step(&s, 5000, 1, 5) == STT_STOP_RETRIES);
    stt_recovery_start(&s, 0);
    for (unsigned int i = 0; i < 5; i++) stt_recovery_opened(&s, 0);
    assert(stt_recovery_step(&s, 5000, 1, 0) == STT_STOP_RETRIES);

    /* Exact offline deadline applies even if link comes back at that instant. */
    stt_recovery_start(&s, 0);
    assert(stt_recovery_step(&s, 1000, 0, 0) == STT_WAIT);
    assert(stt_recovery_step(&s, 30999, 0, 0) == STT_WAIT);
    assert(stt_recovery_step(&s, 31000, 1, 0) == STT_STOP_OFFLINE);
    assert(stt_recovery_step(&s, 31000, 0, 0) == STT_STOP_OFFLINE);

    /* Long suspension or a clock regression cannot extend a trial indefinitely. */
    stt_recovery_start(&s, 1000);
    assert(stt_recovery_step(&s, 180999, 1, 10) == STT_OPEN_SOCKET);
    assert(stt_recovery_step(&s, 181000, 1, 10) == STT_STOP_DEADLINE);
    assert(stt_recovery_step(&s, 999, 1, 10) == STT_STOP_DEADLINE);
    puts("PASS: reconnect, stale socket, retry bounds, offline and session deadlines");
    return 0;
}

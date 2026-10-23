/* Host tests for the Vita agent's portable logic (no Vita SDK needed).
 * They check recovery, deadline clock and encoding decisions only; they do not
 * replace physical tests on the console. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "recovery.h"
#include "deadline_clock.h"
#include "telemetry.h"

static int failures = 0;
#define CHECK(cond) do { if (!(cond)) { \
    fprintf(stderr, "FAIL %s:%d: %s\n", __FILE__, __LINE__, #cond); failures++; } } while (0)

static void test_recovery_normal_send(void) {
    SttRecovery r;
    stt_recovery_start(&r, 0);
    CHECK(stt_recovery_step(&r, 0, 1, 0) == STT_OPEN_SOCKET);
    stt_recovery_opened(&r, 1);
    CHECK(stt_recovery_step(&r, 1000, 1, 0) == STT_SEND);
    stt_recovery_sent(&r, 1);
    CHECK(stt_recovery_step(&r, 2000, 1, 1) == STT_SEND);
    CHECK(stt_recovery_step(&r, 2000, 1, 60) == STT_DONE);
}

static void test_recovery_offline_wait_and_reconnect(void) {
    SttRecovery r;
    stt_recovery_start(&r, 0);
    stt_recovery_opened(&r, 1);
    CHECK(stt_recovery_step(&r, 1000, 0, 1) == STT_WAIT);
    CHECK(stt_recovery_step(&r, 29999 + 1000, 0, 1) == STT_WAIT);
    /* Reconnect inside 30 s: socket must be recreated. */
    CHECK(stt_recovery_step(&r, 30000, 1, 1) == STT_OPEN_SOCKET);
    stt_recovery_opened(&r, 1);
    CHECK(stt_recovery_step(&r, 31000, 1, 1) == STT_SEND);
}

static void test_recovery_offline_limit(void) {
    SttRecovery r;
    stt_recovery_start(&r, 0);
    CHECK(stt_recovery_step(&r, 5000, 0, 0) == STT_WAIT);
    CHECK(stt_recovery_step(&r, 35000, 0, 0) == STT_STOP_OFFLINE);
    /* Even if the network comes back at the limit, the 30 s budget is spent. */
    stt_recovery_start(&r, 0);
    CHECK(stt_recovery_step(&r, 5000, 0, 0) == STT_WAIT);
    CHECK(stt_recovery_step(&r, 35000, 1, 0) == STT_STOP_OFFLINE);
}

static void test_recovery_offline_jump_during_suspend(void) {
    /* Elapsed time jumps (suspend) while offline: must stop, not keep waiting. */
    SttRecovery r;
    stt_recovery_start(&r, 0);
    CHECK(stt_recovery_step(&r, 1000, 0, 0) == STT_WAIT);
    CHECK(stt_recovery_step(&r, 120000, 0, 0) == STT_STOP_OFFLINE);
}

static void test_recovery_time_regression_stops(void) {
    SttRecovery r;
    stt_recovery_start(&r, 10000);
    CHECK(stt_recovery_step(&r, 9999, 1, 0) == STT_STOP_DEADLINE);
    stt_recovery_start(&r, 0);
    CHECK(stt_recovery_step(&r, 5000, 0, 0) == STT_WAIT);
    CHECK(stt_recovery_step(&r, 4000, 0, 0) == STT_STOP_OFFLINE);
}

static void test_recovery_deadline_and_retries(void) {
    SttRecovery r;
    stt_recovery_start(&r, 0);
    CHECK(stt_recovery_step(&r, 179999, 1, 0) == STT_OPEN_SOCKET);
    CHECK(stt_recovery_step(&r, 180000, 1, 0) == STT_STOP_DEADLINE);
    stt_recovery_start(&r, 0);
    for (int i = 0; i < 4; i++) {
        CHECK(stt_recovery_step(&r, 1000u * i, 1, 0) == STT_OPEN_SOCKET);
        stt_recovery_opened(&r, 0);
    }
    CHECK(stt_recovery_step(&r, 4000, 1, 0) == STT_OPEN_SOCKET);
    stt_recovery_opened(&r, 1);
    stt_recovery_sent(&r, 0);
    CHECK(stt_recovery_step(&r, 5000, 1, 1) == STT_STOP_RETRIES);
    /* A success resets the consecutive count. */
    stt_recovery_start(&r, 0);
    for (int i = 0; i < 4; i++) stt_recovery_opened(&r, 0);
    stt_recovery_opened(&r, 1);
    stt_recovery_sent(&r, 1);
    CHECK(stt_recovery_step(&r, 1000, 1, 1) == STT_SEND);
}

static void test_clock_suspend_uses_rtc(void) {
    SttDeadlineClock c;
    uint64_t ms = 0;
    CHECK(stt_clock_start(&c, 0, 1000000, 1000000) == 0);
    /* Process time frozen during suspend; RTC advanced 100 s. */
    CHECK(stt_clock_sample(&c, 2000000, 1000000 + 100000000ull, 1, &ms) == 0);
    CHECK(ms == 100000);
    /* Process time ahead of RTC: the larger value wins. */
    CHECK(stt_clock_sample(&c, 150000000, 1000000 + 120000000ull, 1, &ms) == 0);
    CHECK(ms == 150000);
}

static void test_clock_regressions_invalidate(void) {
    SttDeadlineClock c;
    uint64_t ms = 0;
    CHECK(stt_clock_start(&c, 1000, 5000, 1000000) == 0);
    CHECK(stt_clock_sample(&c, 2000, 4999, 1, &ms) < 0);       /* RTC backwards */
    CHECK(stt_clock_sample(&c, 3000, 6000, 1, &ms) < 0);       /* stays invalid */
    CHECK(stt_clock_start(&c, 1000, 5000, 1000000) == 0);
    CHECK(stt_clock_sample(&c, 999, 6000, 1, &ms) < 0);        /* process backwards */
    CHECK(stt_clock_start(&c, 1000, 5000, 1000000) == 0);
    CHECK(stt_clock_sample(&c, 2000, 6000, 0, &ms) < 0);       /* RTC read failed */
    CHECK(stt_clock_start(&c, 0, 0, 0) < 0);                   /* zero resolution */
}

static void test_clock_saturates_large_jumps(void) {
    SttDeadlineClock c;
    uint64_t ms = 0;
    CHECK(stt_clock_start(&c, 0, 0, 1000000) == 0);
    CHECK(stt_clock_sample(&c, 0, UINT64_MAX, 1, &ms) == 0);
    CHECK(ms == 181000);
    CHECK(stt_clock_start(&c, 0, 0, 1000000) == 0);
    CHECK(stt_clock_sample(&c, UINT64_MAX, 0, 1, &ms) == 0);
    CHECK(ms == 181000);
}

static void test_private_ip(void) {
    unsigned char ok1[4] = {192, 168, 1, 2}, ok2[4] = {10, 0, 0, 1}, ok3[4] = {172, 31, 0, 9};
    unsigned char bad1[4] = {8, 8, 8, 8}, bad2[4] = {192, 168, 1, 255}, bad3[4] = {172, 32, 0, 1};
    unsigned char bad4[4] = {192, 168, 1, 0};
    CHECK(stt_private_ip(ok1) && stt_private_ip(ok2) && stt_private_ip(ok3));
    CHECK(!stt_private_ip(bad1) && !stt_private_ip(bad2) && !stt_private_ip(bad3) && !stt_private_ip(bad4));
}

static void test_encode(void) {
    char out[512];
    SttDiagnostics d = {2, 1, -2147418111, 1};
    int n = stt_encode_v2(out, sizeof out, "vita-1-2", 3, 1500, 80, &d);
    CHECK(n > 0 && (size_t)n == strlen(out));
    CHECK(strcmp(out, "{\"version\":2,\"session\":\"vita-1-2\",\"source\":\"vita\",\"seq\":3,"
                      "\"uptime_ms\":1500,\"battery_pct\":80,\"diagnostics\":{\"send_ok\":2,"
                      "\"send_errors\":1,\"last_result\":-2147418111,\"net_errno\":1}}") == 0);
    CHECK(stt_encode(out, sizeof out, "s", 0, 0, -1) > 0 && strstr(out, "\"battery_pct\":null"));
    CHECK(stt_encode(out, sizeof out, "s", 0, 0, 101) > 0 && strstr(out, "\"battery_pct\":null"));
    SttDiagnostics bad = {1, 1, 0, 0};
    CHECK(stt_encode_v2(out, sizeof out, "s", 3, 0, 50, &bad) < 0);   /* counters != seq */
    CHECK(stt_encode_v2(out, sizeof out, "s", 0, 0, 50, NULL) < 0);
    CHECK(stt_encode(out, sizeof out, "bad\"name", 0, 0, 50) < 0);
    CHECK(stt_encode(out, sizeof out, "", 0, 0, 50) < 0);
    CHECK(stt_encode(out, 10, "s", 0, 0, 50) < 0);                     /* too small */
    char long_session[66];
    memset(long_session, 'a', 65); long_session[65] = 0;
    CHECK(stt_encode(out, sizeof out, long_session, 0, 0, 50) < 0);
    CHECK(stt_encode(out, sizeof out, "s", 9007199254740992ull, 0, 50) < 0);
}

int main(int argc, char **argv) {
    test_recovery_normal_send();
    test_recovery_offline_wait_and_reconnect();
    test_recovery_offline_limit();
    test_recovery_offline_jump_during_suspend();
    test_recovery_time_regression_stops();
    test_recovery_deadline_and_retries();
    test_clock_suspend_uses_rtc();
    test_clock_regressions_invalidate();
    test_clock_saturates_large_jumps();
    test_private_ip();
    test_encode();
    /* Optional: print one encoded STT/2 packet so the Python side can validate it. */
    if (argc > 1 && strcmp(argv[1], "--emit") == 0) {
        char out[512];
        SttDiagnostics d = {5, 2, -2147418111, 35};
        if (stt_encode_v2(out, sizeof out, "vita-abc-123", 7, 7000, 42, &d) < 0) return 2;
        puts(out);
    }
    if (failures) { fprintf(stderr, "%d check(s) failed\n", failures); return 1; }
    fprintf(stderr, "C agent logic: all checks passed\n");
    return 0;
}

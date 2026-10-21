#include "telemetry.h"
#include <inttypes.h>
#include <stdio.h>
#include <string.h>

int stt_private_ip(const unsigned char ip[4]) {
    /* Restrict this first prototype to private unicast-style destinations. */
    return ip && ip[3] != 0 && ip[3] != 255 &&
        (ip[0] == 10 || (ip[0] == 172 && ip[1] >= 16 && ip[1] <= 31) ||
         (ip[0] == 192 && ip[1] == 168));
}

static int encode_packet(char *out, size_t capacity, const char *session,
               uint64_t seq, uint64_t uptime_ms, int battery, const SttDiagnostics *d) {
    char battery_text[8];
    char diagnostics[256] = "";
    size_t length;
    int written;
    if (!out || !capacity || !session) return -1;
    length = strlen(session);
    if (!length || length > 64 || seq > UINT64_C(9007199254740991) ||
        uptime_ms > UINT64_C(9007199254740991)) return -1;
    if (d) {
        if (d->send_ok > seq || d->send_errors > seq || d->send_ok + d->send_errors != seq) return -1;
        written = snprintf(diagnostics, sizeof diagnostics,
            ",\"diagnostics\":{\"send_ok\":%" PRIu64 ",\"send_errors\":%" PRIu64
            ",\"last_result\":%" PRId32 ",\"net_errno\":%" PRId32 "}",
            d->send_ok, d->send_errors, d->last_result, d->net_errno);
        if (written < 0 || (size_t)written >= sizeof diagnostics) return -1;
    }
    for (size_t i = 0; i < length; i++) {
        char c = session[i];
        if (!((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
              (c >= '0' && c <= '9') || c == '_' || c == '-')) return -1;
    }
    if (battery >= 0 && battery <= 100)
        snprintf(battery_text, sizeof battery_text, "%d", battery);
    else
        strcpy(battery_text, "null");
    written = snprintf(out, capacity,
        "{\"version\":%d,\"session\":\"%s\",\"source\":\"vita\","
        "\"seq\":%" PRIu64 ",\"uptime_ms\":%" PRIu64 ",\"battery_pct\":%s%s}",
        d ? 2 : 1, session, seq, uptime_ms, battery_text, diagnostics);
    if (written < 0 || (size_t)written >= capacity || written > 1024) return -1;
    return written;
}

int stt_encode(char *out, size_t capacity, const char *session,
               uint64_t seq, uint64_t uptime_ms, int battery) {
    return encode_packet(out, capacity, session, seq, uptime_ms, battery, NULL);
}

int stt_encode_v2(char *out, size_t capacity, const char *session,
                  uint64_t seq, uint64_t uptime_ms, int battery, const SttDiagnostics *d) {
    if (!d) return -1;
    return encode_packet(out, capacity, session, seq, uptime_ms, battery, d);
}

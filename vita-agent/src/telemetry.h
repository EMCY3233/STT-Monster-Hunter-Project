#ifndef STT_TELEMETRY_H
#define STT_TELEMETRY_H
#include <stddef.h>
#include <stdint.h>
typedef struct SttDiagnostics {
    uint64_t send_ok;
    uint64_t send_errors;
    int32_t last_result;
    int32_t net_errno;
} SttDiagnostics;
int stt_private_ip(const unsigned char ip[4]);
int stt_encode(char *out, size_t capacity, const char *session,
               uint64_t seq, uint64_t uptime_ms, int battery);
int stt_encode_v2(char *out, size_t capacity, const char *session,
                  uint64_t seq, uint64_t uptime_ms, int battery,
                  const SttDiagnostics *diagnostics);
#endif

#ifndef STT_TELEMETRY_H
#define STT_TELEMETRY_H
#include <stddef.h>
#include <stdint.h>
int stt_private_ip(const unsigned char ip[4]);
int stt_encode(char *out, size_t capacity, const char *session,
               uint64_t seq, uint64_t uptime_ms, int battery);
#endif

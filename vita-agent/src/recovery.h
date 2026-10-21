#ifndef STT_RECOVERY_H
#define STT_RECOVERY_H
#include <stdint.h>

typedef enum SttRecoveryAction {
    STT_WAIT, STT_OPEN_SOCKET, STT_SEND, STT_DONE,
    STT_STOP_OFFLINE, STT_STOP_RETRIES, STT_STOP_DEADLINE
} SttRecoveryAction;

typedef struct SttRecovery {
    uint64_t started_ms;
    uint64_t offline_since_ms;
    unsigned int failures;
    int needs_socket;
} SttRecovery;

void stt_recovery_start(SttRecovery *state, uint64_t now_ms);
SttRecoveryAction stt_recovery_step(SttRecovery *state, uint64_t now_ms,
                                    int connected, unsigned int attempts);
void stt_recovery_opened(SttRecovery *state, int success);
void stt_recovery_sent(SttRecovery *state, int success);
#endif

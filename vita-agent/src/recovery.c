#include "recovery.h"

void stt_recovery_start(SttRecovery *state, uint64_t now_ms) {
    state->started_ms = now_ms;
    state->offline_since_ms = UINT64_MAX;
    state->failures = 0;
    state->needs_socket = 1;
}

SttRecoveryAction stt_recovery_step(SttRecovery *state, uint64_t now_ms,
                                    int connected, unsigned int attempts) {
    if (attempts >= 60) return STT_DONE;
    if (now_ms < state->started_ms || now_ms - state->started_ms >= 180000)
        return STT_STOP_DEADLINE;
    if (state->failures >= 5) return STT_STOP_RETRIES;
    if (!connected) {
        if (state->offline_since_ms == UINT64_MAX) state->offline_since_ms = now_ms;
        state->needs_socket = 1;
    }
    if (state->offline_since_ms != UINT64_MAX) {
        if (now_ms < state->offline_since_ms || now_ms - state->offline_since_ms >= 30000)
            return STT_STOP_OFFLINE;
        if (!connected) return STT_WAIT;
        state->offline_since_ms = UINT64_MAX;
        state->needs_socket = 1;
    }
    return state->needs_socket ? STT_OPEN_SOCKET : STT_SEND;
}

void stt_recovery_opened(SttRecovery *state, int success) {
    state->needs_socket = !success;
    if (!success) state->failures++;
}

void stt_recovery_sent(SttRecovery *state, int success) {
    if (success) state->failures = 0;
    else {
        state->failures++;
        state->needs_socket = 1;
    }
}

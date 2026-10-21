#include "telemetry.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    char buffer[512];
    unsigned char good[4] = {192,168,1,2}, bad[4] = {8,8,8,8};
    assert(stt_private_ip(good));
    assert(!stt_private_ip(bad));
    good[3] = 255;
    assert(!stt_private_ip(good));
    assert(stt_encode(buffer, 3, "demo", 0, 0, 50) == -1);
    assert(stt_encode(buffer, sizeof buffer, "bad\"", 0, 0, 50) == -1);
    assert(stt_encode(buffer, sizeof buffer, "", 0, 0, 50) == -1);
    assert(stt_encode(buffer, sizeof buffer, "demo", UINT64_MAX, 0, 50) == -1);
    assert(stt_encode(buffer, sizeof buffer, "demo", 0, UINT64_MAX, 50) == -1);
    assert(stt_encode(buffer, sizeof buffer, "demo", 0, 0, -1) > 0);
    assert(strstr(buffer, "\"battery_pct\":null"));
    puts(buffer);
    assert(stt_encode(buffer, sizeof buffer, "demo", 59, 59000, 100) > 0);
    puts(buffer);
    return 0;
}

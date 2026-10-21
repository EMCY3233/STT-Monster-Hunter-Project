#include <psp2/ctrl.h>
#include <psp2/kernel/processmgr.h>
#include <psp2/kernel/threadmgr.h>
#include <psp2/net/net.h>
#include <psp2/power.h>
#include <psp2/rtc.h>
#include <psp2/sysmodule.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "debugScreen.h"
#include "telemetry.h"

int main(void) {
    unsigned char ip[4] = {192, 168, 1, 2};
    unsigned int previous = 0, seq = 0, sent = 0, errors = 0, consecutive = 0;
    int selected = 3, active = 0, sock = -1, net_ready = 0, module_ready = 0;
    int result = 0, last_error = 0;
    uint64_t start = 0, next = 0;
    char session[65] = "", payload[512], destination[16];
    void *memory = NULL;
    SceNetSockaddrIn address;
    const char *status = "EDIT PC IP, THEN CROSS TO START";

    if (psvDebugScreenInit() < 0) return 1;
    result = sceSysmoduleLoadModule(SCE_SYSMODULE_NET);
    if (result < 0) goto failure;
    module_ready = 1;
    memory = malloc(1024 * 1024);
    if (!memory) { result = -1; goto failure; }
    SceNetInitParam init = {memory, 1024 * 1024, 0};
    result = sceNetInit(&init);
    if (result < 0) goto failure;
    net_ready = 1;
    sock = sceNetSocket("stt-monitor", SCE_NET_AF_INET, SCE_NET_SOCK_DGRAM, 0);
    if (sock < 0) { result = sock; goto failure; }
    int nonblocking = 1;
    result = sceNetSetsockopt(sock, SCE_NET_SOL_SOCKET, SCE_NET_SO_NBIO,
                             &nonblocking, sizeof nonblocking);
    if (result < 0) goto failure;

    while (1) {
        SceCtrlData controls;
        memset(&controls, 0, sizeof controls);
        result = sceCtrlPeekBufferPositive(0, &controls, 1);
        if (result < 0) goto failure;
        unsigned int pressed = controls.buttons & ~previous;
        previous = controls.buttons;
        if (pressed & SCE_CTRL_START) break;
        if (pressed & SCE_CTRL_CIRCLE) { active = 0; status = "STOPPED"; }
        if (!active) {
            if (pressed & SCE_CTRL_LEFT) selected = (selected + 3) % 4;
            if (pressed & SCE_CTRL_RIGHT) selected = (selected + 1) % 4;
            if (pressed & SCE_CTRL_UP) ip[selected]++;
            if (pressed & SCE_CTRL_DOWN) ip[selected]--;
            if (pressed & SCE_CTRL_CROSS) {
                if (!stt_private_ip(ip)) status = "USE PRIVATE PC IP, LAST OCTET 1..254";
                else {
                    SceRtcTick tick;
                    result = sceRtcGetCurrentTick(&tick);
                    if (result < 0) goto failure;
                    start = sceKernelGetProcessTimeWide();
                    snprintf(session, sizeof session, "vita-%" PRIx64 "-%" PRIx64,
                             (uint64_t)tick.tick, start);
                    snprintf(destination, sizeof destination, "%u.%u.%u.%u", ip[0], ip[1], ip[2], ip[3]);
                    memset(&address, 0, sizeof address);
                    address.sin_len = sizeof address;
                    address.sin_family = SCE_NET_AF_INET;
                    address.sin_port = sceNetHtons(32100);
                    result = sceNetInetPton(SCE_NET_AF_INET, destination, &address.sin_addr);
                    if (result != 1) { result = -1; goto failure; }
                    seq = sent = errors = consecutive = 0;
                    last_error = 0;
                    next = start;
                    active = 1;
                    status = "RUNNING (UDP SEND IS NOT DELIVERY CONFIRMATION)";
                }
            }
        }
        uint64_t now = sceKernelGetProcessTimeWide();
        if (active && now >= next) {
            int size = stt_encode(payload, sizeof payload, session, seq,
                                  (now - start) / 1000, scePowerGetBatteryLifePercent());
            if (size < 0) { result = -1; goto failure; }
            result = sceNetSendto(sock, payload, size, SCE_NET_MSG_DONTWAIT,
                                 (SceNetSockaddr *)&address, sizeof address);
            if (result == size) { sent++; consecutive = 0; }
            else { errors++; consecutive++; last_error = result; }
            seq++;
            next = now + UINT64_C(1000000);
            if (consecutive >= 3) { active = 0; status = "STOPPED: 3 CONSECUTIVE SEND ERRORS"; }
            else if (seq >= 60) { active = 0; status = "COMPLETE: 60 ATTEMPTS; CHECK PC LOG"; }
        }
        psvDebugScreenPrintf("\033[H\033[2JSTT VITA MONITOR 0.1 - EXPERIMENTAL\n\n"
            "PC IP: %u.%u.%u.%u :32100   EDIT OCTET: %d\n"
            "LEFT/RIGHT: select; UP/DOWN: change (one press)\n"
            "CROSS: start 60 samples; CIRCLE: stop; START: exit\n\n"
            "%s\nAttempts: %u  Sent: %u  Errors: %u  Last: 0x%08X\n"
            "Session: %s\n\nNo commands received. No files written.\n",
            ip[0], ip[1], ip[2], ip[3], selected + 1, status,
            seq, sent, errors, (unsigned int)last_error, session);
        sceKernelDelayThread(50000);
    }
    result = 0;
    goto cleanup;

failure:
    psvDebugScreenPrintf("\nINITIALIZATION/RUNTIME ERROR: 0x%08X\nClosing in 3 seconds.\n", (unsigned int)result);
    sceKernelDelayThread(3000000);
cleanup:
    if (sock >= 0) sceNetSocketClose(sock);
    if (net_ready) sceNetTerm();
    free(memory);
    if (module_ready) sceSysmoduleUnloadModule(SCE_SYSMODULE_NET);
    psvDebugScreenFinish();
    sceKernelExitProcess(result < 0 ? 1 : 0);
    return 0;
}

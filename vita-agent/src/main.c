#include <psp2/ctrl.h>
#include <psp2/kernel/processmgr.h>
#include <psp2/kernel/threadmgr.h>
#include <psp2/net/net.h>
#include <psp2/net/netctl.h>
#include <psp2/power.h>
#include <psp2/rtc.h>
#include <psp2/sysmodule.h>
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "debugScreen.h"
#include "telemetry.h"
#include "recovery.h"

/* Stable rows: repaint changed text only, without clearing the framebuffer. */
static void screen_line(int row, const char *text) {
    static char previous[15][60];
    char current[60];
    snprintf(current, sizeof current, "%-59.59s", text);
    if (strcmp(current, previous[row]) != 0) {
        psvDebugScreenPrintf("\033[%d;1H%s", row + 1, current);
        memcpy(previous[row], current, sizeof current);
    }
}

static int capture_net_errno(void) {
    int *value = sceNetErrnoLoc();
    return value ? *value : 0;
}

static int open_udp(int *detail) {
    int socket_id = sceNetSocket("stt-monitor", SCE_NET_AF_INET, SCE_NET_SOCK_DGRAM, 0);
    if (socket_id < 0) { *detail = capture_net_errno(); return socket_id; }
    int enabled = 1;
    int code = sceNetSetsockopt(socket_id, SCE_NET_SOL_SOCKET, SCE_NET_SO_NBIO, &enabled, sizeof enabled);
    if (code < 0) {
        *detail = capture_net_errno();
        sceNetSocketClose(socket_id);
        return code;
    }
    return socket_id;
}

int main(void) {
    unsigned char ip[4] = {192, 168, 1, 2};
    unsigned int previous = 0, seq = 0, sent = 0, errors = 0;
    int selected = 3, active = 0, sock = -1, net_ready = 0, module_ready = 0;
    int result = 0, last_error = 0, last_net_errno = 0;
    int netctl_ready = 0;
    SttRecovery recovery;
    uint64_t start = 0, next = 0;
    char session[65] = "", payload[512], destination[16];
    void *memory = NULL;
    PsvDebugScreenFont *original_font = NULL, *large_font = NULL;
    SceNetSockaddrIn address;
    const char *status = "Configura IP del PC y pulsa Cruz.";

    if (psvDebugScreenInit() < 0) return 1;
    original_font = psvDebugScreenGetFont();
    large_font = psvDebugScreenScaleFont2x(original_font);
    if (large_font) psvDebugScreenSetFont(large_font);
    psvDebugScreenPuts("\033[2J\033[H");
    result = sceSysmoduleLoadModule(SCE_SYSMODULE_NET);
    if (result < 0) goto failure;
    module_ready = 1;
    memory = malloc(1024 * 1024);
    if (!memory) { result = -1; goto failure; }
    SceNetInitParam init = {memory, 1024 * 1024, 0};
    result = sceNetInit(&init);
    if (result < 0) goto failure;
    net_ready = 1;
    result = sceNetCtlInit();
    if (result < 0) goto failure;
    netctl_ready = 1;

    while (1) {
        SceCtrlData controls;
        memset(&controls, 0, sizeof controls);
        result = sceCtrlPeekBufferPositive(0, &controls, 1);
        if (result < 0) goto failure;
        unsigned int pressed = controls.buttons & ~previous;
        previous = controls.buttons;
        if (pressed & SCE_CTRL_START) break;
        if (pressed & SCE_CTRL_CIRCLE) { active = 0; status = "Parado."; }
        if (!active) {
            if (pressed & SCE_CTRL_LEFT) selected = (selected + 3) % 4;
            if (pressed & SCE_CTRL_RIGHT) selected = (selected + 1) % 4;
            if (pressed & SCE_CTRL_UP) ip[selected]++;
            if (pressed & SCE_CTRL_DOWN) ip[selected]--;
            if (pressed & SCE_CTRL_SQUARE) ip[selected] += 10;
            if (pressed & SCE_CTRL_TRIANGLE) ip[selected] -= 10;
            if (pressed & SCE_CTRL_CROSS) {
                if (!stt_private_ip(ip)) status = "IP privada; ultimo bloque entre 1 y 254.";
                else {
                    if (sock >= 0) sceNetSocketClose(sock);
                    sock = -1;
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
                    seq = sent = errors = 0;
                    stt_recovery_start(&recovery, start / 1000);
                    next = start;
                    active = 1;
                    status = "Enviando. Confirma recepcion en el PC.";
                }
            }
        }
        uint64_t now = sceKernelGetProcessTimeWide();
        if (active && now >= next) {
            next = now + UINT64_C(1000000);
            int network_state = SCE_NETCTL_STATE_DISCONNECTED;
            int state_result = sceNetCtlInetGetState(&network_state);
            if (state_result < 0) { last_error = state_result; last_net_errno = 0; }
            SttRecoveryAction action = stt_recovery_step(&recovery, now / 1000,
                state_result >= 0 && network_state == SCE_NETCTL_STATE_CONNECTED, seq);
            if (action == STT_DONE) { active = 0; status = "Terminado: 60 intentos. Revisa el PC."; }
            else if (action == STT_STOP_DEADLINE) { active = 0; status = "Parado: limite total de 180 segundos."; }
            else if (action == STT_STOP_RETRIES) { active = 0; status = "Parado: 5 fallos de red consecutivos."; }
            else if (action == STT_STOP_OFFLINE) { active = 0; status = "Parado: 30 segundos sin conexion."; }
            else if (action == STT_WAIT) {
                if (sock >= 0) { sceNetSocketClose(sock); sock = -1; }
                status = "Sin conexion. Esperando Wi-Fi (max 30s).";
            } else {
                if (action == STT_OPEN_SOCKET) {
                    if (sock >= 0) sceNetSocketClose(sock);
                    sock = open_udp(&last_net_errno);
                    stt_recovery_opened(&recovery, sock >= 0);
                    if (sock < 0) { last_error = sock; status = "Reintentando apertura de red..."; }
                }
                if (sock >= 0) {
                    SttDiagnostics diagnostics = {sent, errors, last_error, last_net_errno};
                    int size = stt_encode_v2(payload, sizeof payload, session, seq,
                        (now - start) / 1000, scePowerGetBatteryLifePercent(), &diagnostics);
                    if (size < 0) { result = -1; goto failure; }
                    result = sceNetSendto(sock, payload, size, SCE_NET_MSG_DONTWAIT,
                                         (SceNetSockaddr *)&address, sizeof address);
                    int success = result == size;
                    if (success) { sent++; status = "Enviando. Confirma recepcion en el PC."; }
                    else {
                        last_net_errno = capture_net_errno(); errors++; last_error = result;
                        status = "Fallo de envio. Recreando socket...";
                    }
                    stt_recovery_sent(&recovery, success);
                    seq++;
                    if (seq >= 60) { active = 0; status = "Terminado: 60 intentos. Revisa el PC."; }
                }
            }
        }
        char line[128];
        screen_line(0, "STT VITA MONITOR 0.4 - EXPERIMENTAL");
        screen_line(1, "");
        snprintf(line, sizeof line, "PC: %u.%u.%u.%u :32100", ip[0], ip[1], ip[2], ip[3]);
        screen_line(2, line);
        snprintf(line, sizeof line, "Bloque IP seleccionado: %d", selected + 1);
        screen_line(3, line);
        screen_line(4, "Izq/Der: bloque   Arriba/Abajo: +/-1");
        screen_line(5, "Cuadrado: +10   Triangulo: -10");
        screen_line(6, "Cruz: iniciar   Circulo: parar   START: salir");
        screen_line(7, "");
        screen_line(8, status);
        snprintf(line, sizeof line, "Intentos: %u/60   Envios: %u   Errores: %u", seq, sent, errors);
        screen_line(9, line);
        snprintf(line, sizeof line, "Ultimo error: 0x%08X", (unsigned int)last_error);
        screen_line(10, line);
        snprintf(line, sizeof line, "Detalle red: %d (0x%08X)", last_net_errno, (unsigned int)last_net_errno);
        screen_line(11, line);
        snprintf(line, sizeof line, "Sesion: %s", session);
        screen_line(12, line);
        screen_line(13, "");
        screen_line(14, "UDP: un envio no confirma entrega.");
        sceKernelDelayThread(50000);
    }
    result = 0;
    goto cleanup;

failure:
    psvDebugScreenPrintf("\nINITIALIZATION/RUNTIME ERROR: 0x%08X\nClosing in 3 seconds.\n", (unsigned int)result);
    sceKernelDelayThread(3000000);
cleanup:
    if (sock >= 0) sceNetSocketClose(sock);
    if (netctl_ready) sceNetCtlTerm();
    if (net_ready) sceNetTerm();
    free(memory);
    if (module_ready) sceSysmoduleUnloadModule(SCE_SYSMODULE_NET);
    if (large_font) {
        psvDebugScreenSetFont(original_font);
        free(large_font->glyphs);
        free(large_font);
    }
    psvDebugScreenFinish();
    sceKernelExitProcess(result < 0 ? 1 : 0);
    return 0;
}

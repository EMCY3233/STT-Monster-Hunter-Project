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

/* Stable rows: repaint changed text only, without clearing the framebuffer. */
static void screen_line(int row, const char *text) {
    static char previous[14][60];
    char current[60];
    snprintf(current, sizeof current, "%-59.59s", text);
    if (strcmp(current, previous[row]) != 0) {
        psvDebugScreenPrintf("\033[%d;1H%s", row + 1, current);
        memcpy(previous[row], current, sizeof current);
    }
}

int main(void) {
    unsigned char ip[4] = {192, 168, 1, 2};
    unsigned int previous = 0, seq = 0, sent = 0, errors = 0, consecutive = 0;
    int selected = 3, active = 0, sock = -1, net_ready = 0, module_ready = 0;
    int result = 0, last_error = 0;
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
                    status = "Enviando. Confirma recepcion en el PC.";
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
            if (consecutive >= 3) { active = 0; status = "Parado: 3 errores de envio consecutivos."; }
            else if (seq >= 60) { active = 0; status = "Terminado: 60 intentos. Revisa el PC."; }
        }
        char line[128];
        screen_line(0, "STT VITA MONITOR 0.2 - EXPERIMENTAL");
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
        snprintf(line, sizeof line, "Sesion: %s", session);
        screen_line(11, line);
        screen_line(12, "");
        screen_line(13, "UDP: un envio no confirma entrega.");
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
    if (large_font) {
        psvDebugScreenSetFont(original_font);
        free(large_font->glyphs);
        free(large_font);
    }
    psvDebugScreenFinish();
    sceKernelExitProcess(result < 0 ? 1 : 0);
    return 0;
}

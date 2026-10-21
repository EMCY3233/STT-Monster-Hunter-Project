# Revisión preliminar de APIs — 21 de octubre de 2026

Fuentes oficiales consultadas, sin copiar sus implementaciones:

- [Ejemplo net_http](https://github.com/vitasdk/samples/blob/master/net_http/src/main.c): carga del módulo NET, memoria de sceNetInit y orden de cierre. El futuro agente no usará su descarga HTTP ni escritura de archivos.
- [Cabecera net.h](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/net/net.h): declara sceNetSocket y APIs de red; antes de implementar faltan revisar tipos comunes, envío no bloqueante y códigos de error.
- [CMake hello_world](https://github.com/vitasdk/samples/blob/master/hello_world/CMakeLists.txt): toolchain, vita.cmake y empaquetado. El ejemplo no constituye un build del monitor.
- [Cabecera rtc.h](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/rtc.h): reloj de calendario disponible; no asumir que es monotónico para uptime_ms. Verificar reloj de proceso adecuado antes de elegirlo.

Estado del entorno: VITASDK ausente, CMake y Docker no encontrados en PATH. La consulta de WSL fuera del aislamiento no mostró distribuciones. No se ha instalado software del sistema ni ejecutado código Vita.

Siguiente puerta: preparar un toolchain reproducible y fijar sus versiones; revisar temporización, controles de salida y sockets; compilar una aplicación mínima antes de proponer un paquete para consola. No se presenta código fuente no compilado como agente funcional.

## Actualización STT-MON-003

La rama experimental incorpora compilación remota con la imagen fechada documentada en [VitaSDK](https://vitasdk.org/). Se han revisado además las cabeceras oficiales [processmgr.h](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/kernel/processmgr.h), [ctrl.h](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/ctrl.h), [power.h](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/power.h) y [psp2common/net.h](https://github.com/vitasdk/vita-headers/blob/master/include/psp2common/net.h).

Selecciones del código: sceKernelGetProcessTimeWide para tiempo transcurrido, sceRtcGetCurrentTick solo para identificador, sceCtrlPeekBufferPositive para salida y edición, scePowerGetBatteryLifePercent como lectura, sceNetSetsockopt con SO_NBIO y sceNetSendto con MSG_DONTWAIT. Ninguna prueba de estas llamadas en consola se ha ejecutado. La validación del codificador C y su compatibilidad Python sí pasó en GitHub; el resultado del build Vita debe consultarse por separado.

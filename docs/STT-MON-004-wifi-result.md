# STT-MON-004 — corte Wi-Fi con agente 0.2

21 de octubre de 2026. El usuario informó desactivar Wi-Fi unos diez segundos, reactivarlo y volver a STT Vita Monitor sin reiniciar el ensayo.

## Evidencia

- El PC recibió 39 muestras de una sesión, secuencias consecutivas 0–38, entre 07:09:53.799796 y 07:10:32.031625 (Europe/Madrid). No llegaron más mensajes de ese ensayo antes de cerrar el receptor.
- Usuario: Intentos 60/60, Envíos 46, Errores 14, Último error `0x804101CD`.
- El emisor contó 46 envíos aceptados localmente; siete no aparecen en la captura. No se atribuye esa diferencia a una causa concreta ni se confunde aceptación local con entrega.
- El contador continuó según el usuario, pero el PC no observó recuperación de recepción. **Reconexión automática no validada.** La intervención en Ajustes puede suspender el proceso: el ensayo no aísla suspensión y corte de radio.

La [cabecera oficial](https://github.com/vitasdk/vita-headers/blob/master/include/psp2common/net.h) identifica el código como SCE_NET_ERROR_ERETURN. El nombre por sí solo no establece el motivo subyacente. [sceNetErrnoLoc](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/net/net.h) permite capturar el detalle de errno de red, que 0.2 no registraba.

## Cierre y siguiente revisión

Se cerró el receptor y se confirmó retirada de la excepción temporal de firewall. Registro bruto y contadores del usuario guardados localmente; sin cambios de firmware/plugins ni nuevos archivos transferidos para este informe.

La revisión 0.3 añade detalle de error y mensajes STT/2, y recrea el socket al iniciar manualmente otro ensayo. Esto mejora diagnóstico y recuperación manual; no se presenta como reconexión automática resuelta. Requiere nuevo receptor compatible y prueba física independiente.

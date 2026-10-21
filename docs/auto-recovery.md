# Recuperación acotada — agente 0.4

Implementación pendiente de validación física. Mantiene STT/2, IP privada elegida manualmente y un máximo de 60 intentos de envío por ensayo. No cambia perfiles ni enciende la radio Wi-Fi.

## Comportamiento

Tras Cruz, consulta [sceNetCtlInetGetState](https://docs.vitasdk.org/group__SceNetCtlUser.html) aproximadamente una vez por segundo. Si el estado no es conectado, cierra el socket anterior, pausa las emisiones y conserva sesión, secuencia y contadores. Una consulta fallida se trata de forma conservadora como falta de conexión; se conserva su retorno y errno se establece en cero porque no se obtuvo un detalle de socket para esa operación.

Cuando vuelve el estado conectado, crea un socket no bloqueante nuevo y reanuda sin otra pulsación de Cruz. También recrea el socket en el siguiente ciclo tras un fallo de envío aunque el sistema siga indicando conectado, para cubrir un socket que haya quedado inutilizable tras un corte o suspensión no observados.

Abrir un socket no acredita recuperación: los fallos consecutivos solo se reinician tras un envío aceptado localmente, y la entrega sigue necesitando observación del PC. No hay confirmaciones de recepción ni garantía de entrega UDP.

## Límites

| Condición | Acción |
|---|---|
| Desconectado durante 30 s desde la primera observación | Detener ensayo |
| Cinco fallos consecutivos de apertura/envío | Detener ensayo |
| 180 s desde inicio, incluidos periodos suspendidos si el reloj avanza | Detener ensayo |
| 60 intentos reales de envío | Terminar |
| Círculo / START | Parar / salir, sin reanudación automática posterior |

No se consumen intentos mientras se espera a la red o falla abrir el socket. Los fallos de apertura sí consumen el presupuesto de reintentos. `send_errors` de STT/2 sigue contando únicamente intentos de envío fallidos. Los códigos de consulta/apertura pueden por ello aparecer sin incremento de ese contador.

La aplicación no puede observar estados mientras esté suspendida; el límite de espera empieza cuando detecta la desconexión. El límite total evita ensayos indefinidos. Una vez detenido, solo Cruz inicia otro ensayo.

## Validación

Prueba C portable: arranque, corte y retorno sin nuevo inicio, fallo de socket con enlace conectado, restablecimiento del presupuesto tras envío correcto, cinco fallos de apertura/envío, límite exacto de 30 s incluso si conecta en ese instante, límite total y regresión del reloj. Se compila con advertencias como errores en CI; la compilación Vita comprueba además las APIs y enlace con SceNetCtl.

Prueba física pendiente: observar una pausa y recepción posterior **en la misma sesión**, sin pulsar Cruz ni cerrar la aplicación. Registrar secuencias, tiempos, diagnósticos y contadores; distinguir suspensión al entrar en Ajustes de la pérdida de radio. Un build correcto o abrir un socket no bastan para dar por superada la prueba.

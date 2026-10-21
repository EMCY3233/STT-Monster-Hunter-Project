# Límites durante suspensión — revisión 0.5

En el ensayo 0.4 hubo una pausa de recepción de 53,863822 s entre dos muestras cuyo uptime solo avanzó 8049 ms. El reloj del proceso no podía usarse solo para acreditar límites de tiempo transcurrido durante esa intervención.

## Diseño

Al iniciar con Cruz se guardan el reloj del proceso y el tick RTC; la resolución se consulta mediante sceRtcGetTickResolution. Las APIs RTC están declaradas en la [cabecera oficial](https://github.com/vitasdk/vita-headers/blob/master/include/psp2/rtc.h).

Durante un ensayo, en cada vuelta de controles, se calcula el máximo de dos intervalos: proceso transcurrido y RTC transcurrido desde el inicio. Esa duración alimenta los límites de 30 s sin red observada y 180 s totales. El límite total se comprueba antes de operar con el socket, incluso en la primera vuelta al reanudar. Mientras el proceso está suspendido no puede ejecutar una parada; al volver debe comprobar el plazo antes de transmitir otra vez.

La pantalla muestra «Tiempo de limite: N / 180 s». `uptime_ms` de STT/2 sigue siendo tiempo del proceso: no cambia el contrato ni se confunde con este presupuesto. No se introduce una nueva versión de protocolo ni se informa del fallo de reloj como si fuera un error de red.

## Fallos y ajustes del reloj

- RTC sin lectura válida, resolución cero o retroceso de cualquiera de los relojes: parada por reloj no fiable. Requiere nuevo Cruz para crear otro ensayo.
- RTC avanza mucho: puede disparar el límite antes de tiempo; se prefiere detener a prolongar el ensayo.
- La conversión de ticks se hace por cociente/resto y se satura por encima de 181 s, evitando desbordamiento ante saltos grandes.
- Si el RTC no avanzase durante suspensión y el proceso tampoco, esta solución no podría medir ese periodo. Por eso la API y el build no bastan: se requiere prueba física del avance y del límite al reanudar.

No se cambia la fecha/hora de la consola, no se sincroniza contra Internet y no se alteran perfiles, firmware o plugins. El RTC puede ajustarse: el mecanismo es una comprobación conservadora, no una promesa de reloj monotónico perfecto.

## Validación

Pruebas C de reloj+política: RTC avanza mientras proceso se pausa, límite total exacto de 180 s, espera sin red de 30 s, RTC detenido con proceso activo, saltos enormes, retrocesos, lectura fallida, resolución cero, ticks fraccionarios y resolución máxima. Sin hardware ni esperas reales en esas pruebas.

Pendiente en Vita: dejar Wi-Fi activado, iniciar ensayo, suspender brevemente, reanudar y comparar «Tiempo de limite» con el tiempo externo. Después suspender más de 180 s desde el inicio y comprobar al volver que no se transmite otro mensaje de esa sesión. Esa prueba debe separar el efecto de suspensión del corte manual de radio. Círculo/START permanecen como parada/salida.

# MH4U: sondeo antes/después de una pulsación — 22-10-2026

## Resultado

Se completaron doce lecturas RPC válidas: dos rangos por muestra, tres muestras antes y tres después. Ambos rangos fueron estables y coincidieron con su backing estático en las seis muestras. No se observaron diferencias de bytes.

**No se confirmó la aceptación de la entrada por el juego.** El control nativo devolvió éxito para una sola pulsación `a`, pero las capturas anterior, inmediata posterior y posterior de comprobación seguían mostrando `Formatting complete.`. La configuración del perfil vincula A emulado a teclado, código 65. Esa configuración y el éxito de la llamada no prueban que el juego registrara el botón. No se hicieron más pulsaciones para forzar un cambio.

| Rango | Dirección virtual | Bytes | Offset en .code | Estabilidad antes/después | Coincide con backing |
| --- | --- | --- | --- | --- | --- |
| Control de código | 0x00100000 | 4 | 0 | Sí / sí | 6/6 |
| Candidato de datos | 15466496 | 32 | 14417920 | Sí / sí | 6/6 |

El candidato se eligió **antes de medir** como los primeros 32 bytes del segmento de datos respaldado por archivo, según el ExHeader previamente analizado. No es una estructura de animación, hitboxes o IA identificada. Un rango inicializado estable no permite concluir que el resto de memoria sea invariable. No hubo escaneo ni ampliación del rango tras el resultado negativo.

## Protocolo y trazabilidad

Protocolo privado fijado antes de la primera lectura: tres muestras por fase, intervalo de espera de 0,3 segundos entre muestras, dos solicitudes ReadMemory por muestra, sin WriteMemory. Las lecturas son secuenciales y no atómicas entre rangos. Se usó el mismo lector RPC ya probado; se ejecutó en el anfitrión autorizado porque la etapa anterior identificó timeouts desde el sandbox. No se alteró el cortafuegos.

El marcador registra el intervalo de la llamada de entrada en reloj UTC del anfitrión, no el instante de un frame emulado. La pulsación ocurrió entre `2026-10-21T23:14:18.905Z` y `2026-10-21T23:14:19.327Z`, es decir, el 22 de octubre en Madrid. Las muestras no capturan de forma continua el intervalo de la acción: un cambio transitorio entre fases podría no aparecer.

La comparación revalidó el hash completo del derivado `.code`: `63940d7ef1fecc119f9fb820f5f6a2cf2f2a5549e4a70f00319fbd6c9c1ad8dc`. No se volvió a hashear la imagen original de 4 GiB ni se afirma su reverificación completa. Muestras binarias (216 bytes en total), configuración, marcador y recibos permanecen privados en `analysis-local/citra-transition-20261022`. No se publican valores de memoria ni capturas.

La evidencia JSON enlaza hashes del protocolo, del marcador, de los recibos antes/después y de la comparación. La comparación consiste en igualdad de bytes por rango e índices de diferencias entre la última muestra anterior y la primera posterior; no interpreta tipos ni instrucciones. Este ensayo no requirió modificar el lector ni repetir sus cinco pruebas sintéticas.

## Reproducción y siguiente aceptación

Para esta misma compilación y perfil: comprobar la pantalla y el mapeo de botones; tomar tres lecturas de cada rango con el lector RPC, registrar un intervalo de entrada, observar el resultado visual y repetir exactamente los dos rangos. Conservar los bytes solo en privado para contrastarlos con los offsets estáticos indicados. No tratar una entrada enviada como una acción aceptada sin evidencia de pantalla o estado.

La siguiente aceptación debe confirmar primero una entrada reconocida por el juego (foco y duración, o una pulsación manual delimitada). Después conviene seleccionar un rango mediante referencias de código a estado mutable, sin atribuir significados a diferencias aisladas. Este resultado es negativo para el candidato y **no concluyente sobre una transición**, no una validación de datos de combate. Citra se dejó abierto; no queda un observador ejecutándose.

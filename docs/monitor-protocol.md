# STT Vita Monitor — arquitectura y STT/1–STT/2

Flujo: emisor simulado STT/1 o aplicación Vita independiente 0.5 STT/2 → UDP IPv4 → receptor Python en Windows → JSONL. El receptor no envía respuestas ni comandos. No hay descubrimiento automático, administración remota ni lectura de procesos.

## Contrato de transporte

Un objeto JSON UTF-8 por datagrama, máximo 1024 bytes, puerto por defecto 32100. No se fragmentan mensajes en la aplicación. Se rechazan mensajes inválidos, claves duplicadas, campos adicionales y versiones desconocidas. Un cambio incompatible requiere una nueva versión y soporte explícito.

| Campo | STT/1 |
|---|---|
| version | entero exacto 1 |
| session | 1–64 caracteres ASCII alfanuméricos, `_` o `-`; nuevo por arranque |
| source | `simulator` o `vita`; etiqueta declarada, no autenticación |
| seq | entero 0..2^53−1, incrementar por emisión |
| uptime_ms | entero 0..2^53−1, tiempo monotónico desde inicio del emisor |
| battery_pct | número finito 0..100 o null si no disponible |

Ejemplo: `{"version":1,"session":"demo","source":"simulator","seq":0,"uptime_ms":0,"battery_pct":75}`.

El receptor añade `received_at` (UTC), `peer_ip` y `packet`. UDP puede perder, duplicar o reordenar mensajes: se conservan las secuencias tal como llegan, sin deduplicar ni calcular pérdidas automáticamente. La hora de llegada no mide latencia sin sincronización de relojes. Una sesión distinta distingue reinicios; no existe estado persistente de sesiones en el receptor.

## Límites y operación

Escucha por defecto en 127.0.0.1. Las pruebas Vita autorizadas seleccionaron explícitamente la IP privada del PC con `--bind`; los resultados se registran por versión en el changelog. No abrir puertos en el router ni exponerlo a Internet. STT/1 no tiene cifrado ni autenticación: IP y `source` no prueban identidad. No mandar secretos o datos personales. En una LAN cualquier emisor alcanzable puede inyectar muestras.

El receptor mantiene memoria acotada y descarga cada registro al archivo. No hay rotación; el receptor tiene cuota por defecto de 10 MiB por archivo, incluido contenido existente, configurable con `--max-bytes`. Se detiene antes de excederla sin truncar registros. `--max-packets` limita muestras válidas; la inactividad cuenta desde la última muestra válida. Los paquetes inválidos no prolongan ese plazo. `--duration` puede limitar el tiempo total incluso con tráfico continuo. [Límites y estadísticas parciales](monitor-pc-compatibility.md). Los fallos de disco o enlace de socket detienen el proceso con error, salvo datagramas demasiado grandes, que se descartan. No se han medido rendimiento sostenido, consumo Vita ni resistencia a tráfico hostil.

Decisión inicial: 1 muestra/segundo, solo estado del propio agente. FPS, RAM global, temperaturas, trazas del kernel y telemetría de otros juegos quedan fuera del contrato hasta verificar APIs y viabilidad. Una aplicación independiente no demuestra monitorización concurrente de un juego.

## STT/2 — diagnósticos de red

Conserva todos los campos base con version=2 y añade exactamente un objeto `diagnostics`:

| Campo | Significado |
|---|---|
| send_ok | Envíos aceptados localmente antes del intento actual |
| send_errors | Fallos de envío antes del intento actual |
| last_result | Último retorno de error de envío/apertura de socket o consulta de estado, entero con signo de 32 bits |
| net_errno | Detalle de sceNetErrnoLoc capturado al fallar un socket; cero si no aplica a la operación, entero con signo de 32 bits |

Los contadores son enteros no negativos y su suma debe igualar seq. La muestra se codifica **antes** del envío actual, por lo que no puede informar de su propio resultado. Se rechazan campos desconocidos, booleanos como contadores y valores fuera de rango. Para mostrar un código firmado en hexadecimal, usar su representación de 32 bits (`value & 0xffffffff`).

El último error y su detalle persisten durante la vida de la aplicación, incluso al iniciar otra sesión con Cruz; los contadores y seq se reinician por sesión. Cero significa que todavía no se ha capturado error. Un retorno correcto posterior no borra la evidencia anterior. El detalle de errno es información del sistema, no una causa validada automáticamente.

El receptor nuevo acepta STT/1 y STT/2; un receptor anterior a esta ampliación rechaza STT/2. El simulador existente sigue emitiendo STT/1. Las pruebas C generan muestras de ambas versiones para verificar compatibilidad.

En 0.4, esperar red o fallar al abrir un socket no consume seq ni contadores de envío. La sesión se conserva al recuperar conexión automáticamente; uptime_ms puede saltar aunque las secuencias sean consecutivas. Ver [política y límites](auto-recovery.md). El detalle cero no demuestra ausencia de error si last_result indica fallo de una operación sin errno aplicable.

No hay canal alternativo ni archivo de errores en Vita: sin conectividad no se pueden enviar diagnósticos. El error más reciente puede viajar en una muestra posterior que sí llegue, incluso tras iniciar manualmente otra sesión. Si se cierra la aplicación antes, ese estado en RAM se pierde. No se garantiza un informe de cada fallo ni del último intento de una sesión si no hay otro envío posterior. El analizador expone `diagnostics_latest` de la secuencia diagnóstica más alta recibida por sesión.

# STT Vita Monitor — arquitectura y STT/1

Flujo: emisor simulado (hoy) o aplicación Vita independiente (futuro) → UDP IPv4 → receptor Python en Windows → JSONL. El receptor no envía respuestas ni comandos. No hay descubrimiento automático, administración remota ni lectura de procesos.

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

Escucha por defecto en 127.0.0.1. Para una futura prueba Vita habrá que seleccionar explícitamente la IP privada del PC con `--bind` y autorizar primero la prueba física. No abrir puertos en el router ni exponerlo a Internet. STT/1 no tiene cifrado ni autenticación: IP y `source` no prueban identidad. No mandar secretos o datos personales. En una LAN cualquier emisor alcanzable puede inyectar muestras.

El receptor mantiene memoria acotada y descarga cada registro al archivo. No hay rotación ni límite de almacenamiento automático. `--max-packets` limita muestras válidas; la inactividad cuenta desde la última muestra válida. Los paquetes inválidos no prolongan ese plazo. Los fallos de disco o enlace de socket detienen el proceso con error, salvo datagramas demasiado grandes, que se descartan. No se han medido rendimiento sostenido, consumo Vita ni resistencia a tráfico hostil.

Decisión inicial: 1 muestra/segundo, solo estado del propio agente. FPS, RAM global, temperaturas, trazas del kernel y telemetría de otros juegos quedan fuera del contrato hasta verificar APIs y viabilidad. Una aplicación independiente no demuestra monitorización concurrente de un juego.

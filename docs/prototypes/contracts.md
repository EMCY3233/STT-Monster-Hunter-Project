# STT — contratos iniciales 2026-10-21

Base revalidada: main `410b1dd70a3713b500a829aed55cb99cb74ad1d0`.
PR3 `647bae400974a78af5b2e7e709ed6ea87682d7ab` y PR7
`3bdce7d6d1cfcda0314fd372a0f1ce8ea7a85441` seguían abiertas como borradores.
AGENTS.md leído antes de editar. Ninguna rama de investigación se modifica.

## STT/3, payload play versión 1

STT/1 y STT/2 conservan su estructura y validación. STT/3 es una ampliación
explícita: receptores antiguos lo rechazan. El receptor nuevo acepta las tres
versiones y conserva JSONL; el analizador existente resume sesiones/secuencias,
no calcula estadísticas de combate. Emisor y origen son declaraciones, no autenticación.

Un objeto JSON UTF-8 por datagrama, máximo 1024 bytes, sin fragmentación,
puerto 32100 del receptor existente. Campos desconocidos, duplicados, números
no enteros y valores fuera de límites se rechazan. `battery_pct` es entero 0–100
o null en STT/3; /1 y /2 siguen admitiendo números finitos.

| Campo | Contrato |
|---|---|
| version | 3 |
| session | 1–64 ASCII alfanuméricos, guion o subrayado; nueva por arranque |
| source | vita o simulator; plataforma declarada |
| seq | 0..2^53−1; incremento por muestra emitida |
| uptime_ms | reloj monotónico del emisor, milisegundos |
| play.version | 1 |
| play.tick | tick lógico 60 Hz, no hora de pared |
| play.origin | original-prototype; no recursos ni fidelidad comercial |
| play.hunter | state, pos_mm[3], yaw_mdeg, hp |
| play.camera | yaw_mdeg, pitch_mdeg, distance_mm |
| play.attack | id (0 sin ataque), phase_tick |
| play.hits | 0–2 eventos {attack,target,damage,hp}, IDs positivos |
| play.perf | frame_us, update_us, dropped |
| play.aquatic | null obligatorio; extensión futura reservada |

Sistema local diestro de escena: +Y arriba, +Z hacia delante, +X derecha.
Yaw positivo gira de +Z hacia +X visto desde arriba (convención de rumbo,
independiente de matrices de render). Posiciones enteras en mm, límites ±100 km.
Ángulos de rumbo en miligrados [-180000,180000]; pitch [-89000,89000],
positivo eleva la cámara; distancia 1..1000000 mm. HP/daño enteros 0..1000000.
Estados de cazador: idle, move, windup, active, recovery, stunned.
Attack/target uint32; phase_tick 0..65535. Frame/update 0..10000000 us;
dropped uint32 saturado. Los consumidores no infieren rendimiento global de Vita.

Un ataque/objetivo aparece como máximo una vez en cada lista; la deduplicación
real durante el ataque es responsabilidad del Combat Lab, no del transporte.
Eventos son efímeros: UDP y el buzón pueden perderlos. Esto no es un registro
de combate autoritativo. La muestra indica HP posterior al impacto.

`SttPlayMailbox` guarda una muestra, sobrescribe sin esperar, contabiliza pérdidas
saturadas y no asigna memoria. Uso de un solo hilo; session es un puntero prestado
que debe permanecer válido hasta extraer/codificar. La codificación es acotada,
sin red ni archivos. El primer corte puede trabajar completamente offline:
no se añade envío UDP al bucle jugable ni se afirma recepción desde Vita.
Futuro adaptador: máximo 10 muestras/s, un intento no bloqueante por vencimiento,
sin reintentos dentro del frame; descartar ante socket ocupado. No implementar
esa política no debe presentarse como transporte Vita ya validado.

HUD puede leer directamente la misma instantánea local sin depender del receptor.
Aquatic Lab deberá negociar una nueva versión para medio, profundidad en mm y
orientación 3D; null no declara natación implementada.

## Validación y ejecución

```
python -m unittest discover -s tests -v
cc -std=c99 -Wall -Wextra -Werror -Icontracts contracts/stt_play.c contracts/tests/encode.c -o /tmp/stt-play-test
/tmp/stt-play-test
python -m stt_monitor.receiver --bind 127.0.0.1 --max-packets 2 --output play.jsonl
```

Ejemplos originales sintéticos: `contracts/examples/snapshot.json` y `hit.json`.
Pruebas cruzadas compilan el encoder C, decodifican sus dos salidas en Python y
comprueban igualdad binaria al recodificar. Se prueban truncamiento, IDs de
impacto duplicados, campos malformados y compatibilidad /1 /2. No prueba física.
CI PC existente ejecuta la suite nueva en Windows/Linux; el cruce C se omite si
no hay `cc`, y debe constar el resultado concreto del job.

Dependencias: Python stdlib 3.11+, compilador C99; sin descarga de paquetes.
No se crean claves, herramientas ni datos comerciales. No se cambian firewall,
consola, firmware, montajes, plugins ni monitor instalado.

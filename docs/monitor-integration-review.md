# Revisión de integración del monitor PC — 2026-10-21

Revisión estática y de evidencia CI: #13 → #14 → #16 → #18 → #19, todas abiertas y sin fusionar al revisar. No se ejecutó ninguna fusión ni se repitieron pruebas aprobadas. Este informe no representa una prueba física nueva.

## Bases y heads exactos

| PR | Base/ref | Base SHA | Head/ref | Head SHA |
|---|---|---|---|---|
| #13 | main | fa32a1fe49e3b3ab67bf6860730dd44250f8300a | feat/monitor-live-diagnostics | d112214eb8f4515bbee5a946b50942b27a08e484 |
| #14 | feat/monitor-live-diagnostics | d112214eb8f4515bbee5a946b50942b27a08e484 | feat/monitor-reception-timing | e702126354b2f6214ec3342a2f89498c203e97f9 |
| #16 | feat/monitor-reception-timing | e702126354b2f6214ec3342a2f89498c203e97f9 | test/monitor-combined-capture | 79a896967594b89a9d9b71f15b0e30b78c627487 |
| #18 | test/monitor-combined-capture | 79a896967594b89a9d9b71f15b0e30b78c627487 | feat/monitor-resource-limits | 208a5d74c34d60cd18395ebbb92c874c7d96f0fb |
| #19 | feat/monitor-resource-limits | 208a5d74c34d60cd18395ebbb92c874c7d96f0fb | fix/monitor-incomplete-append | 89f99b2ffd5cd3acb6762d41366404ed5f3942ae |

Verificadas las cinco relaciones de ascendencia con Git, todas correctas. El diff de main al head #19 no modifica stt_monitor/protocol.py, stt_monitor/simulator.py ni vita-agent. El agente instalado sigue en 0.5; no requiere VPK nuevo.

## Matriz final

| Superficie | Compatibilidad | Atención al integrar |
|---|---|---|
| STT/1–STT/2 | Validación, esquema, puerto y tamaño de datagrama sin cambios | Simulador STT/1, agente 0.5 STT/2; source no autentica hardware |
| Receptor CLI | Conserva opciones previas; --live es opcional | Nuevo default: cuota total de 10 MiB; destino no vacío sin LF final devuelve error 2 antes de socket |
| stdout receptor | accepted/rejected conservados | --live añade líneas; cuota añade stop_reason, bytes_written y not_recorded. No confundir muestra no guardada con fallo de envío de Vita |
| JSONL | Mismo sobre received_at/peer_ip/packet | Registros nuevos UTF-8/LF; CRLF previo conservado. No se repara ni valida todo el historial |
| Analizador CLI/API | Conteos anteriores para registros incluidos | Campos nuevos: reception_timing, partial, stop_reason, processed_packets, limits; consumidores de JSON deben tolerar extensión |
| Cuotas de análisis | 1000 sesiones/100000 secuencias únicas globales, configurables | Resultado parcial explícito al primer registro que excedería estado; resto sin examinar |
| Entrada inválida | Rechazos UDP y líneas inválidas contados | Lectura CLI acotada: más de 4096 bytes o UTF-8 inválido cuenta como línea inválida, no como pérdida de red |
| Tiempo | Duración PC monotónica; intervalos observados en UTC | STT/2 no transmite parada ni presupuesto RTC. Pausa no demuestra suspensión por sí sola |
| Recursos | Archivo, cardinalidad y tamaño por línea acotados | Sin máximo RAM medido, rotación, bloqueo de escritores externos ni plazo duro si disco/stdout bloquea |

## Suite vigente

[Monitor tests del head #19](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39678695059): cuatro jobs correctos, Windows/Linux con Python 3.11/3.13. Cada uno ejecutó unittest (26 pruebas), smoke_cli, smoke_diagnostics y smoke_limits correctamente. [Vita agent build](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39678695146) correcto; el código Vita no cambió. Las ejecuciones anteriores correctas están en las descripciones de sus PR.

En esta revisión no apareció otra regresión ejecutable concreta. Se corrigieron textos: excepción de archivo vacío al comprobar LF, cuota como tamaño total y nombre exacto del ensayo descrito. No se repite la suite por esos ajustes documentales; no se certifica ausencia universal de fallos.

## Ejemplo local

En dos terminales desde la raíz del repositorio, con destino nuevo o vacío/terminado en LF:

```powershell
python -m stt_monitor.receiver --live --output telemetry-review.jsonl --duration 30 --idle-timeout 5 --max-packets 10 --max-bytes 10485760
```

```powershell
python -m stt_monitor.simulator --count 10 --interval 0.1
```

Después, sin modificar la captura:

```powershell
python -m stt_monitor.analyze telemetry-review.jsonl --max-sessions 1000 --max-unique 100000
```

Comprobar partial e invalid_lines. Con archivo nuevo y ese emisor se esperan diez muestras simuladas. Son ejemplos revisados; las ejecuciones reproducibles aprobadas están en CI y en la [matriz de pruebas](monitor-pc-compatibility.md).

## Orden propuesto, sin ejecutar

1. Obtener autorización específica para fusionar y comprobar heads, main y CI actuales.
2. Integrar #13 en main preservando ascendencia. Retargetear #14 a main y comprobar que su diff solo contiene su mejora; validar el nuevo estado antes de integrarla.
3. Repetir con #16, #18 y #19 en ese orden. Tras cada cambio de base, revisar diff/CI/estado de fusión y sincronizar sin sobrescribir cambios locales.
4. Integrar después este cierre documental, retargeteado a main y contrastado con el estado real.

Squash/rebase puede exigir reconstruir explícitamente dependencias para evitar diffs repetidos: no hacerlo automáticamente. Este plan no autoriza fusiones. La autorización concedida en este chat solo permite publicar esta PR documental.

## Bloqueos y pendientes

La integración espera autorización específica de fusión; no hay fallo CI activo en los heads revisados. Pendientes físicos: límite de 30 s sin red durante suspensión y fallos/retrocesos RTC. Pruebas sintéticas y compilación no los sustituyen. Sin instalación, FTP, consola, banco, originales ni cambios STT/3 en esta revisión.

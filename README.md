# Start The Travesy, Monster Hunter

**Estado vigente y coordinación:** [estado consolidado](docs/PROJECT_STATUS.md) y [sincronización de frentes](docs/research/game-inputs-2026-10-21/synchronization.md). Monitor0.5 está en main; esta rama documental conserva material de etapas anteriores. Banco general sin clasificación por armas. Copia Frontier Vita terminada y registrada:8261archivos añadidos,banco9888. [Censo final](docs/research/game-inputs-2026-10-21/frontier-complete.md). No se declara descifrado ni jugabilidad. Las PR3/7 abiertas no equivalen a integración en main.

Base inicial de investigación y desarrollo. No existe todavía un juego nativo ni una conversión demostrada. El componente ejecutable es **STT Vita Monitor**: receptor y generador simulado para Windows con Python 3.11 o posterior, y agente Vita independiente **0.5**. El receptor acepta STT/1 y STT/2; el simulador emite STT/1 y el agente actual STT/2. La [recuperación de red en 0.4](docs/STT-MON-006-auto-result.md) y la [parada tras suspensión en 0.5](docs/STT-MON-008-suspend-result.md) tienen resultados físicos documentados; siguen pendientes pruebas físicas del límite sin red durante suspensión y de fallos/retrocesos del reloj. No monitoriza otros juegos.

## Prueba en Windows (dos terminales en esta carpeta)

```powershell
python -m stt_monitor.receiver --max-packets 10 --idle-timeout 30
```

```powershell
python -m stt_monitor.simulator --count 10
```

El receptor añade líneas a `telemetry.jsonl` sin truncar el archivo. Si un archivo existente no vacío no termina en LF, el CLI se detiene antes de abrir el socket y pide otra ruta `--output`; no repara ni concatena una nueva muestra a la línea incompleta. Cada muestra está marcada `source=simulator`. Resumen esperado: 10 aceptadas, 0 rechazadas. El límite por inactividad permite finalizar si desaparece el emisor; Ctrl+C también detiene el receptor. El archivo tiene por defecto una cuota total de 10 MiB, incluido su contenido previo; `--max-bytes` permite cambiarla. Al alcanzarla se detiene sin truncar.

```powershell
python -m unittest discover -s tests -v
```

El monitor PC no tiene dependencias de terceros. Si Windows abre Microsoft Store al invocar `python`, instalar/configurar Python o usar su ruta completa.

## Ver diagnósticos en directo

Añadir `--live` al receptor muestra cada muestra recibida, sesión, batería y diagnóstico STT/2. Por ejemplo, para simulación local:

```powershell
python -m stt_monitor.receiver --live --max-packets 10 --idle-timeout 30
```

El archivo JSONL conserva el mismo formato y sigue añadiendo registros. Los contadores describen intentos anteriores al mensaje actual; «último error conservado» puede pertenecer a una sesión previa. Una recepción no confirma el resultado del envío actual. STT/1 no aporta diagnóstico. La falta de mensajes no demuestra desconexión ni parada: STT/2 no transmite el estado de parada ni el presupuesto RTC. Esta vista no necesita actualizar el VPK.

Para acotar también un flujo continuo, añadir `--duration 180`: el plazo total usa el reloj monotónico del PC y no se reinicia con cada muestra. Se aplica el primer límite alcanzado entre duración, inactividad y máximo de muestras. No cambia el plazo de la Vita. La cuota independiente `--max-bytes` limita el tamaño total del archivo, incluido su contenido previo. [Compatibilidad, límites y ensayo conjunto](docs/monitor-pc-compatibility.md).

## Analizar una captura

```powershell
python -m stt_monitor.analyze telemetry.jsonl
```

Produce un resumen por IP, origen declarado y sesión: muestras, duplicados, llegadas fuera de orden y números ausentes entre el mínimo y el máximo observados. Los huecos no demuestran pérdidas en la red: la captura puede ser parcial. No cuenta como perdidos los mensajes anteriores al primero o posteriores al último recibido. La etiqueta de origen no autentica un dispositivo. El analizador limita por defecto el estado a 1000 sesiones y 100000 secuencias únicas globales, ajustables con `--max-sessions` y `--max-unique`. Si el siguiente registro excedería un límite, se detiene antes de incluirlo y devuelve `partial=true` y `stop_reason`; las estadísticas describen solo el prefijo procesado. La lectura CLI está acotada a líneas de 4096 bytes; líneas mayores o UTF-8 inválido cuentan como inválidas.

El resumen también incluye `reception_timing`: primeras/últimas horas válidas en orden de archivo, normalizadas a UTC, número de horas ausentes/inválidas, retrocesos del reloj del PC y mayor intervalo observado por sesión. `largest_gap` conserva secuencias y diferencia de `uptime_ms` de las dos muestras comparadas. Un timestamp sin zona, ausente o inválido interrumpe la comparación temporal de esa sesión, sin descartar su paquete. Un retroceso se cuenta y no se considera un intervalo positivo. Los mensajes duplicados o desordenados siguen siendo observaciones: una diferencia negativa de uptime no demuestra fallo del reloj del agente. Estos intervalos no identifican por sí solos suspensión, latencia ni causa de un corte. STT y JSONL no cambian; se añaden campos al informe del analizador.

## Estado actual

- [Estado consolidado, decisiones y próximos pasos](docs/PROJECT_STATUS.md)
- [Banco de recursos e inventarios con SHA-256](docs/research/game-inputs-2026-10-21/README.md)
- [Planificación histórica Frontier e interfaces](docs/research/frontier-classic/README.md)

Los archivos comerciales permanecen fuera del repositorio. El inventario distingue metadatos observados de autenticidad o compatibilidad no demostradas. La copia Frontier PCSG00350 está identificada por SFO y registrada; el acceso estructural no acredita descifrado global ni jugabilidad.

## Documentación

- [Áreas 01–10](docs/areas/README.md)
- [Arquitectura y protocolos STT/1–STT/2](docs/monitor-protocol.md)
- [Plan STT-MON-001 y resultados](docs/STT-MON-001.md)
- [Agente Vita experimental y compilación](vita-agent/README.md)
- [Revisión y orden propuesto de integración del monitor PC](docs/monitor-integration-review.md)
- [Changelog maestro](CHANGELOG_MASTER.md)

La conexión FTP y las características del hardware proceden de confirmación del usuario. El agente 0.5 fue transferido e instalado con autorización y hash verificado; las pruebas y la retirada de las excepciones temporales de firewall están documentadas. No incluye recursos de juegos, firmware ni plugins. El workflow del agente prepara un VPK experimental para revisión; no lo instala ni transfiere.

# Start The Travesy, Monster Hunter

Base inicial de investigación y desarrollo. No existe todavía un juego nativo ni una conversión demostrada. El componente ejecutable es **STT Vita Monitor**: receptor y generador simulado para Windows con Python 3.11 o posterior, y agente Vita independiente **0.5**. El receptor acepta STT/1 y STT/2; el simulador emite STT/1 y el agente actual STT/2. La [recuperación de red en 0.4](docs/STT-MON-006-auto-result.md) y la [parada tras suspensión en 0.5](docs/STT-MON-008-suspend-result.md) tienen resultados físicos documentados; siguen pendientes pruebas físicas del límite sin red durante suspensión y de fallos/retrocesos del reloj. No monitoriza otros juegos.

## Prueba en Windows (dos terminales en esta carpeta)

```powershell
python -m stt_monitor.receiver --max-packets 10 --idle-timeout 30
```

```powershell
python -m stt_monitor.simulator --count 10
```

El receptor añade líneas a `telemetry.jsonl` sin truncar el archivo. Cada muestra está marcada `source=simulator`. Resumen esperado: 10 aceptadas, 0 rechazadas. El límite por inactividad permite finalizar si desaparece el emisor; Ctrl+C también detiene el receptor. El registro puede crecer: limitar la duración y archivar manualmente las sesiones.

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

## Analizar una captura

```powershell
python -m stt_monitor.analyze telemetry.jsonl
```

Produce un resumen por IP, origen declarado y sesión: muestras, duplicados, llegadas fuera de orden y números ausentes entre el mínimo y el máximo observados. Los huecos no demuestran pérdidas en la red: la captura puede ser parcial. No cuenta como perdidos los mensajes anteriores al primero o posteriores al último recibido. La etiqueta de origen no autentica un dispositivo. El analizador guarda en memoria las secuencias únicas; usar capturas acotadas.

## Documentación

- [Áreas 01–10](docs/areas/README.md)
- [Arquitectura y protocolos STT/1–STT/2](docs/monitor-protocol.md)
- [Plan STT-MON-001 y resultados](docs/STT-MON-001.md)
- [Agente Vita experimental y compilación](vita-agent/README.md)
- [Changelog maestro](CHANGELOG_MASTER.md)

La conexión FTP y las características del hardware proceden de confirmación del usuario. El agente 0.5 fue transferido e instalado con autorización y hash verificado; las pruebas y la retirada de las excepciones temporales de firewall están documentadas. No incluye recursos de juegos, firmware ni plugins. El workflow del agente prepara un VPK experimental para revisión; no lo instala ni transfiere.

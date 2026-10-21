# Start The Travesy, Monster Hunter

Base inicial de investigación y desarrollo. No existe todavía un juego nativo ni una conversión demostrada. El primer componente ejecutable es **STT Vita Monitor 0.1**, receptor de telemetría para Windows y generador simulado, escrito con la biblioteca estándar de Python 3.11 o posterior.

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

## Analizar una captura

```powershell
python -m stt_monitor.analyze telemetry.jsonl
```

Produce un resumen por IP, origen declarado y sesión: muestras, duplicados, llegadas fuera de orden y números ausentes entre el mínimo y el máximo observados. Los huecos no demuestran pérdidas en la red: la captura puede ser parcial. No cuenta como perdidos los mensajes anteriores al primero o posteriores al último recibido. La etiqueta de origen no autentica un dispositivo. El analizador guarda en memoria las secuencias únicas; usar capturas acotadas.

## Documentación

- [Áreas 01–10](docs/areas/README.md)
- [Arquitectura y protocolo STT/1](docs/monitor-protocol.md)
- [Plan STT-MON-001 y resultados](docs/STT-MON-001.md)
- [Agente Vita experimental y compilación](vita-agent/README.md)
- [Changelog maestro](CHANGELOG_MASTER.md)

La conexión FTP y las características del hardware proceden de confirmación del usuario. Esta entrega no accede a la consola ni utiliza WinSCP. No incluye recursos de juegos, firmware ni plugins. El workflow del agente prepara un VPK experimental para revisión; no lo instala ni transfiere.

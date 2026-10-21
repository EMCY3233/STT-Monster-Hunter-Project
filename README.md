# Start The Travesy, Monster Hunter

**Estado vigente y coordinación:** [estado consolidado](docs/PROJECT_STATUS.md) y [sincronización de frentes](docs/research/game-inputs-2026-10-21/synchronization.md). Monitor0.5 está en main; esta rama documental conserva material de etapas anteriores. Banco general sin clasificación por armas. Copia Frontier Vita en curso, sin declarar cierre ni descifrado. Las PR3/7 abiertas no equivalen a integración en main.

Base inicial de investigación y desarrollo. No existe todavía un juego nativo ni una conversión demostrada. El monitor PC incluye receptor de telemetría y generador simulado en Python 3.11 o posterior. El agente Vita experimental está en la versión 0.2: hay un ensayo de telemetría anterior documentado y confirmación visual del usuario para 0.2; las pruebas físicas restantes siguen pendientes.

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

## Estado actual

- [Estado consolidado, decisiones y próximos pasos](docs/PROJECT_STATUS.md)
- [Inventario de siete archivos locales y SHA-256](docs/research/game-inputs-2026-10-21/README.md)
- [Catálogo Frontier, propuesta de fusión e interfaces](docs/research/frontier-classic/README.md)

Los archivos comerciales permanecen fuera del repositorio. El inventario distingue metadatos observados de autenticidad o compatibilidad no demostradas. No hay Frontier identificado entre las entradas locales.

## Documentación

- [Áreas 01–10](docs/areas/README.md)
- [Arquitectura y protocolo STT/1](docs/monitor-protocol.md)
- [Plan STT-MON-001 y resultados](docs/STT-MON-001.md)
- [Agente Vita experimental y compilación](vita-agent/README.md)
- [Changelog maestro](CHANGELOG_MASTER.md)

La conexión FTP y las características del hardware proceden de confirmación del usuario. Esta entrega no accede a la consola ni utiliza WinSCP. No incluye recursos de juegos, firmware ni plugins. El workflow del agente prepara un VPK experimental para revisión; no lo instala ni transfiere.

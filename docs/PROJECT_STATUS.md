# Estado consolidado — Start The Travesy, Monster Hunter

Actualización: 21-10-2026, Europe/Madrid. La fecha identifica esta revisión documental, no un nuevo ensayo físico.

## Hechos y evidencia

- Monitor PC con receptor, simulador y analizador; agente Vita experimental 0.2. [Registro físico](STT-MON-001-hardware-result.md) y [changelog](../CHANGELOG_MASTER.md) distinguen ensayo de telemetría previo y confirmación visual del usuario en 0.2.
- [Inventario local](research/game-inputs-2026-10-21/README.md): siete archivos, 7.861.039.260 bytes; SHA-256 idénticos en dos lecturas completas. MHFU identificado por SFO ULES01213 / 1.01; otros límites en la ficha.
- MH3U con flags de cifrado; MH4U/MHXX multipartes con CRC de cabeceras correcto, carga todavía no probada. MHGU es nombre de carpeta: no demuestra que sea la edición Switch.
- Sin archivos Frontier identificados. [Catálogo de Espada Larga](research/frontier-classic/01-catalogo.md): 13 registros trazables de investigación; movimientos y cifras históricas pendientes de fuente primaria accesible.
- CI de 1b68b5b: [pruebas](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39547319058) y [compilación](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39547319029) concluyeron success. Seis pruebas nuevas aprobadas localmente; hubo un fallo UDP preexistente local y no se ha demostrado su causa.

## Áreas 01–10

| Área | Situación documentada | Próximo paso |
|---|---|---|
| [01 Dirección](areas/01.md) | Selección de tres rasgos aprobada por el usuario; otras decisiones pendientes | Elegir revisión histórica canónica y criterios para prototipo |
| [02 Arquitectura](areas/02.md) | Inventario y revisión documental recibidos; no port demostrado | Probar íntegramente 7z e identificar código legible |
| [03 Combate](areas/03.md) | Contrato de estados, recursos e interrupciones propuesto | Resolver transiciones y parámetros antes de implementar |
| [04 Frontier](areas/04.md) | Catálogo inicial y fusión original; Extremo separado | Obtener fuentes primarias de Tierra/Cielo/Tormenta |
| [05 Natación](areas/05.md) | Interfaz tierra/agua revisada documentalmente | Diseñar y validar variante acuática aparte |
| [06 Monstruos e IA](areas/06.md) | Sin implementación verificada | Identificar procedencia de recursos y contrato de colisión |
| [07 Animación y gráficos](areas/07.md) | Ficha y comprobaciones propuestas; formatos sin confirmar | Clasificación estructural tras acceder a contenedores |
| [08 Controles](areas/08.md) | Entradas semánticas y perfil Vita candidato | Revisar conflictos con mapa completo y accesibilidad |
| [09 Misiones y economía](areas/09.md) | Planificación, sin nuevas funciones verificadas | Esperar formatos y decisiones de alcance |
| [10 Integración y pruebas](areas/10.md) | Pruebas automatizadas disponibles; físicos pendientes explícitos | Integridad de archivos y matriz de futuros prototipos |

## Decisiones de diseño, separadas de resultados

El usuario eligió corte de retirada (Tierra), corte evasivo (Cielo) y estocada perforante cargable (Tormenta). La [propuesta consolidada](research/frontier-classic/02-fusion.md) prepara carga vulnerable y ejecuta retirada oblicua con estocada en un gesto continuo. Evasión, coste, daño, tiempos y alcance quedan sin definir. No es un ataque histórico confirmado ni un sistema implementado.

Los [contratos 03/05/08](research/frontier-classic/03-interfaces.md) proponen consumo inicial atómico, cierre de ventanas al interrumpir, acción inicialmente terrestre y perfil R+Triángulo / mantener-soltar R para liberar el pulgar de cámara. Son propuestas para revisión, sin aprobación global de controles o balance.

## Siguiente secuencia de trabajo

1. Verificar carga comprimida de MH4U y MHXX; conservar originales.
2. Contrastar identidades internas de bases/parche y clasificación de ejecutables accesibles.
3. Identificar contenedores e índices antes de asignar modelos/animaciones a movimientos.
4. Completar evidencias primarias Frontier; no usar MHFU como sustituto.
5. Resolver interfaces y diseñar pruebas con recursos propios; separar Extremo.
6. Ensayos físicos pendientes del monitor solo en una tarea con autorización aplicable.

No hay juego nativo ni conversión demostrada. No se han publicado juegos, claves o recursos comerciales ni realizado transferencias/instalaciones Vita en este frente. El trabajo se conserva en [PR #3](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/3), independiente del monitor.

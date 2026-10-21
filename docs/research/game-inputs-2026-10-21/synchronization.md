# Sincronización del proyecto — 2026-10-21

Este registro coordina estados y propiedad de archivos. No iguala los contenidos de ramas con funciones distintas ni acredita implementaciones que solo se han encargado.

## Fuentes de verdad y responsables
| Frente | Espacio y rama | Estado comprobado |
|---|---|---|
| Monitor | repository; docs/monitor-status-sync-20261021 | main conserva410b1dd y Monitor0.5; correcciones documentales6200812 en PR12 abierta; árbol limpio en la revisión |
| Banco y documentación central | inventory-work; docs/game-input-inventory-20261021 | PR3 abierta; cambios locales propios y publicaciones por conector. El HEAD local no representa necesariamente el último commit remoto |
| Ingeniería inversa | research-work; research/stt-engineering-resources-20261021 | PR7 abierta; espacio mantenido por el otro chat. Es una carpeta de trabajo de publicación, no se exige que sea un checkout Git local |
| Prototipos | PR8contratos,PR9CombatLab,PR10AssetLab,PR11Vita3D | Primeras implementaciones publicadas,PR abiertas. Pruebas PC/compilación informadas por responsable; visual/físico pendientes,UDP no implementado |

Propietarios: este chat mantiene inventory-work, el banco y los recibos FTP; STTMH Investigacion e ingenieria inversa mantiene research-work/PR7; Desarrolla el prototipo STT Vita mantiene repository y pruebas de monitor. No cambiar archivos ni ramas de otros frentes.

## Banco y copia de Frontier

**Cierre verificado:** [copia y censo final de Frontier](frontier-complete.md):8261 archivos/5212490427bytes incorporados; banco actual9888archivos. BaseG1.00 y parcheZ01.99 confirmados, sin afirmar ZZ, descifrado o jugabilidad.

Estado actualizado: ambos procesos terminaron con código0,0.partial, integridadSQLiteok y hashes de catálogos cotejados. El cierre de investigación está recibido (PR7,commit097f64f). Las correcciones de monitor están publicadas en PR12 abierta, rama docs/monitor-status-sync-20261021,commit6200812; repository está en esa rama limpia. main mantiene410b1dd. Los párrafos de transferencia siguientes conservan el plan inicial; queda superado su estado «en curso».

Banco inicial verificado:1627 archivos físicos,21696 entradas ARC descomprimidas,8823 objetos únicos. Las cifras del banco inicial no incluyen todavía la copia de Vita.

Copia FTP de lectura finalizada: PCSG00350, carpetas app/patch/rePatch,8261 archivos y5212490427 bytes, con una licencia excluida. SFO base confirma FrontierG1.00 y SFO de parcheFrontierZ01.99. No se confirma ZZ. Los conteos provisionales anteriores fueron sustituidos por el censo completo estable. No iniciar otra copia, lectura FTP concurrente ni recatalogación del banco.

Fuente de estado: analysis-local/logs/vita-bank-status.json.
Cierre exige completed=true en vita-copy-PCSG00350.json, phase=complete y vita-registration.json válido. finish_vita_copy.py espera la copia completa y registra tras volver a comprobar hashes locales. La validación de flujo/local no es un hash calculado independientemente en Vita.

## Decisiones vigentes
- Banco y análisis de recursos generales, sin clasificar por armas ni buscar relaciones con Espada Larga.
- Catálogo y fusión anteriores son material histórico, no prioridad del banco actual.
- Prototipos con muestras propias pueden avanzar independientemente del análisis comercial. La propuesta e implementación STT/3 está en PR8; no se acredita interoperabilidad con el receptor MonitorSTT/1–STT/2. El VPK usa telemetría local; UDP pendiente.
- No adaptación comercial sin activos legales. No publicar juegos, recursos, licencias o claves.
- Copia FTP de lectura expresamente autorizada; ninguna instalación ni escritura en consola desde este frente.
- PR3 y PR7 abiertas no equivalen a integración en main. No fusionar automáticamente.
- Continuación en este chat cada15min hasta nuevo aviso: primero verifica descarga/banco y después continúa análisis/documentación en etapas. Avisa solo novedades significativas o bloqueos.

## Discrepancias corregidas y pendientes
Se sustituyen las afirmaciones vigentes antiguas «Monitor0.2», «sin Frontier local», «solo piloto ARC» y «modelos/animaciones sin localizar» por los estados documentados actuales. Los informes fechados de etapas anteriores se conservan como historia.

Las pruebas de hardware del monitor pertenecen al chat propietario; no repetir instalaciones por sincronizar documentos. La descarga no prueba descifrado ni semántica de formatos. Los ensayos Citra y ELF de investigación pertenecen a PR7 y se actualizan por ese propietario.

Monitor confirmó main local=GitHub, árbol limpio, STT/1+STT/2 en receptor, agente STT/2 y UDP32100. Detectó tres textos antiguos (README general, README del agente y descripción de PR6); su corrección documental se encargó al propietario, sin reinstalación ni fusión automática. Investigación remitió cierre en PR7; el estudio de formatos continúa con los candidatos del censo final. Inicio y entrega de prototipos confirmados por responsable:PR8–11 abiertas,STTP00001 independiente de STTM00001. Pendientes revisión visual,interoperabilidad e instalación/pruebas físicas; no se realizan desde este frente. Los mensajes enviados se consideran entregados por la herramienta, no aceptados técnicamente hasta respuesta.

## Secuencia después de la descarga
1. Verificar recibos y registro del banco, incluyendo integridad SQLite y hashes.
2. Leer metadatos app/patch/rePatch y contrastar identidad/versiones sin inferir Z/ZZ del nombre usado por el usuario.
3. Inventariar formatos y accesibilidad con lecturas acotadas; compartir hashes/procedencia con02y07.
4. Estudiar ejecutables y estructuras/modelos/animaciones generales; documentar límites criptográficos e incógnitas.
5. Actualizar PR3 y coordinar referencias cruzadas con PR7/prototipos; conservar ramas y propiedad separadas.

## Auditoría posterior del catálogo

[Auditoría de metadatos](bank-catalog-audit.md):9888archivos,21696entradas,8823objetos;0errores de referencias/estados/tamaños y0objetos sin referencia.161grupos de hashes físicos repetidos,conservados. Cinco pruebas nuevas aprobadas. Hash SQLite tras auditoría coincide con recibo del registro; no se rehashearon archivos de juegos en esta fase.

## Entrega inicial de prototipos

PR abiertas comprobadas: [contratos STT/3](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/8),[CombatLab](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/9),[AssetLab](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/10),[Vita3D](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/11). El chat responsable comunicó pruebas PC y compilación correctas; no se ejecutaron ni reprodujeron aquí. Ninguna está fusionada. El siguiente cruce de integración debe revisar dependencia entre contratos/núcleo y telemetría; no afirmar conexión UDP física que aún no existe.

## Revisión offline STT/3

[Interoperabilidad](protocol-interop-review.md):15casos sintéticos PC correctos. Validador candidato conserva casosSTT/1–2 y acepta ejemplosSTT/3 de386/432bytes; casoamplio715bytes. Validador vigente rechazaSTT/3 deliberadamente. Composición con analizador vigente resume2muestras, sin estadísticascombate. NoUDP,encoderC,VPK ni hardware probados en este recorrido; no se acredita instalación o integración enmain. El buzón del prototipo continúa local. Prototipos recibieron el informe; no hay encargo de cambiar el rechazo esperado del receptor antiguo.

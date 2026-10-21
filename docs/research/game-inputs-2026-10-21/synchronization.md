# Sincronización del proyecto — 2026-10-21

Este registro coordina estados y propiedad de archivos. No iguala los contenidos de ramas con funciones distintas ni acredita implementaciones que solo se han encargado.

## Fuentes de verdad y responsables
| Frente | Espacio y rama | Estado comprobado |
|---|---|---|
| Monitor | repository; main | 410b1dd70a3713b500a829aed55cb99cb74ad1d0; árbol limpio; Monitor0.5. PR6 integrada según cierre del chat propietario |
| Banco y documentación central | inventory-work; docs/game-input-inventory-20261021 | PR3 abierta; cambios locales propios y publicaciones por conector. El HEAD local no representa necesariamente el último commit remoto |
| Ingeniería inversa | research-work; research/stt-engineering-resources-20261021 | PR7 abierta; espacio mantenido por el otro chat. Es una carpeta de trabajo de publicación, no se exige que sea un checkout Git local |
| Prototipos | chat Inicia prototipos Vita | Orden enviada y creación Work en cola según confirmación del responsable. Sin rama/PR propia ni archivos modificados desde el chat emisor; inicio efectivo de implementación pendiente de verificar |

Propietarios: este chat mantiene inventory-work, el banco y los recibos FTP; STTMH Investigacion e ingenieria inversa mantiene research-work/PR7; Desarrolla el prototipo STT Vita mantiene repository y pruebas de monitor. No cambiar archivos ni ramas de otros frentes.

## Banco y copia de Frontier

**Cierre verificado:** [copia y censo final de Frontier](frontier-complete.md):8261 archivos/5212490427bytes incorporados; banco actual9888archivos. BaseG1.00 y parcheZ01.99 confirmados, sin afirmar ZZ, descifrado o jugabilidad.

Estado actualizado: ambos procesos terminaron con código0,0.partial, integridadSQLiteok y hashes de catálogos cotejados. El cierre de investigación está recibido (PR7,commit097f64f). Las correcciones de monitor están publicadas en PR12 abierta, rama docs/monitor-status-sync-20261021,commit6200812; repository está en esa rama limpia. main mantiene410b1dd. Los párrafos de transferencia siguientes conservan el plan inicial; queda superado su estado «en curso».

Banco inicial verificado:1627 archivos físicos,21696 entradas ARC descomprimidas,8823 objetos únicos. Las cifras del banco inicial no incluyen todavía la copia de Vita.

Copia FTP de lectura finalizada: PCSG00350, carpetas app/patch/rePatch,8261 archivos y5212490427 bytes, con una licencia excluida. SFO base confirma FrontierG1.00, no Z/ZZ. Los conteos de archivos observados durante la copia son provisionales y pueden diferir por momento de lectura. No iniciar otra copia, lectura FTP concurrente ni recatalogación del banco.

Fuente de estado: analysis-local/logs/vita-bank-status.json.
Cierre exige completed=true en vita-copy-PCSG00350.json, phase=complete y vita-registration.json válido. finish_vita_copy.py espera la copia completa y registra tras volver a comprobar hashes locales. La validación de flujo/local no es un hash calculado independientemente en Vita.

## Decisiones vigentes
- Banco y análisis de recursos generales, sin clasificar por armas ni buscar relaciones con Espada Larga.
- Catálogo y fusión anteriores son material histórico, no prioridad del banco actual.
- Prototipos con muestras propias pueden avanzar independientemente del análisis comercial. Sus contratos Monitor/HUD/Aquatic están encargados; no se presentan como implementados.
- No adaptación comercial sin activos legales. No publicar juegos, recursos, licencias o claves.
- Copia FTP de lectura expresamente autorizada; ninguna instalación ni escritura en consola desde este frente.
- PR3 y PR7 abiertas no equivalen a integración en main. No fusionar automáticamente.
- Continuación en este chat cada15min hasta nuevo aviso: primero verifica descarga/banco y después continúa análisis/documentación en etapas. Avisa solo novedades significativas o bloqueos.

## Discrepancias corregidas y pendientes
Se sustituyen las afirmaciones vigentes antiguas «Monitor0.2», «sin Frontier local», «solo piloto ARC» y «modelos/animaciones sin localizar» por los estados documentados actuales. Los informes fechados de etapas anteriores se conservan como historia.

Las pruebas de hardware del monitor pertenecen al chat propietario; no repetir instalaciones por sincronizar documentos. La descarga no prueba descifrado ni semántica de formatos. Los ensayos Citra y ELF de investigación pertenecen a PR7 y se actualizan por ese propietario.

Monitor confirmó main local=GitHub, árbol limpio, STT/1+STT/2 en receptor, agente STT/2 y UDP32100. Detectó tres textos antiguos (README general, README del agente y descripción de PR6); su corrección documental se encargó al propietario, sin reinstalación ni fusión automática. Investigación remitió cierre en PR7; el estudio de formatos continúa con los candidatos del censo final. Pendiente confirmar inicio efectivo del Work de prototipos. Los mensajes enviados se consideran entregados por la herramienta, no aceptados técnicamente hasta respuesta.

## Secuencia después de la descarga
1. Verificar recibos y registro del banco, incluyendo integridad SQLite y hashes.
2. Leer metadatos app/patch/rePatch y contrastar identidad/versiones sin inferir Z/ZZ del nombre usado por el usuario.
3. Inventariar formatos y accesibilidad con lecturas acotadas; compartir hashes/procedencia con02y07.
4. Estudiar ejecutables y estructuras/modelos/animaciones generales; documentar límites criptográficos e incógnitas.
5. Actualizar PR3 y coordinar referencias cruzadas con PR7/prototipos; conservar ramas y propiedad separadas.

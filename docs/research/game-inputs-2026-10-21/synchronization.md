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

## Primer derivado Frontier enlazado

[Derivado local y procedencia](bank-derivatives.md): salida JKR349bytes obtenida por investigación y cotejada aquí con su fuente/recibo/hash. Registro adicional derivatives.jsonl,1entrada; bytes externos conservados,sin copia ni cambio de SQLite. Consulta ampliada por ruta/hash. Cinco pruebas nuevas y cinco de regresión aprobadas;consulta real y hashSQLite cotejados. La salida sigue sin identificar. Las65pruebas del decodificador pertenecen a PR7;no se repitió aquí la descompresión. No ampliar los otros43JKR sin aceptación útil del interior.

## Revisión AssetLab→Vita con muestra propia

[Puente de recursos](asset-bridge-review.md): muestra STTAsset/1 original de4huesos/48vértices/72triángulos,192poses a1/60s calculadas sin valores no finitos. Duraciones2s/1,2s y7claves en cuadrícula60Hz; solo se evaluó esta muestra. Conversión numérica×1000 y límites muestreados documentados; sin cambiar base ni exportar formato destino. Redondeo y empaquetado son propuestas explícitas,no contratos aprobados ni memoria Vita medida. Pendientes:ejes/avance,winding,evaluador/importador,runtime/memoria,GUI y física. Coordinador de prototipos informado,sin encargo de implementar por este aviso.

## Coherencia de fuentes entre PR8–11

[Comparación a commits fijados](prototype-overlap-review.md):17rutas compartidas,36observaciones deblobGit;16rutas idénticas ysoloCHANGELOGdistinto. PR11 conserva9rutasdecontratos dePR8 y7deCombatLabdePR9. Los4changelogs comparten prefijo yentradaspropias;requierenconsolidación futura. No se probó fusión combinada ni archivos exclusivos/runtime. Las4PR estaban abiertas,enborrador ysin fusionar. Coordinador informado;sin cambios en ramas.

## Regiones compatibles con texto en el derivado JKR

[SondeoCP932](frontier-jkr-text-regions.md) sobre los mismos349bytes:14tramosNULcompatiblesCP932conkana,160bytes,12sincontroles/2concontroles;14rechazanUTF8estricto. No se exportaron cadenas. Seis pruebas sintéticas correctas yhashfuente igual. No acredita formato,codificacióncanónica ni función. Investigación recibió el hallazgo para gramática/bordes de esta misma muestra;losotros43JKRsiguenpendientes,sin nuevaextracción.

## Contraste JKR y preparación de PR3

## 21-10-2026 — Segundo JKR y preparación de PR3

- Contraste limitado a una muestra adicional: fuente1.058bytes, salida1.884bytes, carga1.042/1.042 consumida. Fuente/salida/recibo cotejados con banco; original intacto. Dos derivados enlazados por metadatos, SQLite intacto.
- Patrón de prefijos del control no reproducido; cero tramos cumplen el criterio CP932/kana, sin probar ausencia de texto. Gramática pendiente,42JKR sin ampliar. PR7 commit90dc6d1 comunica8pruebas nuevas; no repetidas aquí.
- Conflicto exclusivo de changelog con main410b1dd70a resuelto conservando ambas historias en copia aislada. No se fusiona PR3 en main ni se modifican ramas ajenas.

[Registro actualizado de dos derivados](bank-derivatives.md).

Verificación de preparación PR3: 60 pruebas automatizadas PC correctas y ensayo CLI de diez paquetes simulados aprobado. La primera ejecución aislada no recibió UDP local (59/60); repetición autorizada fuera del aislamiento:60/60. Sin tráfico hacia Vita. Diferencias de código del monitor respecto a origin/main: ninguna; únicamente documentación e instrumentos de inventario propios. CI remota de esta preparación pendiente de publicación/ejecución.

## CI de la preparación PR3 y siguiente etapa

Para el commit exacto `1b59dd01ac5cf745b36dba48ceda5984d642e4c9`, GitHub confirmó ambas ejecuciones completed/success: [Monitor tests39576768233](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39576768233) y [Vita agent build39576768171](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39576768171). Esto no acredita hardware ni se atribuye a commits documentales posteriores. No se descargó ni transfirió el artefacto.

PR3 permanecía borrador/abierta, mergeable=true ysin fusionar. Se encargó a investigación una revisión estructural de un único MOD230 ya catalogado; Área07, límites/tablas y bloqueos antes de geometría. [Plan vigente](analysis-plan.md). No repetir descompresión JKR ni ampliar42restantes.

## MOD230: evidencia parcial recibida

[Seguimiento y límites](mod230-followup.md). PR7/10f3f10: una muestra990bytes,16posiciones/UV finitos y28índices accesibles. Discrepancia global30declarados/29disponibles y min/max0/0 pendientes. Aquí cotejados objeto/copia/3recibos yhashSQLite; sin nueva extracción,duplicación de objeto o pruebas del lector. Ocho pruebas comunicadas por investigación; geometría completa no validada.

## Contraste de convenciones: discrepancia delimitada

[Investigación PR7/4d0e9a9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/4d0e9a9/docs/research/stt-re-20261021/mod230-index-conventions.md) encontró que un lector público explícitamente MH4U/E6 lee cantidad de malla+un u16:29índices,58bytes desde932,hastaEOF990. El índice adicional añade una terna con repetición; ambas ventanas mantienen seis ternas de índices distintos. No es comprobación de área/winding.

Ese lector deja sin usar el u32 que RevilLib denomina dos campos min/max. Su semántica MHXX no está probada:0/0 frente a0–15 es diferencia de interpretación, no corrupción confirmada. El contador global30 permanece sin explicación específica MHXX. No se rellena ni corrige el archivo. Geometría completa no validada; cierre del ensayo como delimitación, sin ampliar modelos.

Aquí se cotejó SHA-256 del recibo `index-conventions.json`: `a970b3c73b866af6022e038b190efcdb840da4359c499297ac9c82d287e5a215` y copia fuente contra evidencia. Cuatro pruebas nuevas pertenecen a investigación y no se repitieron. Fuente documental fijada:mhff6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf, aplicabilidad declarada MH4U/E6; no implica compatibilidad MHXX. Banco y derivados sin cambios.

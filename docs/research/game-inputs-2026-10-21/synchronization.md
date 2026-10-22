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

## Referencia estática PSP aceptada

[PR7/c529799](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/c529799/docs/research/stt-re-20261021/mhfu-import-reference.md): primer registro de imports del ELF MHFU, puntero NID VA0x0890EC78 ↔ offset0x0010D22C ↔ sección.rodata.sceNid. Cálculos independientes por sección yPT_LOAD coinciden;12bytes requeridos respaldados por archivo. Confianza estructural alta para esta única referencia, sin identificar función, biblioteca resuelta o ejecución.

Artefacto existente1.910.384bytes, SHA-256 `64937c521286fc8423076e644089881c5fe051bed2565e5061dda8aec0b45e10`; prefijo canónico1.910.044bytes SHA-256 `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`. Cola340bytes excluida,sin interpretar. Aquí cotejados ambos hashes yrecibo `9b370c8b054d81f8cc278f0c84bb135851e30da6267c354b51e762231ff63f3a`; no repetido parser.

Cinco pruebas sintéticas aprobadas por investigación,no reproducidas aquí. Referencia primaria comunitariaPSPSDK6ef2b21dc440ef8d4125f000301faaa2a470975e; no especificación propietariaSony. No se publican NID/código ni se aplican relocaciones; no equivale a port,compatibilidadVita o semántica de juego. Área02 conserva direcciones estáticas yprocedencia; áreas04/07 no reciben funciones/recursos inferidos. Aceptación cerrada a una referencia, sin ampliación automática. Banco,originales yconsola sin cambios.

## Próxima aceptación LMT: una pista, pendiente

Se encargó al propietarioPR7 contrastar una sola pista vectorial LMT67 ya decodificada con una segunda referencia primaria/decoder independiente. Selección determinista,preferencia por menor pista cuantizada; presupuesto una pista. Aceptación requiere independencia real,aplicabilidad y comparación numérica/tiempo con tolerancias. Si falta base,documentar bloqueo,sin llamar al resultado validación cruzada.

No repetir bibliotecas completas,exportar claves comerciales,asociar rig,rotaciones o vista previa. FPS permanece desconocido. El envío del encargo no acredita resultado; pendientes ejecución,evidencia y revisión. Sin ampliación deJKR/modelos ni cambios de banco/consola.

## LMT: contraste documental cerrado con bloqueo

[PR7/19d6e9d](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/19d6e9d/docs/research/stt-re-20261021/lmt-one-track-review.md): una pistaLMT67,slot8/pista2,codec5,payload8bytes/dosclaves. Segunda referencia MHW coincide documentalmente en fórmula yacumulación básica,pero usa otro layout yno acredita independencia/aplicabilidad suficientes paraMHXX LE32. No se ejecutaron dosdecoders;no hubo comparación numérica independiente. Errores/tolerancias permanecennull,no cero;FPS,rig,ejes/unidades desconocidos.

Recibo de selección cotejado aquí por SHA-256 `3db66f07db494024c8b890efa5f40ec1d891c841c9356f157aedb099772deb58`. Sin repetir decodificación,pruebas o publicar claves comerciales. Bloqueo:segunda referencia independiente ycompatible o especificación que justifique equivalencia. Conservar pista como control,sin ampliar bibliotecas.

Siguiente tarea encargada a investigación:una cargaTEX ya catalogada,solo cabecera/versión/dimensiones/mips/rangos con referencia aplicable. Sin exportar imagen ni adaptar. Resultado pendiente;no se declara textura validada. Banco yoriginales intactos.

## Pruebas solicitadas: TEX y corroboración PSP

[PR7/c4215e8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/7):una cargaTEX de84bytes,cabecera16+tabla4+carga64,8×8,unmip,ETC1A4 segúnreferencia3DS aplicable. Rangos coherentes;no se decodificaron píxeles ni validó imagen/swizzle/alfa visual. Siete pruebas sintéticas nuevas pertenecen a investigación. Aquí cotejados ambos recibos porhash.

DoslogsPPSSPP previos corroboran direcciones/tamaños de secciones de la referenciaPSP;no prueban lectura concreta delpuntero,resolución oinvocaciónfuncional. Cuatro pruebas nuevas del comparador pertenecen a investigación;recibo cotejado aquí. Otroarranque con iguales mensajes no añade esa evidencia;no se repitió.

Por solicitud expresa«todaslaspruebas»,este frente ejecutó60pruebasPC correctas yensayoCLI dediezpaquetes simulados aprobado sobre062e085. Sin tráficoVita. Investigación recibió campaña de regresión pertinente de lectores;resultado pendiente. No repetir censos/extracciones ni considerar bloqueoscriptográficos/semánticos resueltos por pruebas sintéticas.

El usuario autorizó ejecución dejuegos en emuladorPC;preservar perfilesaislados,fuentes ypartidas. No implica permiso de instalar/ejecutar enPSVita. Los ensayos futuros requieren aceptaciónconcreta,no repetirarranque porduración.

## Cierre de regresión de investigación y fallo monitor comunicado

PR7 publicó matriz:106/106pruebas sintéticas correctas sobrec4215e801bc14d5158321860a3afddeda790d561,21/21herramientas con sintaxis yCLIhelp correctos,78archivos cotejados. HashSQLite antes/después idéntico. No hubo nuevas ejecuciones de emulador,dumps o decodificación real;no acredita fidelidadcomercial. [Matrizdelpropietario](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/research/stt-engineering-resources-20261021/docs/research/stt-re-20261021/pc-regression-matrix.md). Investigaciónemuladores activa porplataforma;sinresultadosfinales todavía.

PR13/head193c7b467e60bce7e17e721f4f9aba5bf6f7fb94:Monitor tests39674410982 completed/failure,Vita agent build39674411028 completed/success. Diagnóstico/corrección encargado alpropietario,causapendiente. No se modifican susfuentes desdePR3,nosefusionanPR niinstalaartefacto. No atribuir éxito decompilación apruebasPCfallidas.

## Recepción y nueva distribución de tareas

Informes de los propietarios recibidos:prototipos PR15 STT Pose/1,exportación/reimportación de192poses y149.293bytes,29pruebasPC yCI declaradas; lectorC/runtime pendientes. Monitor PR13/d112214 corrige pruebaCLI yPR14/e702126 añade análisis de pausas,CI declarada correcta;sin fusión. FTPlectura delpropietario confirmaSFO STTM00001 00.50 coincidente conVPK;STTP00001 SFO550 no prueba ausencia global. Estos resultados se atribuyen a sus propietarios,no son ensayos repetidos aquí.

Órdenes siguientes enviadas:prototipos lectorCportableSTTPose/1 con pruebas cruzadas/entradasmalformadas ymemoria;monitor validación conjuntaPC dedirecto/pausas con sesiones,reordenación/reloj/entrada inválida;investigación cerrar comparaciónemuladores yprocedencia delnuevoMH4U.3ds,seguida de aceptaciónvisual acotada si existen medios fiables. El avance Citra es carga inicial porlogs,no jugabilidadvalidada.

No nuevas conexionesFTP tras inspección cubierta;sin transferencia/instalación/consola,fusionesPR oalteración de banco/originales. Tres frentes con tareas diferenciadas; resultados nuevos pendientes de cierre,evidencia yrevisión.

## Comparativa de emuladores y nueva base 3DS legible

Entrega delpropietarioPR7,commit964770ad40a6c7dfc7df6bc4294858521ae7ff55:comparativaPPSSPP1.20.4/Azahar2126.2/Vita3K4211,fuentes/versiones/hashes;Azahar yVita3K no instalados en esta etapa. [Informe fijado](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/964770ad40a6c7dfc7df6bc4294858521ae7ff55/docs/research/stt-re-20261021/emulator-comparison.md).

NuevaentradaMH4U EUR NCSD.3ds de4GiB,SHA-2563832beef353d134bcba6ef83dc987e7ae228c43dc32a6ba52519f5f103f52581,ProgramID0004000000126100,tresNCCH no_crypto. No implica equivalencia conCIA ni revisiónexactadeljuego. Citra2104 ejecutó15,641s enperfilaislado:loader/DSPHLE acreditados porlogs,paradacontrolada,originalintacto. Sin imagen/FPS/jugabilidadvalidados. Corrige solo la afirmacióngeneral deausenciadebase3DSlegible;CIApreviasmantienenbloqueocifrado. [Ensayo](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/964770ad40a6c7dfc7df6bc4294858521ae7ff55/docs/research/stt-re-20261021/citra-current-inputs.md). No incorporada automáticamentealbanco.

ContrasteTEX delpropietario:segundalectura descarta alfa;no acredita fidelidadRGBA/RGB/orientación. Derivadoprivado,noaptitudparaadaptación. No confundir aceptaciónestructural anterior conimagenfiel.

Bloqueovisual:superficieCUA disponible sinAPIsnativas;noobservaciónvisualrealizada,norepetirarranquesconmismoslogs. Encargada alternativa:.codeMHXX,flag/rangosBLZ ysegmentosantesdedescompresión;no forzar codec si flags noaplican. Fuente/derivadoslocales,metadatospublicables,sincambiosconsola/banco/originales.

## Monitor: ensayo conjunto y duración acotada

Propietario entregóPR16/79a8969,sin fusionar,dependenciaPR13→PR14→PR16. Ensayo cubre reinicios/duplicados/desorden/reloj/entradasinválidas;20pruebaslocales yensayosintético correctos según informe. Opción--duration detiene captura incluso con tráfico continuo. CIpushPC/Vita correcta segúnpropietario;eventoPRpendiente al cierre. No atribuirlo apruebasfísicas.

Nuevaaceptación encargada:límites explícitos de memoria porconteo y tamaño dearchivo,paradalimpia/resultadoparcial marcado sin descartes silenciosos,pruebasdecasos límite. No afirmar bytesRAM medidos si solo se limita número deelementos. Sinconsola/FTP.

Prototipos continúan lectorC/pruebaC-Python/VitaSDK yadaptador de triángulos,sin cierre definitivo aún;investigación ExHeader/BLZ MHXX en curso,compresiónindicada ysalida declarada13.045.760bytes,pendiente aplicación/recibo. Avances provisionales,noaceptacionescerradas.

## MHXX .code: aceptación BLZ cerrada

PR7/3e9bbdb032cf448194b09c07499fb5ee4ecde264:una entrada NCCHexistente,flagcompresión confirmado,pieBLZ ysegmentos declaran13.045.760bytes;salidaúnica coincide,flujo completo,prefijo84bytes conservado. BSSseparado,no añadido a salida. SHA-256code.bin `6f66928e0deecdcd20c3b0e67c614e6313dfe92c8dc0b9ba2d7a906d1efe4fe8`;reciboprivado `bcfa81ad09d0bc68476e75340006b9d5d9f29b7e73be84aaf2827f3f91ec02cc`. Ambos cotejados aquí,sin repetirdescompresión.

Investigación declara10pruebasnuevas,116/116suitecorrecta;decodificador adaptado deAzahar GPL2+ conatribución/licencia. No hashdescomprimidoindependiente encontenedor ni contrasteindependienterealizado. Valida algoritmo/rangos,nosemántica,ejecución,baseMHXXcifrada oparchearrancable. Derivadosprivados fueraGit,sin incorporaciónalbanco. [Informe](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/3e9bbdb032cf448194b09c07499fb5ee4ecde264/docs/research/stt-re-20261021/mhxx-code-blz.md).

Siguienteaceptaciónencargada:unaVA↔offset↔segmentoARM respaldadaporExHeader/fuenteprimaria;distinguirtextstartdeentrypoint yARM/Thumbsolo sihaybase. Sin inferirfunciones odesensambladocomercialpublicado,ni repetirBLZ/emu.

## MHXX: referencia estática de entrada cerrada

PR7/d419d6b41e7c21ee9cb11025df50fb120f0a75f2:mapaúnico VA0x00100000→offset0→text,rango[0,4) respaldado porarchivo,noBSS/padding. Entryderivado delrutaloaderAzahar2126.2,no campo explícitoExHeader;CPSR.T=0/A32 esperado según implementación,alta confianza estructural. Sin opcode comercial publicado,funciónidentificada,ejecuciónhardware oparchearrancable demostrado.

Propietario comunica8pruebasnuevas/124suitecorrecta,fuentesversionadas yhashesNCCH/code conservados. Reutilizócode.bin,sinnuevaBLZ/emu/binarios/banco. [Informe](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/d419d6b41e7c21ee9cb11025df50fb120f0a75f2/docs/research/stt-re-20261021/mhxx-entry-reference.md). Contrasteindependiente ysemántica siguen pendientes;no atribuirIA/hitboxes.

## Cierres lectorC y límites delmonitor

Propietario prototipos:PR17 dependiente15,lectorCacotadoSTTPose/1 yadaptadortriángulos,288casosC/Pythonconsanitizadores,30pruebasPython yobjetoVitaSDK correctos. MemoriaPC comunicada:índice5.600bytes,salidapose3.456bytes;no presupuestoRAMVita completo. SinVPKnuevo ovalidacióngráfica/física. EncargadaconexiónalrendererPR11 con muestrapropia,pruebasPC/compilación yfallocontrolado.

Propietario monitor:PR18/208a5d7 cuota10MiB ylímites1000sesiones/100000secuencias,parada/parcialexplícitos;PR19/89f99b2 rechaza anexadotrasarchivo sinLFfinal,conservándolo.26pruebas/CI PC-Vitacorrectas;CI16 confirmada. Cadena13→14→16→18→19 sinfusionar. LímitesdeconteonoRAMmedida. Encargadarevisiónfinaldependencias/CLI/formatos yordenpropuesto,sinfeaturesnuevasinnecesarias.

Resultados atribuidos asuspropietarios,no repetidosenPR3. Banco completoconrecibos sin cambios;sinFTP/instalación/consola niadaptacióncomercial.

## Renderer propio integrado y monitor listo para revisión

InformeprototiposPR21:Pose/1 conectado alrenderer con muestrapropia,límite160KiB yfallbackcontrolado;sanitizadores/anclas/animación/16cámaras aprobadossegúnpropietario. VPKSTTP00001/00.11 compilado/inspeccionado;almacenamientoassetPC172.904bytes,noRAMVita medida. Visual/físicopendiente. Encargada comprobaciónvisualPC solo si backendexistente viable;sincrearmotorcompleto oinstalarconsola.

MonitorPR20/f30e8d4 entregamatriz/heads/orden13→14→16→18→19→20;26pruebas/CIdecódigocorrectas segúnpropietario. CI documentalpendiente,encargadocierre;frente listopararevisión,sinfusión ofeaturesadicionalesinnecesarias. Pendientesfísicosred/reloj no se sustituyenconPC.

Investigaciónrecibe siguienteaceptación:una particiónNCCH ejecutable de nueva baseMH4Ulegible,ExHeader/ExeFS/flags/rangos conprocedencia;sinRomFSmasivo,nuevosemuruns odescompresiónautomática. Banco/otrasramas/originalesintactos.

## MH4U base estructurada y monitor integrado por autorización directa

PR7/1bdf73ecd6f3535b2d83c105b1847f3f9806ccca:partición0NCCHejecutable/no_crypto deMH4Ubase,ProgramID0004000000126100;ExHeader/tablaExeFS yhashes.code/banner/icon coinciden. .codecomprimido9.091.360bytes,pieBLZdeclara16.261.120igualpáginasdesegmentos;sin descompresiónenestaetapa. FlagsCPUsolicitanL2/804MHz,no frecuenciaobservada;noISAinferida de core_version. Propietario comunica7pruebasnuevas,sinrepetirsuite124.

DosSHAcompletos4GiBleenbytesRomFS pero no lo parsean/extractan:recibooriginalseconserva yacceptanceaclaraelalcance,no se reescribehistoria. Siguienteaceptaciónencargada:solo.codeBLZ,salidaprivadaacotada16.261.120bytes,consumo/prefijo/hash/segmentos yBSSseparado. SinrepetirSHAimagencompletasinmotivo,sinbanco/emu.

Monitorconfirmó autorizaciónhumanadirectaensuchat:«Sí,fusionarlas seisPR». Cadena13/14/16/18/19/20fusionada;merges130948a/79a6292/0041f73/5c9a79b/7becc6e/f199bd0. Según cierre:mainlocal/remoto sincronizado,árbollimpio,CI finalPC/Vita correcta. No esuna autorización general de fusionarPR3/7/prototipos. Sinreinstalación/FTP;pendientesfísicosred/reloj conservados. Estadoanterior«sin fusionar» deestas6PRqueda superado;registrohistóricoconservado.

## MH4U BLZ cerrado: alcance parcial de preservación

PR7/93455dcab83d823d1b4218b039aa29e951e5e7a1:una.code9.091.360bytes,cotejadaantes/después;salida16.261.120bytes SHA-25663940d7ef1fecc119f9fb820f5f6a2cf2f2a5549e4a70f00319fbd6c9c1ad8dc,tamaño/hashsalidacotejadosaquí. Flujo/coberturaterminanexactamente,prefijo76conservado;segmentostext/ro/datarespaldados yBSS/stackseparados. Propietariocomunica7tests nuevos,decodercompartidosincambios.

No se repitióSHAdeimagen4GiB:hashNCSDhistórico,noafirmarimagenenteraintactareverificada. Statigualnopruebaotrasregiones;whole_image_unchanged_reverified=false. SinRomFSparseado/extraído,arranque,banco oconsola. [Informe](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/93455dcab83d823d1b4218b039aa29e951e5e7a1/docs/research/stt-re-20261021/mh4u-code-blz.md).

Siguienteaceptación:comprobarlinaje/aplicabilidad deunasegundaimplementaciónBLZ ycontrastaruna salida siindependenciaacreditable;deotro modo cerrar bloqueoexplícito. No acreditarsemántica/ARMThumb/funcionesporhashcorrecto.

## 22-10-2026 — Independencia BLZ bloqueada y visualPC cerrada

PR7/a914801aa3865a516aba848a214d055243ca6284 revisóCTRTool,CUE/PeterLemon y3dstool con fuentes/linaje/licencias;no aceptóindependencia suficiente. No implica que todas sean dependientes:procedenciaindependiente no acreditada bajo criterio fijado. second_decoder_executed=false;igualdad tamaño/hash/consumo=null,no cero. Sin nuevaslecturasimagen/descompresiones/pruebas. Whole_image_unchanged_reverified=false conservado. Reabrir solo con evidencia primariaaplicable,norepetirbúsquedaidéntica. [Informe](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/a914801aa3865a516aba848a214d055243ca6284/docs/research/stt-re-20261021/mh4u-blz-independent-review.md).

Prototipos entregó revisiónvisualPC dePR21:dosposesobservadas ydefectodecobertura alinvertirtriánguloscorregido;sanitizadores,VPK einspeccióncorrectos segúnpropietario. Noacredita renderGPUVita. Siguienteaceptaciónrequierehardware:carga/controles/suspensión/rendimiento. No se ordenan instalación/FTP/ejecuciónconsola con autorizaciónactual de revisiónlectura. Sinfusión ni cambiosbanco/originales.

## 22-10-2026 — Aceptación de jerarquía independiente encargada

Nuevaorden de investigación:una muestraMOD230 ya catalogada conhuesos,selecciónmínimatamaño/desempatehash;solo tablas/esqueleto,rangos,padres/raíces,ciclos yfinituddematrices si fuenteaplicable. No escontinuacióndelcontadorgeométrico de990bytes,nolo resuelve. No asociarLMTpor nombre,skinning oadaptación. Resultado pendiente. BloqueosBLZ/LMTno se reabren sin nuevaevidencia;monitorPCcerrado yprototipoPCvisualcerrado conservan pendientesfísicos.

## 22-10-2026 — Jerarquía MOD230 parcial cerrada

PR7/16111d8,según propietario:una muestra catalogada con3huesos,2raíces,0ciclos y6matricesfinitas;10pruebas nuevas correctas. Acredita estructuraacotada,no rigfuncional,skinning,bindpose oasociaciónLMT. [Informe](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/16111d8/docs/research/stt-re-20261021/mod230-skeleton.md).

Centralrecibióinforme porlecturadeestado;elenvíoderegresodelpropietariofue rechazadopor revisiónautomática yno se reintenta. No bloqueatrabajolocal. Siguienteaceptaciónencargada:sobre mismamuestra,propiedadnuméricadelasdosfamiliasdematrices solo confuenteprimariaaplicable,toleranciaexplícita ymetadatosagregados. Si semántica noacreditada,cerrar bloqueo;sinmatricescomercialespublicadas,nuevoLMT/skin/render/banco/consola.

## 22-10-2026 — Relación entre matrices no confirmada

PR7/e8a0c7b:0/3pares dematrices cumplen tolerancia0,0001;8pruebasnuevas deherramientacorrectas segúnpropietario. No convertir prueba negativa en corrupciónconfirmada orelacióninversaaceptada. Jerarquíaestructuralprevia conservaaceptación;rigfuncional/posebasependientes. No ampliar toleranciaparaforzaréxito.

Cerradoensayo deestamuestra;reabrir con fuentesemánticanueva,no expandirconvenciones/muestrasindiscriminadamente. Encargada consolidación documentalPR7 deaceptaciones/commits/límites/criteriosdereapertura yconclusioneshistóricassuperadas,sin ensayos nuevos. Banco yrecibosFTP completos,sin cambios.

## 22-10-2026 — ÍndicePR7 consolidado y controles pendientes

Índice delpropietario consolida29aceptaciones hastae8a0c7b:22verificadasdentrodesualcance,2negativas,5bloqueadas. No son29funcionesdeljuegovalidadas;mantener snapshot/commits ycriteriosdereapertura. [Índice](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/research/stt-engineering-resources-20261021/docs/research/stt-re-20261021/acceptance-index.md).

Avanceposterior comunicado:12lecturas de2rangos sinvariación;traspulsaciónautomáticaA no se confirmóentrada reconocida,pornotanto sinvínculodatos↔acción. Noconcluir ausenciaestadovariable.No repetirlecturas hasta confirmarentrada/estado observable.

Eigent auditoríadocumentalpública permaneceesperando aprobación search_actions(mcp.tool.write);0archivosdesalida, no informefinal. No aprobada ni reintentada. Bloqueoyacomunicadoalusuario;sinrepetiravisosinalterados. Banco/completitudrecibos sin cambios.

## 22-10-2026 — PR3 preparada sobre main integrado

Copiaaislada dePR3 actualizada conmainf199bd07b4e05ee4f7e56ed616840518374f3300;solo conflictosREADME/changelog,ambashistoriasconservadas yreferenciasvigentes corregidas. Código stt_monitor/vita-agent/workflows idénticoamain. No fusión dePR3 enmain.

Validaciónlocaldelárbolpreparado:71/71pruebasPC correctas,CLI10muestras ysmoke_limits correctos(cuotaUTF8/LF,CRLFprevio,intactos,rechazoanexadoincompleto,informeparcial). Tráficoexclusivobuclelocal,sinVita/FTP. CIremota deesta preparaciónpendientedecomprobar.

## 22-10-2026 — CI PR3 confirmada y contadores por fotograma

CI delcommitexacto966fb5ffef7f11020ab7ea07fb76ec260834744c confirmada:Monitor tests39697855865 yVita agent build39697856255 completed/success. Recibolocalanalysis-local/logs/pr3-ci-966fb5f.json. No atribuir estas ejecuciones a commits documentalesposteriores ni a hardware.

PropietarioPR7 comunica runtime-frame-step:100lecturascorrectas/0errores,en3avancesindividuales defotograma amboscontadores+1yestablesentreavances.4pruebasnuevasdelaherramienta correctas. Esaceptaciónacotadaderelaciónconavanceemulado,noposición/animación ni instruccionesescritorasidentificadas. Citraretornadoaejecuciónnormalporpropietario;central nointervinoemulador. [Informe](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/research/stt-engineering-resources-20261021/docs/research/stt-re-20261021/runtime-frame-step.md). SinVita/FTP/banco alteradosdesdeestefrente.

## 22-10-2026 — Lector de capturas ampliado

Cierre delpropietarioPR7:2.400lecturascorrectas/0errores,barridos8KiB conventanasprioritarias,archivo deduplicado con tiempos/direcciones/hashes;9exportacioneslocales verificadas y9pruebasdelaherramienta aprobadas. Permite reconstruir/compararmemoria muestreada,no identifica recursosoriginales. Capturas/datoscomerciales privados,fuera delbancoexistente yGit. Citra seguíaabierto yteclasliberadassegúncierre;centralnointervino.

Aceptaciónestática previa:24candidatosdelecturadedoscamposvecinos,71palabrasinstrucciones/literales coincidenconmemoria segúnpropietario;6pruebasdelanalizadorcorrectas. No ejecución decandidatos ni escritordeloscontadores confirmado. No tratar coincidenciabytescomosemántica. Investigaciónactual contrasta referenciasexternasporversión,sin activartrucos/escriturasdememoria. No nuevastareasduplicadas.

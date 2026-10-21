# STT — Ingeniería inversa y recursos

## Estado más reciente: bordes de la muestra JKR

[Contraste de gramáticas y bordes](frontier-jkr-layout.md): se reutilizan las 14 anclas del sondeo central, sin exportar texto ni repetir CP932. Patrón repetido de 11 bytes observado; estructuras públicas examinadas no aceptan el bloque desde cero. Gramática interior pendiente, sin ampliar a los otros 43 JKR. 70 pruebas sintéticas aprobadas.


## Etapa anterior: primera muestra JKR

[Una muestra Frontier JKR/LZ descomprimida](frontier-jkr-sample.md): 349/349 bytes, toda la carga consumida, hash registrado, original intacto. Salida todavía sin firma reconocida ni semántica validada. 65 pruebas sintéticas aprobadas. Código con adaptación MIT atribuida; resultados comerciales solo locales.


## Etapa anterior: Frontier completo

El frente de inventario cerró la copia local. [Contraste independiente de 50 candidatos](frontier-complete-headers.md): 44 cabeceras JKR/LZ, 5 ECD y 1 firma SCE, con hashes coincidentes. Sin descifrado/descompresión de esos candidatos ni validación semántica. 52 pruebas sintéticas aprobadas. Los párrafos de copia parcial siguientes describen etapas anteriores.


## Etapa anterior: Citra y DATA.BIN completo

Ensayos reales de [Citra para 3DS](citra.md): bases MH3U/MH4U/MHXX bloqueadas por material criptográfico ausente; parche MHXX instalado con contenido de hash coincidente, ejecución aislada termina con crash. [MHFU DATA.BIN](mhfu-data.md): 6.657 entradas procesadas con comprobación de reversibilidad. [PPSSPP y Frontier](emulators.md): ELF PSP obtenido y contrastado; Frontier continúa siendo copia parcial. 46 pruebas sintéticas aprobadas. No demuestra reproducción visual ni validación semántica completa.


## Antecedentes de las etapas anteriores

Encargo STT-RE-20261021. Informe de ejecución del 21-10-2026, Europe/Madrid.

**Emuladores y descifrado comprobado:** [PPSSPP/MHFU y nuevos metadatos Frontier](emulators.md). Se obtuvo un EBOOT local descifrado: su prefijo de 1.910.044 bytes coincide exactamente con BOOT.BIN; 340 bytes adicionales quedan sin interpretar. Frontier ya tiene metadatos de parche Z 01.99, todavía sin copia completa ni revisión ZZ verificada. Corregidas firmas ECD/EXF del sondeo; 40 pruebas sintéticas aprobadas. Sin instalación/transferencia a consola.

**Etapa LMT anterior:** [decodificación limitada de pistas MHXX](lmt-vectors.md): 1.772 claves vectoriales en 90 pistas; 89 presentan variación. Aún sin rotaciones, binding o reproducción visual; datos extraídos solo locales. El usuario autorizó el descifrado; las entradas cifradas siguen sujetas a requisitos técnicos. Suite ampliada a 36 pruebas.

**Actualización posterior autorizada:** [continuación PSP y Frontier local](continuation.md). GU Switch queda excluido por el usuario. Hay ahora archivos Frontier Vita locales en una copia todavía incompleta; su SFO identifica la base G 1.00, sin revisión Z/ZZ demostrada. Las menciones de ausencia de Frontier y los conteos siguientes describen la primera fotografía, no el estado posterior. El nuevo lector amplía a 620 secciones ELF PSP; 25 pruebas aprobadas.

## Resultado y alcance real

Revisión independiente del proyecto, los archivos accesibles y las fuentes públicas. No demuestra un port nativo ni recursos comerciales listos para reutilizar.

- Se leyeron completos y calcularon SHA-256 de **10.641 archivos físicos, 13.045.602.968 bytes**, en la carpeta del proyecto: juegos, derivados previos, banco de objetos, herramientas y documentación. No son 10.641 archivos originales de juegos. Se excluyeron `.git`, enlaces y la carpeta de salida del propio ensayo; alcance exacto en [recibo](audit-summary.json). Es una fotografía del recorrido, no una instantánea atómica de trabajos concurrentes.
- **7 originales, 7.861.039.260 bytes**, conservan sus hashes de referencia. Ningún fallo de lectura o cambio de tamaño/mtime durante la lectura fue observado. SHA-256 identifica contenido; no autentica la distribución ni acredita derechos.
- Se volvieron a descomprimir en memoria **1.228 ARC LE v17 / 21.696 entradas** del RomFS del parche MHXX. Longitudes comprobadas; hashes idénticos al catálogo previo. Se releyeron los **8.823 objetos** del banco: tamaños y hashes correctos, SQLite `integrity_check=ok`. Cero errores en esas comprobaciones.
- Se volvieron a sondear **83 MOD230 y 4 LMT67**: todas sus cabeceras pasaron las comprobaciones limitadas. No se han validado geometría completa, skinning, codecs de pistas, asociación rig/animación ni reproducción.
- Se inventariaron por lectura los **13 archivos internos del ISO MHFU**, con tamaño, offset y hash. Hallazgo nuevo: `BOOT.BIN` presenta ELF32 little-endian, `e_machine=8` (MIPS), ET_EXEC y entry `0x08906934`. Esto permite un próximo análisis estático sin descifrar `EBOOT.BIN`.
- Se leyó el ExeFS ya legible del parche MHXX: `.code`, `banner` e `icon`; los tres SHA-256 coinciden con la tabla ExeFS y el hash de su cabecera coincide con NCCH. No se descomprimió ni ejecutó `.code`.

Catálogo físico completo local: `analysis-local/stt-re-audit-20261021/physical-files.jsonl`. Banco previo local: `analysis-local/resource-bank/catalog.sqlite`, con procedencia de cada entrada y objeto. El manifiesto físico incluye cada archivo accesible en el recorrido, incluso derivados duplicados y muestras sintéticas; no se suman como material independiente. Los archivos creados después de este recorrido quedan fuera de sus conteos. [Recibo de evidencias locales](local-evidence-receipt.json) y [archivos internos PSP](psp-files.json) permiten cotejar procedencia sin publicar contenidos.

## Entradas y bloqueos por juego

| Juego / plataforma observada | Archivos originales | Estado verificable | Límite |
|---|---:|---|---|
| MH3U / 3DS | 1 CIA, 1.871.489.344 bytes | CIA/TMD `00040000000B1D00`; hash completo | Contenidos base marcados cifrados; recursos y código no accesibles por este análisis |
| MH4U / 3DS | 2 partes 7z, 2.734.920.480 bytes | CIA derivado presente; metadatos previos `0004000000126100`; ambas partes releídas | Bases cifradas; las pruebas 7zr anteriores constan en PR3/logs, no se atribuyen como extracción nueva |
| MHFU / PSP | 1 ISO, 886.702.080 bytes | ISO9660, SFO ULES01213 / DISC_VERSION 1.01, 13 archivos internos hasheados | DATA.BIN aún opaco; el ejecutable visible no equivale a funciones reconstruidas |
| MHXX / 3DS, carpeta llamada MHGU | 2 partes 7z, 2.331.029.628 bytes | CIA derivado, TMD previo `0004000000197100`; hash completo | No acredita edición Switch ni GU occidental; base cifrada |
| Parche MHXX / 3DS | 1 CIA, 36.897.728 bytes | NCCH sin cifrar ya disponible, RomFS y ExeFS inspeccionados | Su contenido no representa el juego base completo; traducción/compatibilidad no probadas |
| MHGU / Switch | 0 identificados | Investigación documental | Sin imagen ni RomFS local de Switch |
| Frontier Z/ZZ / PS Vita | 0 identificados | Investigación documental y coordinación | Sin archivos locales de cliente Vita; sin confirmar Title ID/revisión/formatos particulares |

Los hashes completos de los siete originales están en [audit-summary.json](audit-summary.json). No se renombraron ni aplicaron parches a originales. MHFU es Freedom Unite: no aporta evidencia de Frontier. MH3U Wii U y Portable 2nd G aparecen en fuentes de investigación, pero no se dispone aquí de esos juegos.

## Inventario de formatos y grado de verificación

Grados: **L** lectura/hash local; **E** estructura limitada comprobada; **D** soporte declarado documentalmente; **H** hipótesis funcional; **B** bloqueo. Ningún grado E de este informe equivale a validación visual o jugable.

| Sistema | Evidencia local / formatos candidatos | Herramienta aplicable y grado | Pendiente concreto |
|---|---|---|---|
| Contenedores | CIA/TMD; NCCH; ExeFS/RomFS; ISO9660; 7z dividido; ARC LE v17 | Sondeos propios L/E; CTRTool y 7zr portátiles ya presentes, uso anterior documentado; Arc Explorer D | Parser independiente del ARC y comparación por hash; no usar sus opciones de cifrado |
| Modelos y esqueletos | 83 cargas con firma MOD y versión 230; cabeceras de huesos/mallas/materiales | `probe_resource_headers.py` E; RevilLib D | Validar offsets, índices, matrices bind, pesos, jerarquía sin ciclos, ejes y unidades; conteo de huesos no prueba rig utilizable |
| Animaciones | 4 LMT67; 83 slots no vacíos en total bajo tabla de punteros 32-bit LE | Lector limitado E; RevilLib D | Decodificar una pista, comprobar interpolación y asociación a hueso; FPS/duración en segundos desconocidos |
| Movimientos y combate | Etiquetas de tipos `spactdata`, `hunterartsdata`, `commonscript` en diccionario externo | Correspondencia de type_id D/H; no se interpretaron valores | Contrastar esquema y referencias con código; no asignar por nombre daño, cancelaciones o invulnerabilidad |
| Hitboxes / hurtboxes | Sin estructura funcional validada | B/H | Buscar referencias desde código legible, distinguir volúmenes de ataque/recepción, hueso, espacio y ventana temporal; una animación no define el impacto |
| IA | Módulos `.cro` presentes, nombres `roEm...` en RomFS; firma CRO0 observable | L/E de firma; Ghidra como candidato D | Tabla de carga/relocación y referencias verificadas antes de llamar «IA» a un módulo; no se identificaron estados o decisiones |
| Escenarios y colisiones | `areacommonlink.xfs` por type_id; no malla de colisión ni navegación comprobadas | D/H | Separar geometría visible, colisión física, navegación y cambios de área; punteros y coordenadas pendientes |
| Interfaz y textos | 2.637 cargas con firma GMD; 220 TEX; 83 MRL. Type_id añade 143 `gui` y 70 `ean` | L/E de firma; Kuriimu2/RevilLib y biblioteca gmd D | Validar versión, dimensiones/swizzle, materiales, fuentes y layout; un GMD no valida todo HUD |
| Audio | PSP SND0.AT3 tiene RIFF/WAVE; ICON1.PMF tiene PSMF. 531 type_id `soundsourceadpcm.madp` | L/E de cabecera PSP; vgmstream D | Identificar codec, canales, sample rate y loop antes de decodificar; MADP aún etiqueta documental, sin reproducción |
| VFX | 51 type_id `efl`, 5 `pec`, 4 `pel`; no efecto reproducido | D/H | Emisores, curvas, texturas, blend, dependencias y eventos; etiquetas no prueban semántica |
| Misiones | Type_id: 2.520 `questdata`, 5.119 `rem`, 3.258 `setemmain`, 2.298 `esl`, 1.218 cada `supplylist`/`questplus`/`questlink` | Lectura/hash L; diccionario D; MHGUQuestEditor para Switch D | Interpretar una revisión 3DS con límites e IDs; no aplicar offsets de Switch a MHXX 3DS |
| Ejecutables | PSP BOOT ELF32 MIPS; EBOOT envuelto ~PSP. Parche: ExeFS `.code`; CRO/CRS | L/E; PRXTool/Ghidra candidatos D | Loader, segmentos, compresión y relocaciones antes de desensamblado; no ejecutar juegos |

Las firmas de 21.696 cargas son: GMD 2.637, TEX 220, MRL 83, MOD 83, LMT 4 y **18.669 sin clasificar por firma**. El cruce con [diccionario de Arc Explorer](https://github.com/Paxlord/pax_arc_explorer/blob/main/data/dti_ext.json) añade nombres de tipo; no convierte esas 18.669 cargas en formatos semánticamente validados. [Conteos por type_id](entry-type-labels.json) conserva cada identificador y etiqueta. No se clasificó por armas ni se atribuyeron recursos a movimientos específicos.

La procedencia de cada MOD/LMT y las observaciones completas están en [resource-headers.json](resource-headers.json). La clave estable para compartir resultados es `(SHA256 original, SHA256 contenedor, índice ARC, SHA256 carga)`; para animación añadir slot. No deducir parentesco funcional solo por hashes iguales.

## Ejecutables: avance nuevo y precaución interpretativa

[plain-executables.json](plain-executables.json) conserva únicamente metadatos. BOOT.BIN: 1.910.044 bytes, SHA-256 `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`. Tiene 300 cabeceras de programa y 620 cabeceras de sección declaradas. Se comprobó el límite de la tabla de programas y sus rangos físicos; no se validó completamente la tabla de secciones, las relocaciones ni la fidelidad del código. Hay muchas entradas PT_NULL; no deben tratarse como segmentos cargables. El ELF visible no autentica el ISO.

El ExeFS del parche MHXX ocupa 7.677.952 bytes en offset 10.752 del NCCH derivado. `.code`: 7.419.468 bytes, SHA-256 `251399daef52a2a23bf77375a94ac4e6746bacb9b6d67e1b0654c82f57964f93`. Su compresión declarada en el exheader previo sigue sin decodificar. Coincidir con hashes embebidos comprueba integridad interna, no firma/autenticidad. No se exportaron ejecutables ni proyectos de desensamblado.

## Herramientas y fuentes públicas

El [registro de fuentes](sources.md) separa soporte anunciado, documentación de formatos y pruebas locales. Se revisaron fuentes de autores y código público; resultados de foros se usaron como pistas, sin usarlos como prueba de compatibilidad. Se investigaron PSP, 3DS, Switch y Vita; no es una afirmación de haber agotado toda la web.

No hicieron falta instalaciones nuevas: Python del runtime Work y las herramientas portátiles previas bastaron para el alcance legible. 7zr y CTRTool fueron hasheados en el inventario físico de esta revisión; su procedencia anterior se conserva en PR3. No se ejecutaron mhtools, ReFrontier, importadores Blender ni servidores: varias utilidades integran descifrado automático y exigirían separar antes una ruta de lectura de datos ya legibles. No se buscaron claves ni se probó esa funcionalidad.

Para Frontier, FMOD/FSKL/MOT y contenedores de escenario PAC/JKR son formatos descritos por el importador público; **no observados en archivos Vita locales**. FMOD en ese contexto es modelo, no identificación del middleware de audio homónimo. ReFrontier/FrontierTextHandler describen BIN y perfiles de datos, pero el perfil `zz` documentado se refiere a PC. Erupe declara compatibilidad de servidor con Vita; no reconstruye por ello IA cliente, animaciones o hitboxes. Z y ZZ deben fijarse por revisión concreta, no por carpeta o vídeo.

## Repositorio y PR3

Consulta GitHub: main `0067706f7baf01465f335b5509a1ce62c6b2d02f`; [PR3](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/3) abierta, borrador, head `51b8904c84de6bdf241f731bd15a6f8ea56528b6`, base declarada `c22b5a849568114c4a1f45938f669bfa5c294b33`, `mergeable=false` según API. No se resolvieron conflictos ni se alteró esa rama.

PR3 reúne inventario y primer piloto; los archivos locales de `inventory-work` contienen avances posteriores sobre banco y cabeceras, con cambios sin commit. La descripción remota aún habla de 782 entradas del piloto. No se confundió ese estado remoto con los 21.696 resultados vueltos a comprobar aquí. También contiene estados antiguos del monitor; no copiarlos sobre main.

Dos intentos de clonación local fallaron al arrancar el shell interno de Git (`NtCreateDirectoryObject`, acceso denegado). Se usó la API GitHub para una **rama remota independiente** `research/stt-engineering-resources-20261021`, creada desde main, y una carpeta de entregables nueva `research-work`. No es un checkout administrado ni se cambiaron ramas de otros Work. Solo se añaden rutas nuevas bajo `docs/research/stt-re-20261021/` y `tools/stt_re/`; no se reescriben monitor, README general, fichas ni PR3.

## Prioridades y experimentos reproducibles

| Prioridad / ID | Experimento y entrada | Criterio de aceptación | Bloqueo / área |
|---|---|---|---|
| P0 / RE-01, ejecutado | Auditoría de lectura y banco sobre raíces locales | 7/7 originales iguales; 21.696 cargas y 8.823 objetos con hash coincidente; errores explícitos | Superado en este recorrido; 02/10 |
| P0 / RE-02, ejecutado | Sondear BOOT.BIN y ExeFS plaintext | Rangos de programas dentro del archivo; tres hashes ExeFS y cabecera coincidentes | Superado a nivel limitado; secciones/código pendientes; 02 |
| P1 / RE-03 | MOD230 pequeño y LMT67 locales, identificados por hash/índice | Decodificar una pista y una malla, comprobar índices/pesos/jerarquía y vista previa local; registrar ejes/FPS desconocidos | Codecs y vínculo rig/clip; 07/10 |
| P1 / RE-04 | ELF BOOT.BIN de hash registrado; PRXTool/Ghidra fijados a versión/hash | Verificar secciones/segmentos y una referencia de función con dirección y confianza; registrar anomalías PT_NULL | Loader Allegrex/VFPU y posible contenido empaquetado; 02 |
| P1 / RE-05 | Una carga `questdata` y dependencias del mismo ARC | Esquema 3DS acotado, IDs y límites cruzados; sin importación al juego | No aplicar esquemas Switch automáticamente; 03/10 y 09 |
| P1 / RE-06 | Una muestra de audio ya legible, fuera de Git | Cabecera/codec/canales/sample rate/loop coincidentes entre parser y decoder | Codec MADP no confirmado; 07/10 |
| P1 / RE-07 | Fuentes primarias Frontier por revisión/plataforma | Movimiento, condición y transición con referencia y timestamp; distinguir diseño STT | Sin cliente Vita local ni parámetros históricos acreditados; 04 |
| P2 / RE-08 | Referencias de código/datos para colisión, IA y eventos | Volumen, espacio, hueso, unidades y ventana demostrados; reproducir con datos propios | Ningún esquema funcional validado; 02/03/05/07/10 |
| B / RE-09 | MH3U/MH4U/MHXX base y Frontier/Switch ausentes | Entrada de análisis legítima ya legible, revisión y hash | Cifrado o ausencia; no buscar claves, eludir DRM ni descargar juegos |

Repetir desde la carpeta de proyecto usando Python 3.11+ real (el alias WindowsApps `python.exe` falló en este entorno):

```powershell
& $python tools/stt_re/audit_accessible.py --root $projectRoot --out "$projectRoot/analysis-local/stt-re-audit-repeat"
& $python tools/stt_re/probe_plain_executables.py --root $projectRoot --output "$projectRoot/analysis-local/stt-re-audit-20261021/plain-executables-repeat.json"
```

`$python` debe apuntar al intérprete del runtime Work, y `$projectRoot` a la carpeta que contiene `Juegos`, `analysis-local` e `inventory-work`. El segundo comando usa deliberadamente el manifiesto PSP de esta ejecución. La auditoría requiere el banco previo y su inventario base en esas ubicaciones. Destino nuevo obligatorio; no borrar evidencias para repetir. El recorrido incluye nuevos informes/bancos, de modo que el total físico cambiará; comparar conjuntos de rutas y hashes de originales/recursos, no exigir igualdad del total global. Nunca colocar estos destinos en el repositorio público.

Validación realizada: ejecución real completa de RE-01/02 y **18 pruebas sintéticas existentes** del lector ARC y cabeceras MOD/LMT aprobadas. Son las pruebas de los parsers utilizados, no una nueva validación del monitor ni del hardware. No se atribuye CI o prueba visual a esta revisión sin evidencia específica.

Las 18 pruebas también se repitieron correctamente desde las copias entregadas en `research-work/tests`, ajustadas únicamente a la nueva ruta `tools/stt_re`. Para repetir en el checkout publicado: `python -m unittest discover -s tests -p 'test_stt_re*.py' -v`. El cruce de etiquetas puede repetirse con `tools/stt_re/label_catalog.py --bank <catalog.sqlite> --dictionary <dti_ext.json> --output <destino-nuevo.json>`; diccionario público exacto identificado por blob en provenance.json.

## Coordinación y entrega

Se leyeron los chats de Diseño 02, 03, 04, 05, 07 y el chat «Confirmación diseño integración» (área 10). [coordination.md](coordination.md) registra interfaces, mensajes enviados y estado de recepción. Las revisiones documentales de otros chats no son inspecciones independientes de los bytes. No se les encargaron modificaciones de consola ni implementación.

Solo se publican informes, metadatos y código propio. Catálogo físico detallado, objetos comerciales, CIA/ISO y muestras permanecen locales. No se descargaron juegos, claves ni recursos comerciales. El descifrado autorizado se realizó en el PC con las entradas existentes y queda detallado por etapa. Sin FTP, montajes ni cambios de firmware, plugins o archivos de PS Vita desde este encargo.

# Continuación autorizada: PSP y Frontier local

**Nota editorial de consolidación (22-10-2026):** Este documento conserva los cortes parciales de Frontier. La copia local se completó después (A09); aquí no se sustituye la verificación independiente de50candidatos por un nuevo cotejo de8261archivos. Véase [el índice de aceptaciones](acceptance-index.md).

21-10-2026, Europe/Madrid. El usuario excluyó GU Switch y autorizó continuar. Alcance actual: MH3U/MH4U/MHXX 3DS, MHFU PSP y Frontier Vita. Las referencias históricas a Switch del informe inicial se conservan como antecedentes, sin nuevas pruebas ni requisitos sobre esa plataforma.

## Frontier Vita: material nuevo, todavía incompleto

La inspección inicial había registrado ausencia de Frontier. Ahora existe `Juegos/MHF-Vita/PCSG00350/app/PCSG00350` en el PC. Se examinó exclusivamente esa carpeta local. No se ejecutaron scripts de copia/FTP presentes en otros trabajos, no se accedió a la consola ni se alteró su estado o el banco compartido.

La enumeración cambia mientras otro trabajo incorpora archivos. Por ello se guardaron dos recibos locales independientes, con fecha, rutas, tamaños, SHA-256 y errores. No se esperó ni dio por finalizada aquella operación, que queda fuera de este encargo.

| Lectura | Fecha UTC | Enumerados | Lectura completa estable | Resultado |
|---|---|---:|---:|---|
| Primera | 2026-10-21 06:34:41 | 1.027 | 1.026 | Un `.partial` desapareció entre enumeración y apertura; registrado como error, código de salida 1 |
| Segunda | 2026-10-21 06:36:21 | 1.653 | 1.652 | 887.956.306 bytes en archivos leídos; un `.partial` excluido explícitamente, sin fallos en los otros archivos; código 0 |

Durante la segunda lectura aparecieron 30 rutas adicionales y desapareció una ruta parcial. **No es un volcado completo, una instantánea atómica ni una validación de todos los archivos que existirán al terminar la copia.** Los conteos no son archivos extraídos ni descifrados. La exclusión de `.partial` evita que un archivo en transferencia se trate como entrada terminada.

Único tipo identificado positivamente por el sondeo de firmas en la segunda enumeración: SFO. Sus campos legibles indican:

- TITLE_ID: `PCSG00350`.
- TITLE: `モンスターハンター フロンティアＧ`.
- APP_VER y VERSION: `01.00`; CATEGORY: `gd`.

Esto identifica metadatos de la aplicación base Frontier G, **no confirma actualización Z o ZZ**, integridad del cliente completo ni autenticidad de distribución. No se han inspeccionado contenidos de claves o licencias.

Los otros 1.651 archivos leídos quedaron `unclassified` bajo las firmas reconocidas por este lector. Hay extensiones `.pac`, `.mot`, `.gab`, `.txb`, `.bin`, `.mus`, `.suprx` y `.png`, pero no se convirtieron sus nombres en formatos confirmados. Tampoco `eboot.bin` presentó ELF o SCE en el offset cero bajo este sondeo. No se forzó un loader basándose en el nombre.

Hipótesis: una capa de protección/almacenamiento podría explicar cabeceras no reconocidas incluso en imágenes y ejecutables. **No se ha demostrado esa causa ni se ha identificado una capa exacta.** La ausencia de coincidencia con una lista finita de firmas también puede deberse a una variante de formato o a entradas no interpretadas. No equivale a corrupción demostrada. No se ejecutó ReFrontier para intentar retirar capas desconocidas.

Como referencia, [ReFrontier](https://github.com/Houmgaor/ReFrontier) describe ECD/EXF y JKR y puede descifrar automáticamente; la [documentación del importador Frontier](https://github.com/Houmgaor/MHFrontier-blender-addon) describe FMOD/FSKL/MOT después de preparar los datos. Son capacidades documentales, no prueba de que estos bytes Vita estén ya en esos formatos ni de que un flujo PC sea aplicable a este material.

## MHFU: validación ampliada del ELF ya legible

Entrada: `PSP_GAME/SYSDIR/BOOT.BIN` leída dentro del ISO, sin exportar código. SHA-256 permanece `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`; 1.910.044 bytes. El manifiesto previo fija offset/tamaño/hash y el nuevo lector exige coincidencia antes de analizar.

Resultados de lectura estructural:

- ELF32 little-endian, ET_EXEC, machine 8 (MIPS).
- 300 cabeceras de programa: **1 PT_LOAD y 299 PT_NULL**. No son 300 regiones cargables.
- PT_LOAD: offset 9.652, dirección virtual 142.622.720, 1.866.384 bytes de archivo y 22.418.560 de memoria declarada, flags 7, alineación 16.
- Entry `0x08906934`: cae en la porción respaldada por archivo de un PT_LOAD ejecutable; offset físico relativo a BOOT.BIN **1.068.776**.
- **620 entradas de sección**: 1 NULL, 1 STRTAB, 313 PROGBITS, 304 REL y 1 NOBITS. Tablas, rangos físicos aplicables y nombres comprobados dentro de límites.
- No hay SHT_SYMTAB ni SHT_DYNSYM estándar: **sin tabla estándar de símbolos funcionales**. La STRTAB observada sirve a nombres de sección; no se presenta como símbolos de funciones.

El contenido de las 304 secciones REL no se ha validado semánticamente. No asumir que las reglas genéricas ELF/MIPS resuelven todas las convenciones PSP/Allegrex. Quedan loader, relocaciones, imports, instrucciones y referencias de datos antes de identificar funciones o plantear recompilación.

Se añadieron siete pruebas sintéticas que comprueban mapeo de entry, entry solo en memoria, tablas/secciones fuera de límite, nombre inválido, tamaño de archivo mayor que memoria y endian incompatible. Las **25 pruebas** de esta rama (18 anteriores + 7 nuevas) pasan. No se ejecutó el juego, no se instaló un loader y no hay ensayo físico nuevo.

## Reproducción y evidencias

Herramientas propias nuevas: `tools/stt_re/inspect_frontier_local.py` e `inspect_elf_sections.py`. Solo lectura de entradas; los informes usan creación exclusiva y quedan fuera de los juegos.

```powershell
& $python tools/stt_re/inspect_frontier_local.py --root "$projectRoot/Juegos/MHF-Vita/PCSG00350" --out "$projectRoot/analysis-local/frontier-local-new"
& $python tools/stt_re/inspect_elf_sections.py --iso "$projectRoot/Juegos/MHFU/Monster Hunter Freedom Unite.iso" --manifest "$projectRoot/analysis-local/stt-re-audit-20261021/psp-files.json" --output "$projectRoot/analysis-local/mhfu-elf-sections-new.json"
& $python -m unittest discover -s tests -p 'test_stt_re*.py' -v
```

`$python` es la ruta real de Python del runtime y `$projectRoot` la carpeta de proyecto. Cambiar los destinos para cada ejecución, sin borrar los anteriores. La primera herramienta informa de altas/bajas durante la lectura; un código 0 no afirma que el conjunto sea estático ni completo.

Publicable: [resumen y recibos](continuation-summary.json), método, código propio y pruebas sintéticas. Inventario detallado y las 620 secciones permanecen locales en las rutas y hashes del recibo. Sin contenido comercial incorporado a Git.

## Prioridades y bloqueos actualizados

1. **Frontier P0:** comprobar localmente una copia terminada contra su recibo, cuando esté disponible. No actuar sobre la transferencia ni la consola desde esta tarea. Determinar base/parche y revisión antes de afirmar Z/ZZ.
2. **Frontier P1:** identificar la capa exterior con documentación de formato y una cabecera reproducible; distinguir firma ausente de corrupción/cifrado. No ejecutar automáticamente herramientas que descifran o escriben junto al original.
3. **PSP P1:** contrastar loader/imports/relocaciones con especificación PSP; mapear una referencia y su confianza, sin dar por identificado combate/IA.
4. **3DS P1:** continuar con recursos legibles del parche MHXX y su asociación rig/pista. Las bases cifradas siguen bloqueadas; no se buscaron claves ni se descifraron.

Esta ejecución amplía el inventario y valida más estructura; **no afirma haberlo descifrado todo**. GU Switch queda fuera del trabajo futuro. Sin cambios de archivos de consola, firmware, plugins, montajes ni FTP.

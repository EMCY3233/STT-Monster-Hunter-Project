# Base MH4U EUR: una partición ejecutable sin extracción

**Nota editorial de consolidación (22-10-2026):** La ausencia de descompresión describe solo este sondeo. A26validó después una única BLZ; los datos anteriores y la corrección del campo romfs_read se conservan. Véase [el índice de aceptaciones](acceptance-index.md).

2026-10-21. Aceptación Área02 sobre la base NCSD .3ds encontrada durante [la prueba Citra](citra-current-inputs.md), **distinta del update MHXX**. Se inspecciona únicamente la partición0, ExHeader y ExeFS; no se repite arranque ni se produce/descomprime código o RomFS.

## Identidad y alcance de lectura

Original local `Juegos/Monster Hunter 4 Ultimate (Europe) (En,Fr,De,Es,It)/Monster Hunter 4 Ultimate (Europe) (En,Fr,De,Es,It).3ds`,4.294.967.296bytes. SHA256 antes/después **`3832beef353d134bcba6ef83dc987e7ae228c43dc32a6ba52519f5f103f52581`**, coincide con el recibo Citra anterior. La adquisición externa y revisión exacta del juego siguen sin acreditarse; no inferir equivalencia con la CIA por nombre.

Partición0: offset **16.384**, longitud **2.727.489.536**, tamaño NCCH declarado coincidente y dentro del original. ProgramID NCCH y ExHeader **0004000000126100**, mutuamente coincidentes. Flags NCCH: ejecutable y no_crypto. Solo unidades512bytes y ExHeader1024bytes admitidos por este sondeo.

Lecturas estructurales registradas: **9.356.680bytes**, presupuesto64MiB; siete rangos con offset/longitud/hash en el recibo. Además se realizan **dos pasadas SHA256 completas de4GiB** para verificar el original. Esas pasadas incluyen todos los bytes del archivo, también los que pertenezcan a RomFS, sin interpretarlos ni extraerlos. No afirmar que solo se leyeron9MB en total. Ninguna otra partición NCCH se interpreta.

Fuente primaria: **Azahar2126.2, commit `219d743a1e698101fe1ab8bef43e6563126c3c27`**, [ncch_container.h](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/file_sys/ncch_container.h), blob `1559ee5dcf83aee8b197fb7510b433871c0e6b55`. Layout NCSD/NCCH, CodeSetInfo y ARM11_SystemLocalCaps. La interpretación del pie reutiliza la referencia [ncch_container.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/file_sys/ncch_container.cpp), blob `666d6037f1667ceea641cc46c7ee94cac5bee56c`. No se instala ni ejecuta Azahar.

## ExHeader, segmentos y CPU

Hash ExHeader cotejado con NCCH: **`0fc242e3ab0c8cfc2de2a0f1205438afa466ed336ebb464e038148818dfdef09`**.

| Segmento | VA | Páginas | Bytes declarados | Capacidad por páginas | Offset lógico descomprimido |
|---|---:|---:|---:|---:|---:|
| text | 1.048.576 | 3.309 | 13.549.804 | 13.553.664 | 0 |
| ro | 14.602.240 | 211 | 863.584 | 864.256 | 13.553.664 |
| data | 15.466.496 | 450 | 1.842.044 | 1.843.200 | 14.417.920 |

Alineación4096, sin solapamiento, campos de tamaño dentro de capacidad; suma **16.261.120bytes**. Stack262.144bytes y BSS636.332bytes declarados, separados. Los offsets son del **layout esperado**, no de un code.bin que se haya producido ni posiciones directas dentro del .code comprimido.

ARM11_SystemLocalCaps: core_version=2 (campo del sistema, no versión ISA); n3ds_cpu_flags=3, con solicitudes `enable_l2_cache=true` y `enable_804MHz_cpu=true`. n3ds_mode bruto1, system_mode bruto3, ideal_processor bruto0 y affinity_mask bruto1. Se conservan los modos numéricos sin asignarles tamaños de memoria o modelos de consola no cotejados. Son **solicitudes de configuración**, no mediciones de reloj ni demostración de funciones New3DS. No se acredita estado de instrucción ARM/Thumb ni extensiones CPU leyendo estos campos; no se decodificó ninguna instrucción.

## Tabla ExeFS y compresión

ExeFS: offset relativo a partición11264 (absoluto27648), longitud9.355.264bytes. Hash del bloque tabla coincide con NCCH: `2cd39b00fa40aa68f29dbc9d8bb9828618700b8a0bc6c416debbc3d7e233fe0e`. Entradas sin solapamiento y dentro del rango; sus tres hashes de contenido coinciden con la tabla:

| Entrada | Offset absoluto | Bytes | SHA256 |
|---|---:|---:|---|
| .code | 28.160 | 9.091.360 | `655e5b4f896d16ab1a745c3f516ef13c6cf482f3aa676b5c9927f3fa8ee57d83` |
| banner | 9.119.744 | 248.744 | `047d6d78587066d7cadcf9802329cce90cd1647204a55d71ce24559509a14634` |
| icon | 9.368.576 | 14.016 | `5f0e0c0ec9eb85273cc392c5b67e4b487825a44e72c56c08771cd9857f4ab225` |

Solo se leen para hash; no se exportan ni muestran icon/banner o bytes ejecutables. Flag ExHeader0x01, bit0 activado: .code comprimido. Pie BLZ: top9, bottom9.091.284, incremento7.169.760, prefijo declarado76 y flujo declarado9.091.275bytes. **9.091.360+7.169.760=16.261.120**, igual a las páginas antes de intentar descompresión. El pie es coherente, pero **no prueba consumo válido del flujo**: no se llamó al decoder ni se reservó una salida descomprimida.

## Reutilización y aceptación

Herramienta propia `tools/stt_re/probe_ncsd_executable.py`, lectura por rangos de un contenedor grande. Reutiliza **sin cambios** `inspect_ncch_code.blz_footer` y `map_ncch_entry_reference.map_reference`. El segundo valida el layout declarado con su tamaño esperado; no se presenta ese resultado como mapeo respaldado por archivo descomprimido. Reusar el lector completo MHXX habría exigido cargar una partición de2,7GB y llamado al decoder: se evita esa operación mediante la interfaz acotada.

Siete pruebas sintéticas nuevas aprobadas: partición válida no comprimida sin extracción, partición fuera del archivo, cifrado rechazado, flag no ejecutable, ExHeader alterado, entrada ExeFS alterada y lectura corta. No se repiten las124pruebas anteriores porque los dos validadores compartidos no cambian. No se presenta131 como suite completa ejecutada. Ayuda CLI verificada. [Recibo público](mh4u-ncsd-executable-evidence.json); recibo original privado en `analysis-local/mh4u-ncsd-executable-20261021/receipt.json`.

El recibo inicial llamó `romfs_read=false` al estado del sondeo estructural; en la aceptación pública se corrige el nombre a `romfs_parsed_or_extracted=false`, conservando intacto el recibo original. Las dos pasadas de hash completas se declaran explícitamente. Solo se crean metadatos JSON; banco, original y otras ramas permanecen sin modificaciones.

Reproducción: `probe_ncsd_executable.py --input <NCSD existente> --expected-sha256 3832beef353d134bcba6ef83dc987e7ae228c43dc32a6ba52519f5f103f52581 --out <JSON nuevo>`. Rechaza sobrescribir salida. El nombre de las entradas nunca se usa para construir rutas de extracción.

**Aceptación cerrada:** base legible con partición ejecutable coherente, ExHeader/ExeFS íntegros, flags/segmentos/modos declarados y pie BLZ compatible con el layout reutilizado. **Próximo bloqueo:** queda por validar el flujo BLZ real. La siguiente aceptación concreta sería descomprimir solo este .code, con los límites y pruebas existentes, registrar consumo/cobertura/hash y conservar resultado privado. No demostraría por sí sola funciones, IA, hitboxes, estabilidad o fidelidad visual. No se inicia esa fase en este sondeo.

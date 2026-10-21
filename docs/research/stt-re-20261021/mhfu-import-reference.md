# MHFU: una referencia estática de tabla de imports

Fecha: 2026-10-21. Se consultaron primero los recibos ELF previos y se reutilizó el único artefacto ya catalogado. No se reextrajo ISO, ejecutó ELF/juego/emulador/consola ni se repitió la comprobación de las 620 secciones. Se comprueban directamente **dos cabeceras de sección, un program header y una sola referencia** del primer registro de imports.

## Artefacto y especificación primaria

Entrada existente: `analysis-local/emulators/ppsspp-1.20.4/memstick/PSP/SYSTEM/DUMP/ULES01213_EBOOT.BIN`, 1.910.384 bytes, SHA-256 `64937c521286fc8423076e644089881c5fe051bed2565e5061dda8aec0b45e10`. Su prefijo de 1.910.044 bytes coincide con BOOT.BIN, SHA-256 `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`; se verifican ambos hashes contra recibos anteriores. Los **340 bytes finales no interpretados se excluyen** de todas las direcciones y límites. No se crea ni publica otra copia del ejecutable.

Referencia primaria comunitaria PSP: PSPSDK, commit **`6ef2b21dc440ef8d4125f000301faaa2a470975e`**:

- [src/kernel/psploadcore.h](https://github.com/pspdev/pspsdk/blob/6ef2b21dc440ef8d4125f000301faaa2a470975e/src/kernel/psploadcore.h), blob `cd17040b7300de4bb97a2004b13e96f17fcda74f`: SceLibraryStubTable define libname, versión/atributos, len, vstubcount, stubcount, nidtable y stubtable; **len × 4** determina tamaño real, no sizeof de la versión ampliada de la estructura.
- [src/base/pspstub.s](https://github.com/pspdev/pspsdk/blob/6ef2b21dc440ef8d4125f000301faaa2a470975e/src/base/pspstub.s), blob `ca04503afb6f72a37dfa270cc2d60d3cebfc125b`: STUB_START sitúa registro de cinco palabras en `.lib.stub` y la tabla de identificadores en `.rodata.sceNid`.

Es una implementación/documentación de desarrollo PSP de código abierto, no una especificación propietaria Sony. No se instala ni ejecuta PSPSDK.

## Una referencia comprobada

ELF32 LE, ET_EXEC, MIPS. La sección **11, `.lib.stub`**, comienza en VA `0x0890E6D4`, offset `0x0010CC88` (1.100.936), tamaño 680 bytes. Solo se interpreta su **primer registro**: len=5 palabras, 20 bytes; tres funciones y cero variables. No se enumeran los demás registros ni se resuelven nombres.

| Elemento de la misma referencia | VA estática ELF | Offset en archivo | Sección |
|---|---|---|---|
| Campo nidtable, primer registro +12 | `0x0890E6E0` | `0x0010CC94` (1.100.948) | 11, `.lib.stub` |
| Destino del puntero | `0x0890EC78` | `0x0010D22C` (1.102.380) | 18, `.rodata.sceNid`, offset relativo cero |

La cantidad de tres funciones requiere 12 bytes de tabla NID; caben en los 3.200 bytes de la sección destino. Se verifica alineación y que el rango completo esté respaldado por archivo, no por BSS.

Dos cálculos independientes de límites deben coincidir:

1. Sección: `target.sh_offset + (VA − target.sh_addr)` = 1.102.380.
2. PT_LOAD 0: `p_offset + (VA − p_vaddr)` = `9.652 + (143.715.448 − 142.622.720)` = 1.102.380.

Se coteja ese único PT_LOAD con la evidencia previa y se comprueba su rango físico. Se comparan los campos de las dos cabeceras de sección seleccionadas con el recibo anterior. Los nombres provienen de la validación de secciones ya aceptada sobre el mismo prefijo de hash idéntico; no se vuelve a recorrer la tabla completa.

## Confianza y límite

**Confianza estructural alta** para identificar un registro de tabla de imports y esa correspondencia dirección↔offset↔sección: layout PSPSDK, tamaño y conteos coherentes, puntero alineado, destino en sección esperada y concordancia sección/PT_LOAD. Son direcciones estáticas del ELF, no observaciones de memoria en ejecución.

No se leen/publican valores NID ni bytes de código, nombres comerciales o cadenas. No se identifica una función concreta, biblioteca resuelta, relocación aplicada, callsite ni comportamiento de combate/IA. La existencia de un import no demuestra su invocación. La validación previa de 304 secciones SHT_REL no equivale a relocaciones presentes o aplicadas; no se investiga esa vía en este ensayo.

## Reproducción y aceptación

`tools/stt_re/map_psp_import_reference.py --elf <artefacto existente> --baseline <mhfu-elf-sections.json previo> --dump-receipt <comparison.json previo> --out <JSON nuevo>`. Presupuesto de artefacto 4 MiB; verifica hashes, excluye cola sin interpretar, exige una sola tabla/registro del alcance fijado y rechaza rangos solo en memoria o mapas discordantes. No exporta ejecutable ni identificadores.

Evidencia privada: `analysis-local/psp-import-reference-20261021.json`. [Recibo público](mhfu-import-reference-evidence.json), sin bytes comerciales. Cinco pruebas sintéticas nuevas aprobadas: mapa coherente, rechazo BSS, array que cruza el fin físico, longitud de registro ajena al alcance y desacuerdo sección/segmento. No se repitió la batería/censo completo ni se modificó el banco u otras ramas.

**Aceptación cumplida:** una tabla identificada y una referencia estática reproducible mapeada con invariantes suficientes. No se amplía automáticamente a las otras entradas, relocaciones o funciones. La identificación funcional requeriría otra aceptación y evidencia de vínculo con un NID público; queda fuera de este ensayo.

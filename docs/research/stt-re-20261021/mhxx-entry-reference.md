# MHXX update: una referencia de inicio derivada del loader

2026-10-21. Área02: una única VA↔offset↔segmento sobre el `code.bin` existente, sin repetir BLZ, volcado, arranque, desensamblado ni acceso al banco. Base MHXX cifrada y update se mantienen separados.

## Qué establece la fuente

El ExHeader declara `CodeSetInfo.text.address`, tamaños/páginas y otros campos; **no se trata aquí como un campo entrypoint explícito**. La referencia de inicio se obtiene de la asignación del loader, no solo de que text sea el primer segmento.

Fuente primaria **Azahar2126.2, commit `219d743a1e698101fe1ab8bef43e6563126c3c27`**:

1. [loader/ncch.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/loader/ncch.cpp), blob `842453fcbdace1f42a6ac17e9d6b15595fa8064d`, líneas142–143 y171: offset text=0, dirección tomada de ExHeader; asigna `codeset->entrypoint = codeset->CodeSegment().addr`.
2. [kernel/process.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/hle/kernel/process.cpp), blob `e272bd5f81389b73313fd3e77e3bd89cfb6a3d28`, líneas234–245 y265: copia desde offset de segmento a VA, con permisos ReadExecute para text, Read para ro y ReadWrite para data; pasa el entrypoint a SetupMainThread.
3. [kernel/thread.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/hle/kernel/thread.cpp), blob `03c9aa9bedd594fcb2fc2232b95f0f15f482ebcb`, líneas376–381,428 y487–489: crea el hilo con esa dirección, fija el PC y deriva CPSR.T del bit0 de entry_point.
4. [ncch_container.h](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/file_sys/ncch_container.h), blob `1559ee5dcf83aee8b197fb7510b433871c0e6b55`: respaldo del layout de ExHeader.

Esto describe la ruta de carga revisada, sin modificaciones externas. Overrides, parches, plugins y comportamiento real del sistema no se prueban en esta aceptación. Azahar no se instala ni ejecuta aquí.

## Una referencia y su respaldo

Se reutiliza [la salida BLZ](mhxx-code-blz.md),13.045.760bytes, SHA256 **`6f66928e0deecdcd20c3b0e67c614e6313dfe92c8dc0b9ba2d7a906d1efe4fe8`**. Se verifican ese hash, longitud y los tres segmentos contra el recibo anterior; se relee el ExHeader original, cotejando hash NCCH y campos. No se aplica BLZ otra vez.

| Campo | Resultado |
|---|---|
| Inicio derivado del loader | **0x00100000 / 1.048.576** |
| Referencia única | VA[0x00100000,0x00100004) |
| Segmento | text |
| Fórmula | offset text0 + (VA0x00100000 − base text0x00100000) |
| Offset en code.bin | **0**, rango[0,4) |
| Respaldo | dentro de11.478.072bytes declarados de text y de la capacidad11.481.088; no padding/BSS |
| Permisos de la ruta Azahar | **r-x**, derivados de process.cpp, no de flags de permisos inventados en ExHeader |
| CPSR.T inicial esperado | **0**, porque entry_point es par |
| Estado inicial esperado | **ARM/A32**, por configuración del contexto del loader |

El rango de cuatro bytes es una referencia de archivo: **no se han decodificado esas palabras ni se afirma que constituyan una instrucción válida o una función**. No se exportan bytes, opcodes, textos o desensamblado. ARM/A32 es una inferencia de alta confianza para la inicialización que implementa esta versión del emulador; no certifica el estado observado en consola, extensiones ISA concretas, instrucciones posteriores ni transiciones a Thumb.

NCCH original SHA256 `1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473`; ExHeader SHA256 `93db6de01e1bdb19f80352456487ca6c3e26d7122577179dfa86e3e23e531941`. NCCH y code.bin conservan hash antes/después. Solo se escribe JSON nuevo; no se genera otro binario.

## Reproducción y aceptación

Herramienta propia `tools/stt_re/map_ncch_entry_reference.py --ncch <NCCH existente> --code <code.bin existente> --receipt <recibo BLZ existente> --out <JSON nuevo>`. Verifica identidad y consistencia, no descomprime. Presupuestos128MiB/64MiB; no sobrescribe el JSON. La función de mapeo exige tres segmentos ordenados, sin solapamiento, cobertura de archivo completa y rango dentro de bytes declarados, excluyendo padding y BSS.

Ocho pruebas nuevas: inicio RX, delta en ro, rechazo de padding, cruce de fin declarado, BSS no respaldado, segmentos solapados, archivo truncado y tamaño de referencia cero. Suite completa **124/124**, salida0; las116pruebas anteriores son su subconjunto histórico. Log privado conservado en `analysis-local/mhxx-entry-reference-20261021/tests.log`. [Recibo público](mhxx-entry-reference-evidence.json), sin instrucciones comerciales.

**Aceptación cerrada:** asignación explícita de entry en fuente versionada, una VA↔offset↔segmento respaldada y permisos/estado inicial documentados por la ruta del emulador. **Bloqueo siguiente:** no hay observación de ejecución del update ni validación independiente del código descomprimido; no se atribuye semántica a esa dirección. El paso que aportaría evidencia distinta es contrastar el mapa con otro lector independiente sobre esta misma salida, antes de proponer desensamblado o atribuciones funcionales. No sustituir la falta de base ejecutable por otro arranque del update aislado.

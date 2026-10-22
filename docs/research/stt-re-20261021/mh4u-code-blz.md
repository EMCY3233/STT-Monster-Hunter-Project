# Base MH4U: una descompresión BLZ de .code

2026-10-21. Siguiente aceptación explícita del [sondeo de partición0](mh4u-ncsd-executable.md). Solo se descomprime su .code; sin RomFS, otro ejecutable, arranque, claves o cambios al banco. No es el update MHXX.

## Cadena de identidad y límite de verificación

Se fija el recibo privado anterior por SHA256 **`6b7b06ac0ecd1692d591a28917201bcd284dbc45a324886cf5f71b5226386c6d`**, publicado en [la evidencia inmutable de1bdf73e](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/1bdf73ecd6f3535b2d83c105b1847f3f9806ccca/docs/research/stt-re-20261021/mh4u-ncsd-executable-evidence.json). El recibo original conserva `romfs_read=false` con su corrección de alcance ya documentada; no se reescribe.

Original:4.294.967.296bytes, SHA256 **histórico** `3832beef353d134bcba6ef83dc987e7ae228c43dc32a6ba52519f5f103f52581`. En esta etapa **no se repiten dos hashes completos de4GiB**. Se cotejan los cuatro rangos de cabeceras contra el recibo fijado y se vuelve a verificar .code antes/después. Tamaño y mtime del original permanecen iguales, pero esto **no demuestra que todos los demás bytes sigan idénticos**. `whole_image_unchanged_reverified=false` queda explícito.

Rango único .code: offset absoluto **28.160**, longitud **9.091.360**, SHA256 antes/después **`655e5b4f896d16ab1a745c3f516ef13c6cf482f3aa676b5c9927f3fa8ee57d83`**. Las cabeceras NCSD, NCCH, ExHeader y ExeFS conservan sus hashes. Lectura total de esta etapa **18.185.280bytes**: dos lecturas del rango comprimido y2560bytes de cabeceras. No se releen banner/icon ni otras particiones.

Flag0x01, bit0 de compresión activado, y pie iguales al sondeo previo. **Antes de reservar salida**, se exige que el presupuesto exacto de16.261.120bytes coincida con páginas de segmentos y con `9.091.360+7.169.760`. Si cualquiera difiere, se rechaza sin llamar al decoder.

## Reutilización y resultado

Se reutiliza sin cambios `inspect_ncch_code.decompress_blz`, adaptado y atribuido a Azahar2126.2 commit `219d743a1e698101fe1ab8bef43e6563126c3c27`, [ncch_container.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/file_sys/ncch_container.cpp), blob `666d6037f1667ceea641cc46c7ee94cac5bee56c`. [Licencia incluida](azahar-gpl2-license.md). El wrapper nuevo `decode_ncsd_code_range.py` gestiona identidad, rangos y presupuesto sin reconstruir el contenedor ni modificar el algoritmo.

**Salida privada** `analysis-local/mh4u-code-blz-20261021/code.bin`: **16.261.120bytes**, SHA256 **`63940d7ef1fecc119f9fb820f5f6a2cf2f2a5549e4a70f00319fbd6c9c1ad8dc`**. Recibo nuevo en el mismo directorio. Se comprueba también el hash del archivo escrito antes de publicar metadatos. No se publica código comercial.

- Pie: top9, bottom9.091.284 e incremento7.169.760.
- Prefijo sin comprimir: **76bytes**, comparación directa idéntica.
- Flujo: **9.091.275bytes**, consumo completo y terminación exacta en el prefijo.
- Entrada:763.240controles +3.883.803literales +2×2.222.116tokens =9.091.275bytes.
- Salida:3.883.803literales +12.377.241bytes por referencias +76bytes de prefijo =16.261.120bytes.
- Sin lectura o escritura fuera de límites aceptados por el decoder.

No existe aquí un hash esperado independiente de la salida. El hash ExeFS acredita el .code **comprimido**; el de salida identifica el derivado producido, no certifica por sí solo cada byte descomprimido.

## Respaldo real de segmentos y BSS

Los offsets que antes eran solo declarados ahora están dentro de un code.bin realmente producido, con tamaño/hash fijados. Reutilizando `map_reference` se verifica el layout completo; no se decodifican instrucciones ni se identifica estado ARM/Thumb.

| Segmento | VA | Rango de archivo por páginas | Bytes declarados |
|---|---:|---|---:|
| text |1.048.576|[0,13.553.664)|13.549.804|
| ro |14.602.240|[13.553.664,14.417.920)|863.584|
| data |15.466.496|[14.417.920,16.261.120)|1.842.044|

Rangos consecutivos, alineados y sin solapamiento; tamaños declarados dentro de capacidad. Las colas de3860/672/1156bytes no se asumen todas cero. **BSS636.332bytes**, redondeado638.976según páginas, queda fuera de la salida; no se añade ni se escribe una expansión de memoria. Stack262.144separado. Estos datos no acreditan comportamiento de una función.

## Pruebas, reproducción y bloqueo siguiente

Siete pruebas nuevas aprobadas: salida sintética explícita y prefijo, flag ausente, presupuesto discrepante antes de llamar al decoder, cabecera alterada, hash .code incorrecto, cambio de rango durante la operación y lectura corta. Ayuda CLI comprobada. El decoder y validador compartidos no cambian: **no se repite la suite histórica124**, ni se presenta una suma de campañas como ejecución completa nueva.

Reproducción: `decode_ncsd_code_range.py --input <NCSD existente> --receipt <recibo original anterior> --expected-receipt-sha256 6b7b06ac0ecd1692d591a28917201bcd284dbc45a324886cf5f71b5226386c6d --expected-output-bytes 16261120 --out-dir <directorio nuevo>`. Rechaza salida existente. [Recibo público](mh4u-code-blz-evidence.json), sin bytes, opcodes o instrucciones del juego. Se preservan todos los recibos previos y su corrección explícita sobre RomFS.

**Aceptación cerrada:** consumo real BLZ, prefijo, cobertura y terminación exactos, salida identificada y segmentos respaldados, BSS separado. **Bloqueo siguiente:** falta contraste independiente del derivado y semántica; no se afirma ARM/Thumb, funciones, IA, hitboxes o jugabilidad. La siguiente prueba útil sería contrastar esta salida/mapa con otra implementación independiente, sin volver a arrancar el juego o descomprimir otras entradas por analogía.

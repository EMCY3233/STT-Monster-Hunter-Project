# Frontier: bordes de la misma muestra, gramática aún abierta

Fecha: 2026-10-21. Se conserva `decoded.bin` de 349 bytes, SHA-256 `592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c`, y su recibo original. No se repite descompresión ni el scanner CP932 y no se leen los otros 43 JKR.

## Entradas y hechos

Se utilizó el informe de regiones elaborado por el frente central, SHA-256 `1f21e8d40993ae3f1fd7073e1e76f2df00d1b288f2457a40a85a1db929829311`, `analysis-local/logs/frontier-jkr-text-regions-20261021.json`. Aporta 14 regiones compatibles con CP932, 160 bytes en total, doce sin controles y dos con tres controles cada una. Esto es evidencia del sondeo central, no una segunda determinación de codificación ni una tabla canónica de cadenas.

Aquí se comprobaron de nuevo únicamente su hash de origen, límites, ausencia de NUL interior, terminadores NUL y no solapamiento. Las catorce regiones cumplen esos límites; el origen sigue intacto. No se exportan cadenas.

Medidas entre terminador anterior y región siguiente: diez intervalos de 11 bytes, uno de 12, dos de cero y prefijo inicial de 52. Queda un byte después del último NUL. Los intervalos no se denominan automáticamente metadatos: podrían incluir bytes de otro significado o cadenas que el sondeo no seleccionó.

Para las doce regiones con al menos once bytes anteriores, se compararon ventanas de once bytes. Ocho columnas son constantes, tres varían (2, 11 y 3 valores distintos). Es un patrón repetido observado, **no un registro de once bytes confirmado**. Se buscaron campos de longitud de 1/2/4 bytes LE/BE dentro de esas ventanas, tanto con NUL como sin él: ninguna posición coincide en más de 1/12 ventanas. No hay evidencia suficiente para aceptar esa gramática simple de longitudes.

Antes de la primera región no se hallaron enteros absolutos de 16/32 bits LE/BE, alineados a su anchura, que apunten exactamente a cualquiera de los catorce offsets. No descarta punteros relativos, offsets sin alinear, tablas posteriores u otras codificaciones.

## Contraste con lectores públicos

Fuente: [FrontierTextHandler, src/scenario.py](https://github.com/Houmgaor/FrontierTextHandler/blob/ed855dc7e4fbe5abecbe16b6491e1beca0643284/src/scenario.py), blob `fa02f10eb7bd6eb766f7286bfb43ddba68fa0b87`, y [src/ftxt.py](https://github.com/Houmgaor/FrontierTextHandler/blob/ed855dc7e4fbe5abecbe16b6491e1beca0643284/src/ftxt.py), blob `1dbd0de748510c047e3ad8d142961835a77fe123`. Se revisó código; no se instalaron ni ejecutaron los lectores externos ni sus rutinas de modificación.

| Hipótesis aplicada **desde offset 0** | Comprobación observada | Conclusión limitada |
|---|---|---|
| Escenario externo con tamaños u32 BE | primer tamaño 4.294.967.295 excede los 341 bytes disponibles | ese contenedor no es válido desde cero |
| Subcabecera de ocho bytes y bloque de metadatos | padding no cero, total u16=65.535, inicio calculado de cadenas=9 frente a primer ancla=52 | no acepta esa estructura como explicación de las regiones |
| FTXT | falta magic 0x000B0000 | no es FTXT en ese offset |
| Registro chunk2 de 17 bytes, u32+13 ceros | los trece bytes de padding no son todos cero | no acepta esa gramática desde cero |

El scanner heurístico de texto dentro de JKR del lector público no proporciona por sí mismo una gramática de estos bytes. Sus ejemplos y comentarios sobre cliente PC no demuestran compatibilidad estructural de Vita. Los rechazos anteriores no descartan subbloques internos ni formatos relacionados con cabecera distinta.

## Reproducción, aceptación y bloqueo

`tools/stt_re/inspect_frontier_text_layout.py --input <decoded.bin> --regions <informe central> --out <directorio nuevo>` exige coincidencia exacta de hash/tamaño y limita la entrada a 64 KiB. Solo publica offsets, contadores y pruebas estructurales. [Recibo público](frontier-jkr-layout-evidence.json), original local en `analysis-local/frontier-jkr-layout-20261021/report.json`. 70 pruebas sintéticas aprobadas, cinco nuevas sobre límites, terminadores y solapamiento de anclas.

**Bloqueo concreto:** falta una gramática interior aceptada. No se han establecido longitud, recuento, delimitador de registro o significado de los campos repetidos. Próximo experimento útil: contrastar el patrón de once bytes con un lector o especificación pública específica, o realizar un contraste diferencial autorizado que pueda validar campos, manteniendo esta muestra como control. No ampliar masivamente por una coincidencia CP932. No se tocaron banco, registro de derivados, otros Work, originales, consola o material criptográfico.

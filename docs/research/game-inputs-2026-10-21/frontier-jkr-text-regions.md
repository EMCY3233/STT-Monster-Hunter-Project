# Regiones compatibles con CP932 en la muestra JKR — 21-10-2026

## Hallazgo limitado
La salida JKR de349bytes,ya enlazada al banco,contiene **14regiones no vacías entre bytesNUL** que se decodifican estrictamente con CP932 y contienen puntosUnicode de los bloques Hiragana/Katakana. Suman160bytes. Doce regiones no contienen controles Unicode;dos contienen tres cadauna. Las14terminan enNUL yninguna acepta UTF-8estricto.

Esto aporta evidencia de contenido textual compatible con CP932 dentro del bloque. **No identifica una tabla de cadenas,la gramática completa,una codificación declarada,un tipo de recurso ni su función en el juego.** Otros decodificadores podrían producir caracteres válidos;no se ha probado unicidad de la codificación ni estimado falsos positivos. No se usa el nombre del archivo para atribuir semántica.

Fuente local:analysis-local/frontier-jkr-smallest-20261021/decoded.bin.
SHA-256:592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c,igual antes/después de este sondeo. No se repitió la descompresión ni se cambió su recibo o el registro del banco.

## Metadatos observados
Offsets enbytes desde inicio;los contadores describen la decodificación CP932,no una estructura declarada por el archivo. Se publican solo offsets,longitudes yconteos;**ninguna cadena comercial ni bytes de contenido**.

| Offset | Bytes | PuntosUnicode | Bloqueskana | IdeogramasCJK | Controles |
|---|---:|---:|---:|---:|---:|
| 52 | 30 | 15 | 14 | 0 | 0 |
| 83 | 9 | 6 | 3 | 0 | 3 |
| 104 | 14 | 7 | 5 | 1 | 0 |
| 119 | 7 | 5 | 2 | 0 | 3 |
| 138 | 8 | 4 | 1 | 3 | 0 |
| 159 | 10 | 5 | 4 | 1 | 0 |
| 181 | 8 | 4 | 2 | 2 | 0 |
| 201 | 10 | 5 | 2 | 3 | 0 |
| 223 | 10 | 5 | 5 | 0 | 0 |
| 245 | 8 | 4 | 4 | 0 | 0 |
| 265 | 12 | 6 | 6 | 0 | 0 |
| 289 | 8 | 4 | 3 | 0 | 0 |
| 309 | 8 | 4 | 4 | 0 | 0 |
| 329 | 18 | 9 | 4 | 2 | 0 |

Los dos tramos con controles se mantienen íntegros en el análisis;no se quitaron bytes para hacerlos pasar como cadenas limpias. El resto del archivo continúa sin interpretar.

## Método y límites
[Herramienta propia](../../../tools/probe_cp932_regions.py),sin dependencias externas. Entrada máxima64KiB. Recorre tramos máximos sinNUL,usa decodeCP932conerrors=strict,descarta fallos de decodificación yretiene solo tramos con almenos un puntoU+3040–U+30FF. Cuenta por separado controles yCJK,comprueba UTF-8como comparación yregistra terminaciónNUL. No produce texto,reescritura,traducción oadaptación.

```powershell
python tools/probe_cp932_regions.py --source ../analysis-local/frontier-jkr-smallest-20261021/decoded.bin --report ../analysis-local/logs/frontier-text-regions-new.json
python -m unittest discover -s tests -p test_cp932_regions.py -v
```

Seis pruebas sintéticas aprobadas:offsets/conteos sin texto exportado,ASCII no seleccionado,byte multibyte truncado sin sustitución,controles preservados,cola sinNUL eentrada/tamaño fuera de contrato. El recorrido real registra14regiones ypreservación dehash. No son pruebas de un parser interno del juego.

[Recibo de metadatos](frontier-jkr-text-regions.json).

## Fuentes contrastadas y siguiente aceptación
La [documentación de codecs de Python](https://docs.python.org/3/library/codecs.html#standard-encodings) describe la decodificación estricta. [FrontierDataTool](https://github.com/Houmgaor/ReFrontier/blob/master/FrontierDataTool/README.md) documenta flujosCP932/UTF-8;es contexto general,no prueba de soporte de este bloque Vita.

La consulta web del árbol FrontierTextTool falló por acceso/caché;no se interpreta como ausencia de esa herramienta ni como demostración de que falte un lector público.

Se entregó el hallazgo al frente de investigación para contrastar gramática ybordes sobre esta misma muestra. Mantener pendientes los otros43JKR hasta una aceptación útil de su formato interior. No se amplió extracción,cifrado,FTP oconsola,ni se clasificó por armas.

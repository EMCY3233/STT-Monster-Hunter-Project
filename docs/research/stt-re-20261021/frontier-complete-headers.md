# Frontier: contraste de candidatos tras completar la copia

Fecha: 2026-10-21. Sustituye las afirmaciones de copia incompleta de los informes anteriores; aquellos describen cortes anteriores. Este frente no realizó la transferencia ni modificó su banco.

## Censo y comprobación independiente

El frente de inventario comunicó cierre de 8.261 archivos / 5.212.490.427 bytes y cotejo de 8.252 hashes, excluyendo nueve metadatos de package. Se leyó su resumen local y lista de candidatos. Estos totales son evidencia del otro frente; **aquí se releen independientemente solo los 50 candidatos**, con hash completo, tamaño y estabilidad antes/después. Los 50 coinciden con el censo, sin errores de lectura o cambios observados.

Entrada documental: `docs/research/game-inputs-2026-10-21/frontier-container-candidates.json` del frente PR3, SHA-256 `b990d19577b07448a03d8d261e5014aca712aec2d06740adcaf782f0be2f50be`. No se volvió a catalogar el banco ni se modificaron archivos de entrada.

| Resultado | Cantidad | Comprobación |
|---|---:|---|
| JKR | 44 | firma real `JKR` seguida de 0x1A; versión 0x0108, tipo 3 LZ en todos; offset de datos dentro del archivo y tamaño de salida dentro del presupuesto |
| ECD | 5 | firma real `ecd` seguida de 0x1A; índice de parámetros admitido; tamaño declarado igual al archivo menos 16 bytes |
| SCE | 1 | firma `SCE` seguida de cero; no se afirma ELF ni ejecutable cargable |

ECD localizados: `rePatch/PCSG00350/dat/mhfdat-vita.bin`, `mhfinf.bin`, `mhfjmp.bin`, `mhfpac-vita.bin` y `mhfrcc.bin`. SCE: `rePatch/PCSG00350/eboot.bin`. Las 44 entradas JKR están también en rePatch; declaran 239.784 bytes de salida en total, entre 349 y 21.093 bytes por archivo. No se deduce de ello precedencia efectiva de capas en consola ni equivalencia funcional entre app, patch y rePatch.

## Fuentes y límite de verificación

[ReFrontier ARCHIVE_FORMATS.md](https://github.com/Houmgaor/ReFrontier/blob/master/docs/ARCHIVE_FORMATS.md), blob `2d810513e0c85ac81712123e0b6a89e3612e6f6e`, describe campos JKR/ECD; [FileMagic.cs](https://github.com/Houmgaor/ReFrontier/blob/master/LibReFrontier/FileMagic.cs), blob `cb89c2fc2f028c9b9ff32a02762cbac86ae51936`, permite contrastar constantes. La columna ASCII del documento tiene el orden de bytes de algunas firmas invertido: se sigue la constante little endian y los bytes observados, no esa transcripción.

El lector propio solo valida cabeceras. **No** descifra ECD, comprueba su CRC, descomprime JKR, valida el tamaño real descomprimido o interpreta el SELF/SCE. Los 8.196 archivos restantes del censo siguen sin clasificación por firma; no se atribuye corrupción ni cifrado específico por esa ausencia. El SFO de parche Z 01.99 no confirma revisión ZZ.

Evidencia privada: `analysis-local/frontier-candidates-20261021/report.json`. Resumen reproducible publicado en [frontier-candidate-evidence.json](frontier-candidate-evidence.json); no contiene recursos comerciales ni material criptográfico. Código: `tools/stt_re/inspect_frontier_candidates.py`. Repetir con `--root <copia local> --candidates <manifiesto> --out <directorio nuevo fuera de entradas>`.

## Experimentos siguientes

Prioridad 1: decoder LZ acotado para los 44 JKR, comprobando consumo, backreferences y tamaño final; comenzar por la salida declarada más pequeña. Prioridad 2: estudiar la implementación primaria ECD en copia de trabajo y exigir CRC del plaintext antes de atribuir el formato interior. Prioridad 3: contrastar la estructura SCE con un lector SELF de Vita sin ejecución ni cambios de firmware. Ninguno implica transferencia a consola ni clasificación por armas.

52 pruebas sintéticas aprobadas: seis nuevas comprueban límites JKR, longitud ECD y que una firma SCE no se clasifique como ELF. No equivalen a validar el contenido de los contenedores ni a pruebas en hardware.

# Frontier: un único par diferencial JKR

Fecha: 2026-10-21. Se conserva el control de 349 bytes y todos sus recibos originales. Se procesa **solo un JKR adicional**, sin banco, consola, FTP, instalación, ejecución de juego, material criptográfico o modificación de otros Work.

## Selección y transformación

Selección determinista del manifiesto de candidatos ya verificado: JKR versión 0x0108, codec 3; excluir SHA-256 `4fcc62ad49f42b315d69013b2d312845b2d301dc97d47526047497f37125d385`; salida declarada como máximo **4.096 bytes**; elegir la menor, desempate por ruta. No se utilizó el significado del nombre ni se amplió presupuesto.

Seleccionado: `rePatch/PCSG00350/dat/load/uc/uc00_000_01.bin`, 1.058 bytes, SHA-256 `29d9e008ccd705a82185c3574f7e58327d6a77f4ccedb9ad89d5599c62fb2463`. Se usó el decoder existente, sobre copia nueva, sin modificar su algoritmo LZ. Solo se añadieron filtros explícitos de selección y parámetros registrados.

Resultado: **1.884/1.884 bytes**, SHA-256 `fa22ddcc947003496640007bd8f9cd5153e25b61a33b98e430bb1b4eb88352c8`; consumo **1.042/1.042 bytes** de carga, cero bytes sobrantes, siete bits de control sin usar. Termina por tamaño declarado, sin afirmar marcador final ni checksum. Hash del original intacto. Salida sin firma reconocida por el detector limitado.

## Contraste estructural observado

| Propiedad | Control A | Contraste B |
|---|---:|---:|
| Bytes descomprimidos | 349 | 1.884 |
| Bytes NUL | 143 | 364 |
| Tramos máximos no vacíos entre NUL | 44 | 89 |
| Mayor tramo no vacío | 30 | 129 |
| Último byte es NUL | no | no |
| Regiones con criterio CP932+kana del sondeo central | 14 (resultado anterior reutilizado) | 0 (un sondeo nuevo) |

Los bloques comparten **dos bytes iniciales**. Las doce ventanas de once bytes anteriores a anclas de A aportaban ocho columnas constantes; ese patrón parcial de ocho columnas no aparece en **ninguna posición** de B. No se publican esos bytes ni cadenas.

El sondeo B reutiliza `inventory-work/tools/probe_cp932_regions.py` sin modificarlo. Su regla exige un tramo máximo entre NUL decodificable completamente como CP932 estricto y al menos un carácter U+3040–30FF. **Cero coincidencias no prueba ausencia de texto**, otra codificación ni corrupción: puede haber metadatos mezclados, texto sin kana u otros límites. No se repitió CP932 sobre A ni se descomprimió de nuevo el control.

## Hipótesis y aceptación

Sobrevive la compatibilidad mecánica de ambas entradas con este decoder JKR/LZ: tamaño declarado y consumo completos. No demuestra identidad funcional.

No sobrevive la transferencia **literal** a B del patrón parcial de prefijo obtenido de A. La regla CP932 usada no produce anclas comparables en B, por lo que la hipótesis de una tabla homogénea de esas regiones no recibe apoyo. Esto no descarta una familia más amplia con campos/tipos distintos ni prueba formatos separados.

La gramática interior de A sigue sin aceptar; B tampoco tiene un lector interior contrastado. **No se amplía a los otros 42 JKR.** Siguiente aceptación: especificación o lector público específico que explique campos y límites, o una hipótesis diferencial falsable dentro de estas dos muestras, sin convertir dos coincidencias en semántica confirmada.

## Evidencia y reproducción

Solo local: `analysis-local/frontier-jkr-pair-20261021/` contiene copia de fuente, salida, recibo, sondeo sin cadenas y comparación. Baseline A permanece en `analysis-local/frontier-jkr-smallest-20261021/`; no se cambia su registro de procedencia.

Decoder: `decode_jkr_lz.py --root <Frontier local> --candidates <report.json ya verificado> --out <carpeta nueva fuera de Git> --exclude-sha256 4fcc62ad49f42b315d69013b2d312845b2d301dc97d47526047497f37125d385 --max-declared 4096`. Sondeo CP932 sobre B con la herramienta central; comparación con `tools/stt_re/compare_frontier_jkr_pair.py`, que limita ambos bloques a 4 KiB y no exporta texto/bytes.

[Recibo público](frontier-jkr-pair-evidence.json): selección, hashes, medidas y trazabilidad. Cinco pruebas nuevas de selección y tres de comparación **aprobadas**. Se conservan los resultados de las setenta pruebas previas; no se repitió la batería ni el censo completo para esta adición.

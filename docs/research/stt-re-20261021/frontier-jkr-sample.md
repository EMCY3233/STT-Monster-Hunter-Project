# Frontier: primera muestra JKR descomprimida

Fecha: 2026-10-21. Continuación de [cabeceras completas](frontier-complete-headers.md). Ensayo en copia derivada nueva, sin ejecutar juegos, instalar herramientas, acceder a consola o modificar banco/originales.

## Observación real

Se eligió la menor salida declarada entre los 44 JKR del manifiesto ya comprobado: `rePatch/PCSG00350/dat/load/uc/uc00_001_03.bin`. Entrada: 238 bytes, SHA-256 `4fcc62ad49f42b315d69013b2d312845b2d301dc97d47526047497f37125d385`. Se copió al directorio nuevo de ensayo antes de decodificar y se comprobó nuevamente el hash del original después.

Cabecera JKR versión 0x0108, tipo 3, datos en offset 16. Resultado: **349/349 bytes**, SHA-256 `592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c`. Se consumieron los **222/222 bytes** de carga; cero bytes sobrantes y cinco bits de control sin utilizar. La terminación es por tamaño declarado, **no por un marcador final ni checksum**. Operaciones: 107 literales, 26 referencias cortas, 6 medias, 2 largas A, 1 larga B y 1 bloque literal.

Clasificación: **sin firma reconocida** por el detector limitado. Tampoco pasó su prueba de tabla inicial de pares offset/tamaño. No demuestra texto, modelo, animación, misión, hitbox o IA; el nombre del archivo no se usa para atribuir semántica. Que coincida el tamaño no es prueba independiente de identidad funcional del recurso. No se recompuso ni adaptó para el juego.

## Método revisado y límites

Se revisó [JPKDecodeLz.cs de ReFrontier](https://github.com/Houmgaor/ReFrontier/blob/60e43a6692e05b810bb6710501fcf576eeb0ccbd/ReFrontier/Jpk/JPKDecodeLz.cs), commit `60e43a6692e05b810bb6710501fcf576eeb0ccbd`, blob `469390222071858749a42556b12809820123718f`. El lector Python `tools/stt_re/decode_jkr_lz.py` adapta ese algoritmo, con licencia MIT y atribuciones preservadas íntegramente en su cabecera. No se instaló ni ejecutó ReFrontier.

El lector limita entrada y salida a **64 MiB**. Rechaza codecs/versiones distintos, offsets fuera de rango, truncamiento, referencias anteriores al inicio y operaciones que excedan la salida declarada. Admite copias solapadas; registra consumo y sobrantes. El destino debe ser nuevo y estar fuera de entradas y Git. No contiene claves ni funcionalidad ECD/SCE.

Repetición: `decode_jkr_lz.py --root <copia Frontier local> --candidates <report.json de inspect_frontier_candidates> --out <directorio nuevo fuera de Git>`. Selecciona determinísticamente el menor tamaño declarado; valida tamaño/hash contra manifiesto, trabaja sobre `source.jkr` derivado y conserva `decoded.bin` y `receipt.json` **solo localmente**. Ensayo observado: `analysis-local/frontier-jkr-smallest-20261021/`.

[Recibo público](frontier-jkr-evidence.json): hashes, tamaños, consumo y límites, sin bytes comerciales. 65 pruebas sintéticas aprobadas, trece nuevas para las cinco ramas de referencias/literales y los límites, más el ensayo real descrito. No se interpreta como validación de todos los JKR ni se repiten las lecturas completas del censo.

## Bloqueos y siguientes comprobaciones

La identidad estructural de los 349 bytes requiere un lector interior contrastado con otra fuente o muestra; queda abierta. No ampliar a los otros 43 archivos hasta fijar una aceptación útil del formato interior. ECD: solo cabeceras/longitudes comprobadas, sin plaintext ni CRC verificado. SCE: firma comprobada, sin ELF validado ni ejecutabilidad demostrada. No se buscaron claves o licencias ni se intentó eliminar esas protecciones.

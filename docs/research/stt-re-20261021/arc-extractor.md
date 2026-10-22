# Extractor completo de ARC LE v17 sin cifrado — 22-10-2026

## Resultado entregado

`tools/stt_re/extract_arc.py` ya extrae **todas las entradas** de los ARC LE v17 con flujos zlib dentro de los límites comprobados. Incluye listado, extracción completa y verificación posterior con opción de volver a decodificar el original. No depende del emulador ni de entradas de ratón/teclado.

Se ejecutó con cuatro contenedores reales accesibles del parche **MHXX para 3DS**, sin confundirlos con MH4U o Switch/GU. Se extrajeron **1341 archivos, 23.093.773 bytes**, en una carpeta privada nueva. Las cuatro extracciones pasaron verificación de todos los hashes/tamaños y una segunda operación de lectura/decodificación del archivo fuente. 500 hashes de cargas coinciden además con recibos anteriores. Esta última comparación no constituye un segundo algoritmo de descompresión independiente.

| Contenedor | Entradas extraídas | Bytes de salida | Hashes de cargas contrastados con recibos anteriores |
| --- | ---: | ---: | ---: |
| title.arc | 121 | 9,323,521 | 121 |
| quest.arc | 373 | 3,879,361 | 373 |
| common.arc | 843 | 9,641,271 | 6 |
| hunter_note.arc | 4 | 249,620 | 0 |

Las firmas iniciales incluyen 83 MOD, cuatro LMT, 200 TEX, 63 GMD y 83 MRL; 908 entradas permanecen sin clasificar por firma. Estas son cargas reales extraídas de archivos, no bloques BSS exportados. Las firmas y extensiones no certifican semántica, geometría, reproducción de animaciones ni conversión a formatos editables.

## Uso

Desde la carpeta de herramientas y con un intérprete Python disponible:

```text
python extract_arc.py list archivo.arc
python extract_arc.py extract archivo.arc --out carpeta_nueva --expect-sha256 HASH_DEL_ORIGINAL
python extract_arc.py verify carpeta_nueva --source archivo.arc
```

`--expect-sha256` es opcional; si se proporciona, se comprueba antes de crear la salida. `verify` sin `--source` valida manifiesto y archivos exportados; con `--source` también contrasta identidad y todas las entradas con una nueva decodificación. Se requiere `probe_arc.py` junto al extractor y sólo biblioteca estándar Python. No es necesario instalar herramientas adicionales ni ejecutar el juego.

Las salidas reales están en `analysis-local/arc-extractor-acceptance-20261022/`, subcarpetas `title`, `quest`, `common` y `hunter_note`. Cada una contiene:

- `entries/00000.ext`, etc.: nombres por índice para evitar colisiones o rutas maliciosas.
- `manifest.json`: ruta interna original como metadato, bytes originales del campo de nombre en hexadecimal, type_id, flags, offsets, tamaños, firma candidata y SHA-256 por entrada.
- `manifest.sha256`: comprobación del contenido del manifiesto. Es integridad local, no firma de autenticidad.

Las rutas internas no se usan para escribir archivos, por lo que nombres duplicados y secuencias como ../ permanecen sólo como metadatos. No se inventan extensiones de tipos desconocidos: se usa .bin. Las extensiones conocidas se basan únicamente en la firma inicial y quedan marcadas como candidatas.

## Validaciones y fallos

Se valida tabla completa, nombres terminados, rangos, ausencia de solapamientos y presupuestos antes de escribir. Cada flujo zlib debe terminar exactamente, producir el tamaño declarado y no dejar bytes sobrantes. Todas las entradas se validan antes de crear el directorio de salida; se vuelven a decodificar para escribir, se comprueba el hash de lectura de cada archivo y el original se contrasta de nuevo al terminar. Cualquier cambio de fuente hace fallar la aceptación.

La salida debe ser nueva: no se sobrescribe contenido existente. Se rechaza extraer en el árbol de publicación o dentro de un checkout Git. Si un error posterior a la creación deja una salida parcial, se conserva con `failure.json`; `verify` la rechaza. No se borra automáticamente la evidencia del fallo.

Diez pruebas sintéticas correctas: extracción completa y nueva decodificación, rutas/nombres problemáticos, destino existente, hash esperado incorrecto, zlib corrupto, exportación alterada, manifiesto alterado, archivo extra, versión no compatible y marca de fallo. Son diez métodos, sin sumar nuevamente sus repeticiones. Se reutilizan además las validaciones del lector previo; no se presentan como pruebas nuevas.

Límites actuales: archivo ARC de hasta 64 MiB, entrada descomprimida de hasta 32 MiB y total declarado de hasta 128 MiB. Sólo cabecera ARC little endian v17, campo reservado cero y flujos que cumplan la decodificación zlib exacta. No hay soporte reclamado para ArcC, cifrado, otras versiones de ARC, ROM/NCSD/NCCH/RomFS completos ni reconstrucción de archivos desde memoria en ejecución. Un ARC de MH4U sólo podrá darse por compatible después de probar sus bytes, no por compartir nombre de juego o extensión.

## Relación con las lecturas de juego

Las sesiones Citra, los contadores por avance y las referencias EUR siguen aportando pistas de ejecución y dependencias. No son requisito para esta extracción estática y no se usan para atribuir estos recursos de MHXX a acciones observadas en MH4U. El extractor completa una etapa concreta: **contenedor → cargas descomprimidas verificadas**. La conversión de MOD/TEX/LMT/GMD y la identificación de su uso en juego son etapas posteriores.

Se publicó sólo el código, pruebas y metadatos. Los 1341 archivos comerciales permanecen locales; no se publicaron ROMs, claves, imágenes ni recursos extraídos. No se modificaron los contenedores probados, el banco anterior o trabajos de otros chats. Las comprobaciones de hash de esta etapa se refieren a esos cuatro ARC, no a un nuevo hash de todos los juegos originales.

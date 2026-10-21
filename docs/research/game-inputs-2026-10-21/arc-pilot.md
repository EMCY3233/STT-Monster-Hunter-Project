# Piloto ARC — parche MHXX 3DS

21-10-2026, Europe/Madrid. Análisis local de una muestra del parche; no se atribuyen estos resultados a todos los recursos del juego base o a Frontier.

## Cadena de procedencia

CIA original del parche → contenido NCCH ya registrado en [extracción](extraction-tools.md) → RomFS extraído localmente con CTRTool 1.3.0 → tres ARC de muestra → lectura de tabla y descompresión acotada con [lector propio](../../../tools/probe_arc.py).

El primer intento de `--romfsdir` falló porque no existía el directorio padre. Se creó `analysis-local/romfs` y se repitió con salida 0: **1.609 archivos, 28.822.254 bytes**. Un contenedor RomFS intermedio de diagnóstico se retiró tras registrar su hash; se conservan NCCH fuente, archivos extraídos y logs. Ninguno está en GitHub.

Las 1.228 entradas con nombre `.arc` extraídas presentan firma `ARC\0`. Esa lectura de cuatro bytes no certifica sus tablas ni sus datos. El análisis completo de tabla/payload se limitó a los tres archivos siguientes.

## Muestra comprobada

| Archivo | Bytes | SHA-256 | Entradas | Descompresión y longitud declarada |
|---|---:|---|---:|---|
| title.arc | 2.421.728 | `6c73a0cfb275ed54b0909d4aac8989b887af3db10b69b4a3dfe342ac4753446e` | 121 | 121/121 correctas |
| resident.arc | 1.917.494 | `63c29d8e0d87d1096082babc82b66677f9c781a0bee479f8fc1743ec2d2f4c49` | 288 | 288/288 correctas |
| quest.arc | 1.953.795 | `63714c4c4ddd7eba78560d9a998dadf8319d788963e79928844e88f0814054be` | 373 | 373/373 correctas |

Formato observado en la muestra: ARC little-endian, versión 17, campo reservado cero. Tablas y rangos dentro del archivo; sin solapamientos de payload en cada tabla. **782 entradas descomprimidas correctamente en memoria**, con terminación zlib y tamaño de salida comprobados; sin datos sobrantes en los streams. Los tres ARC mantuvieron su hash tras el sondeo.

La disposición de campos se contrastó con el [lector de Arc Explorer](https://github.com/Paxlord/pax_arc_explorer/blob/main/arc.odin), función `arcle_read`. El código propio aplica límites adicionales, no contiene descifrado ni código copiado de esa aplicación, y no equivale a validar el ejecutable de Arc Explorer. Soporte limitado a esta variante observada; no se extrapola a ARC cifrados, big-endian u otras versiones.

## Clasificación preliminar

| Firma reconocida tras descomprimir | title | resident | quest | Estado |
|---|---:|---:|---:|---|
| TEX | 22 | 17 | 60 | Texturas candidatas; sin decodificar formato, mipmaps ni swizzle |
| GMD | 11 | 31 | 6 | Tablas/textos candidatos; contenido no traducido ni adaptado |
| MRL | 0 | 0 | 32 | Materiales candidatos; vínculos sin resolver |
| MOD | 0 | 0 | 32 | Modelos candidatos; geometría/rig sin validar |
| No clasificada por el sondeo | 88 | 240 | 243 | No implica ausencia de formato válido |

No se reconoció firma LMT en esta muestra. Eso no demuestra ausencia de animaciones: las entradas no clasificadas u otros contenedores podrían contenerlas. No se han identificado rigs, clips, frecuencias de animación, huesos, movimientos de Espada Larga, daño ni hitboxes.

## Exportación local de dos entradas

El lector exporta únicamente el índice solicitado a un nombre generado, sin usar rutas internas del ARC como destino. No sobrescribe archivos existentes y rechaza destino situado dentro de un checkout Git.

| Origen | Índice y descripción | Bytes de salida | SHA-256 cotejado al releer salida |
|---|---|---:|---|
| title.arc | 0, candidato GMD | 8.215 | `e478a0480d0590a56256b4afb0369b6ac8608e3f10b6e19373989a20de995d26` |
| quest.arc | 213, `effect\\base\\cm050_000`, tipo `58A15856`, candidato MOD | 4.126 | `998b2fbee2d06b726fad75c3395404139fa8204de74657cfa4128e442e7746ac` |

Los bytes exactos de title/índice 0 se contrastan en el resumen JSON adjunto; no derivar tamaño a partir del nombre o de la firma. Ambas salidas son locales bajo `analysis-local/samples`, no distribuidas. La segunda no está identificada como modelo de cazador o arma: la ruta sugiere efectos, una hipótesis pendiente de estructura y dependencias.

## Límites y pruebas del lector

Límites por ejecución: ARC máximo 64 MiB, entrada descomprimida máxima 32 MiB y suma declarada máxima 128 MiB. Rechaza tabla truncada, rango fuera del payload, solapamiento, versión no soportada, exceso de presupuesto, stream incompleto, longitud incorrecta y datos zlib sobrantes. Son salvaguardas de este sondeo, no límites del formato comercial.

Ocho pruebas sintéticas aprobadas: payload válido con nombre interno que intenta traversal (no se usa para exportar), versión distinta, tabla truncada, offset sobre tabla, presupuesto excesivo, tamaño de salida falso, trailing data y corrupción zlib. Los datos de prueba son propios. Sin pruebas de visualización ni adaptación a Vita.

## Preservación y siguientes pasos

Se cotejaron nuevamente los siete originales con el inventario inicial después del piloto: **7/7 SHA-256 idénticos**. Herramientas y recursos quedan fuera del checkout; se publican solo código propio, pruebas y metadatos.

Próxima etapa: validar la estructura del pequeño candidato MOD y sus vínculos MRL/TEX con una herramienta compatible, registrar versión exacta y confirmar conteos/rangos antes de visualizar. No convertir, adaptar ni reutilizar el recurso por el hecho de poder extraerlo. Los CIA base siguen con contenidos marcados como cifrados; no se buscaron claves ni se modificaron originales. Extremo y el catálogo histórico Frontier permanecen separados de este piloto.

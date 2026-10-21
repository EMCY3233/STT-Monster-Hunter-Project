# Prueba ejecutada: Citra y entradas 3DS

Fecha: 2026-10-21. Solo PC, perfil portátil nuevo por ensayo. GU Switch excluido. No se descargaron juegos, claves ni firmware. No se actuó sobre ninguna consola.

## Procedencia y límites

Se consultó el [archivo del sitio Citra mantenido por Azahar](https://citra.azahar-emu.org/download/). Sus enlaces originales ya no ofrecen builds y remite a copias de terceros en Internet Archive, cuya autenticidad debe verificarse. No se usaron sitios que se presentan como Citra oficial.

Build conservado: Nightly 2104, HEAD-0ff3440, confirmado por el registro de ejecución. [ZIP archivado](https://archive.org/download/citra_20240304_2129/citra-windows-msvc-20240303-0ff3440.zip), 31.851.210 bytes, SHA-1 `824be65eac6b1dbaaf22da8522fa2a2975099d56`, SHA-256 `ea8569d5989ca51bf233a63cde03c998f6f1b1addd01906c96647e0a9915ebf5`. Coincide con el manifiesto del depósito; esto acredita integridad del archivo conservado, **no** firma del desarrollador. El archivo 7z de igual nombre y versión figura en dos depósitos con el mismo SHA-1, sin descargarlo. No se presenta esa coincidencia como comprobación independiente del ZIP.

`citra.exe`: 22.420.480 bytes, SHA-256 `53087fb66a5e76bf6fe23bfe324c25c257c39b97fb1eefd8c69a8c917a104f27`. La prueba utilizó el frontend de consola, no automatización de menús Qt. Se conservan ejecutables, licencia, perfiles y registros locales. Configuración SDL predeterminada: telemetría deshabilitada según comentario del perfil; no se configuraron credenciales, multijugador ni claves.

## Resultado observado

| Entrada | Operación real | Evidencia |
|---|---|---|
| MH3U EUR, 00040000000B1D00 | instalación CIA | aborta: `CommonKey 0 missing`, CIA cifrado sin title key |
| MH4U EUR, 0004000000126100 | instalación CIA reconstruido localmente | mismo bloqueo |
| MHXX JPN, 0004000000197100 | instalación CIA reconstruido localmente | mismo bloqueo |
| Parche MHXX, 0004000E00197100 | instalación CIA | primera ruta falla con Windows 206; segunda ruta corta instala correctamente |
| NCCH plaintext del parche | carga directa en perfil nuevo | entra en ejecución; errores de memoria sin mapear y shader/vertex; termina con 0xC0000005 tras 13,469 s |

Los cuatro CIA y el NCCH conservan su SHA-256 antes/después de cada ensayo. La instalación del parche escribe una copia dentro del perfil emulado del PC. Su `.app` tiene 36.868.096 bytes y SHA-256 `1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473`, idéntico al NCCH obtenido por nuestro lector. Citra registra `Installed ... successfully`, aunque su frontend devuelve código 1: no usar únicamente ese código para juzgar la instalación.

El parche es un título de actualización; cargarlo aisladamente **no sustituye al juego base**. El crash no identifica por sí solo una causa única: faltan el juego base y validación visual, y el log también contiene fallos de emulación. No se afirma pantalla de título, jugabilidad, compatibilidad plena, FPS ni descifrado de las tres bases.

La [FAQ conservada](https://citra.azahar-emu.org/wiki/faq/) confirma que Citra puede usar aplicaciones cifradas con material de claves de la propia 3DS. Aquí no se aportó ni se buscó ese material. El siguiente ensayo de las bases depende de una entrada descifrada autorizada o material propio verificado; repetir la instalación con el mismo perfil vacío no resuelve el bloqueo.

## Reproducción

`tools/stt_re/run_citra_probe.py` exige perfil `user` vacío, crea un recibo, calcula SHA-256 antes/después, limita el proceso a 15 s y termina solo el proceso creado. Ejecutar con `--exe <citra.exe> --input <entrada.cia> --install --out <directorio nuevo>`. Para NCCH, omitir `--install`. Antes del siguiente ensayo, archivar el perfil anterior con su recibo; conservar todas las evidencias. Usar una ruta corta dentro del espacio local para evitar el límite de rutas de esta build de Windows.

Recibos privados: `analysis-local/citra-{mh3u,mh4u,mhxx,mhxx-patch,mhxx-patch-short,mhxx-patch-boot}-20261021/receipt.json`. Los perfiles iniciales archivados están junto al ejecutable largo; la instalación válida está en `analysis-local/c3/user-patch-installed` y el perfil de ejecución en `analysis-local/c3/user`. Logs completos y contenido comercial permanecen locales; el JSON público solo recoge huellas, estados y tamaños, sin contenido ni claves.

# Herramientas contrastadas y primera extracción local

21-10-2026, Europe/Madrid. Actualiza los pendientes de contenedores del inventario inicial; no sustituye su referencia de hashes.

## MHXX / MHGU: denominación y plataforma

El usuario identifica MHXX/MHGU como Monster Hunter Generations Ultimate. [Capcom confirma](https://news.capcomusa.com/lets/browse/monster-hunter-generations-ultimate-coming-to-nintendo-switch-on-august-28th) que Generations Ultimate se conoce como Monster Hunter XX en Japón. [El anuncio original de XX](https://www.capcom.co.jp/ir/english/news/pdf/e161028.pdf) identifica la edición 3DS. Ambos nombres se relacionan con la misma entrega; la plataforma debe conservarse por separado para elegir herramientas.

La imagen local extraída es un CIA 3DS con TMD `0004000000197100`; la revisión numérica observada es 48 (componentes 0.3.0). No es una imagen Switch demostrada ni el parche convierte su formato a Switch. La etiqueta del proyecto puede ser «MHXX / Generations Ultimate — 3DS JPN», manteniendo JPN como denominación de origen y sin afirmar que se ha validado la región del programa completo.

## Herramientas: comprobado frente a anunciado

| Herramienta y fuente primaria | Función | Estado de esta sesión |
|---|---|---|
| [7-Zip / 7zr](https://www.7-zip.org/download.html) | Listar, probar y extraer 7z multipartes | Descargado portátil desde sitio oficial; banner 26.04 x86, 05-10-2026. Listado, prueba y extracción aprobados para MH4U y MHXX |
| [CTRTool](https://github.com/3DSGuy/Project_CTR/blob/master/ctrtool/README.md), [publicación 1.3.0](https://github.com/3DSGuy/Project_CTR/releases/tag/ctrtool-v1.3.0) | Información y extracción CIA/NCCH/ExeFS/RomFS | ZIP Windows x64 contrastado con digest de publicación. Ejecutado: contenido sin descifrar del parche, información NCCH y listado RomFS |
| [Arc Explorer](https://github.com/Paxlord/pax_arc_explorer) | Abrir, listar y extraer ARC | El autor declara soporte de MH3U 3DS/Wii U, MH4/MH4U, MHX/MHXX 3DS y MHGU Switch, y ArcLE/ArcBE/ArcC. No instalado ni probado con muestra local |
| [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2) | Toolkit con plugins de recursos y extracción | Alternativa candidata. La compatibilidad concreta debe contrastarse en su tabla y con una muestra; no probado |
| [mhtools de codestation](https://github.com/codestation/mhtools), [README](https://raw.githubusercontent.com/codestation/mhtools/master/README) | Contenedores DATA.BIN, índices, PAK y TMH | Comandos documentados `--gen-index`, `--dec-all` y extracción PAK/TMH. Java no localizado en PATH; no instalado ni probado. No afirmar soporte exacto de la revisión MHFU local |
| [PRXTool](https://github.com/pspdev/prxtool) / [Ghidra](https://github.com/NationalSecurityAgency/ghidra) | Estudio de ejecutables legibles | Fase posterior; no extraen por sí solos todos los recursos ni convierten un juego a Vita |

No se ha instalado software en el sistema: herramientas portátiles dentro de `analysis-local/tools`, fuera de ambos checkouts. No se han ejecutado juegos ni conectado a PS Vita/FTP.

## Procedencia de herramientas descargadas

- 7zr: [URL oficial utilizada](https://www.7-zip.org/a/7zr.exe). SHA-256 observado `256feca8e274e5da655e2a284fabafd9f554365eb164862089dacd4e8276d282`. Authenticode: NotSigned. El hash identifica la descarga, sin presentarlo como cotejo independiente con hash publicado.
- CTRTool: ZIP [Windows x64 1.3.0](https://github.com/3DSGuy/Project_CTR/releases/download/ctrtool-v1.3.0/ctrtool-v1.3.0-win_x64.zip), SHA-256 `8031dff3be72d0adb250fae1f969f27627e12a89ebc6dd074a15a75f87ddc949`, coincidió con digest SHA-256 de la API oficial de releases. Ejecutable: `79021f283b2199950eb22cf3c459806b9c8aaaf68f65c80100107d3454a1c224`.

## Pruebas y derivados locales

7zr reconoció dos volúmenes por juego y un solo CIA en cada archivo 7z. Los dos comandos `t` terminaron con código 0 y «Everything is Ok»; las extracciones `x` a directorios nuevos terminaron también con código 0. Se comprobó por tanto descompresión/CRC de la carga, además de las cabeceras anteriores. Esto no autentica los juegos ni valida sus firmas.

| Derivado local, no publicado | Bytes | SHA-256 | Metadatos públicos observados |
|---|---:|---|---|
| MH4U CIA | 2.734.762.304 | `3b11095265bd96436306cbde7aa6256e7550164e83914d3ec9f8a139902e8069` | TMD `0004000000126100`, raw 0; dos contenidos con flag cifrado |
| MHXX CIA | 2.330.896.704 | `195570856aa2cd623001d00aaa7c7e20d1e563fe8782979e054570ac83982245` | TMD `0004000000197100`, raw 48; dos contenidos con flag cifrado |
| Contenido NCCH del parche MHXX | 36.868.096 | `1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473` | CTRTool: NCCH v2, producto `CTR-U-AGQJ`, sin crypto, RomFS listado y metadatos ExeFS |

Los CIA cifrados no se han descifrado ni se han buscado claves. Los metadatos de CIA/TMD se leyeron con la herramienta propia del inventario. CTRTool se probó con el parche exterior sin cifrar, usando `--plain --raw --contents` y sin extraer tickets.

CTRTool pudo leer el NCCH del parche y listar su RomFS con salida 0: **1.228 líneas de entradas terminadas en `.arc` y 270 en `.gmd`**. Ejemplos: `resident.arc`, `quest.arc`, `title.arc`. Son nombres enumerados, no 1.228 formatos ARC analizados ni recursos gráficos confirmados. No se decodificaron textos o modelos. RomFS declarado: offset `0x00756000`, tamaño `0x01bd3000`; ExeFS: offset `0x00002a00`, tamaño `0x00752800`.

Limitación observada: la ayuda de CTRTool anuncia `--listexefs`, pero ese binario rechazó la opción como desconocida (código 1). Repetir solo con `--listromfs` funcionó. No se oculta este fallo ni se presenta como prueba completa de ExeFS.

Después de la extracción, se cotejaron de nuevo los siete archivos originales con el inventario: **7/7 hashes coinciden**. Los derivados, herramientas y logs íntegros permanecen únicamente en `analysis-local/`; al repo se incorporan solo este informe y metadatos.

## Siguiente paso concreto

1. Inspeccionar una entrada ARC del parche de forma local y controlada, para contrastar firma/versión y la herramienta adecuada antes de extracción masiva de recursos.
2. Para MH3U/MH4U/MHXX base, documentar el bloqueo de contenido cifrado hasta disponer de entradas legítimamente legibles; no extrapolar la accesibilidad del parche a los juegos completos.
3. Para MHFU, revisar el código y compatibilidad de mhtools antes de instalar Java o generar índices. No confundir índices de contenedor con modelos/animaciones identificados.
4. Comunicar resultados a 02/04/07: sí hay dos CIA extraídos, la carga 7z ya está probada y el RomFS del parche es enumerable; no hay material Frontier ni adaptación de activos autorizada por estos resultados.

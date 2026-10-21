# STT — Inventario de entradas de juegos, 21-10-2026

**Actualización posterior del 21-10-2026:** [herramientas y extracción local](extraction-tools.md). Los dos conjuntos 7z ya pasaron prueba íntegra y extracción; hay metadatos de sus CIA y listado RomFS del parche. Los párrafos iniciales que indican «sin prueba de carga» o «herramientas no disponibles» describen la primera etapa, superada donde lo precisa ese informe. MHXX es el nombre japonés relacionado con Generations Ultimate; se conserva por separado la plataforma 3DS observada en el CIA.


Alcance: lectura local de `Juegos/`, sin modificar originales, ejecutar juegos, instalar herramientas, transferir a Vita o usar FTP. Solo se publican metadatos y código propio. Copia de trabajo independiente del monitor, rama `docs/game-input-inventory-20261021`.

## Resultado verificado

Siete archivos accesibles y leídos íntegramente. [Inventario JSON](inventory.json) contiene nombres, tamaños exactos, SHA-256 y sondeos de formato. [Lista SHA-256](SHA256SUMS.txt) permite cotejo local. Dos pasadas dieron los mismos siete hashes. Tamaño y fecha de modificación permanecieron estables durante cada lectura. Esto establece una referencia local; no autentica los juegos, no acredita una edición comercial concreta y no verifica firmas.

| Entrada local | Bytes | Formato observado | Versión e identidad observadas | Límite |
|---|---:|---|---|---|
| MH3U / EUR - Monster Hunter 3 Ultimate(00040000000b1d00).cia | 1.871.489.344 | Cabecera CIA y secciones dentro del archivo | TMD `00040000000B1D00`, versión numérica 0 | Dos contenidos con flag de cifrado; sin NCCH visible en primero. Región EUR por nombre, sin validar programa |
| MH4U / EUR - Monster Hunter 4 Ultimate (0004000000126100).7z.001 | 1.610.612.736 | Cabecera 7z dividida | Versión del juego desconocida | Identidad y EUR por nombre |
| MH4U / EUR - Monster Hunter 4 Ultimate (0004000000126100).7z.002 | 1.124.307.744 | Continuación del conjunto anterior | Desconocida | No es archivo comprimido independiente |
| MHFU / Monster Hunter Freedom Unite.iso | 886.702.080 | ISO9660; 13 archivos enumerados | SFO: `ULES01213`, `DISC_VERSION=1.01`, título Freedom Unite | `PSP_SYSTEM_VER=5.03` es requisito declarado, no versión del juego. Sin verificar autenticidad |
| MHGU / MHXX_MHGU_English_Patch_v2.cia | 36.897.728 | Cabecera CIA; primer contenido NCCH visible | TMD `0004000E00197100`, versión numérica 4224, componentes 4.8.0 | `v2` procede del nombre del parche; no es la versión TMD. Traducción y compatibilidad no comprobadas |
| MHGU / Monster Hunter XX  JPN (0004000000197100).7z.001 | 1.610.612.736 | Cabecera 7z dividida | Versión del juego desconocida | MHXX JPN y Title ID por nombre; contenido aún sin inspeccionar |
| MHGU / Monster Hunter XX  JPN (0004000000197100).7z.002 | 720.416.892 | Continuación del conjunto anterior | Desconocida | No identifica por sí solo una imagen de Switch |

Los componentes de versión TMD son una descomposición del entero del contenedor, no una etiqueta comercial validada. `version_verified=null` significa que no se ha autenticado una versión de distribución; `version_metadata_observed` y el sondeo conservan lo que sí se leyó.

Los conjuntos 7z tienen partes contiguas desde 001, CRC de cabecera inicial correcto, cabecera siguiente dentro de las partes y CRC siguiente correcto. Tamaños conjuntos: MH4U 2.734.920.480 bytes; MHXX 2.331.029.628 bytes. **No se ha probado la descompresión ni el CRC de los datos internos**. No afirmar que el juego está completo por estas comprobaciones.

## Hallazgos de ejecutables y recursos

- MHFU: `PSP_GAME/SYSDIR/EBOOT.BIN`, 1.910.384 bytes, envoltura `~PSP`; no es un ELF listo para analizar por esa sola observación. Existe también `BOOT.BIN`, cuyo formato interno no se ha sondeado.
- MHFU: `PSP_GAME/USRDIR/DATA.BIN`, 772.732.928 bytes, candidato a contenedor principal. Su contenido, compresión e índices siguen desconocidos. El ISO incluye `.pmf`, `.at3`, `.png`, `.sfo` y `.bin`, según sus nombres internos; no se han decodificado imágenes, audio ni animaciones.
- MHFU: `PSP_GAME/SYSDIR/UPDATE/` contiene archivos de actualización del sistema PSP; excluirlo del estudio de assets del juego. No ejecutar ni transferir esos archivos.
- MH3U: TMD declara dos contenidos cifrados. La lectura de metadatos no demuestra accesibilidad de ExeFS/RomFS. No se han buscado, leído ni publicado claves/tickets.
- Parche MHXX: contenido exterior sin flag de cifrado y marcador NCCH visible. Esto **no prueba** que sus regiones internas sean legibles o que el parche sea compatible con la base disponible.
- No se encontraron archivos identificados como Frontier. **MHFU significa Freedom Unite, no Frontier**. Tampoco hay imagen de Wii U o Switch identificada en este inventario.

## Hipótesis separadas

1. MH3U correspondería a la edición 3DS por su contenedor y TMD; la región específica debe contrastarse con metadatos internos accesibles.
2. La carpeta MHGU parece alojar MHXX 3DS japonés y una actualización/parche, no Generations Ultimate Switch. Confirmar base tras listar el 7z y contrastar IDs internos; no renombrar originales.
3. `DATA.BIN` de MHFU probablemente agrupa recursos, pero no se han observado todavía sus entradas ni sus formatos.
4. MOD/MOT/TEX/ARC u otros formatos propuestos por herramientas no están confirmados para estos bytes. Compatibilidad de herramientas pendiente de muestra controlada.

## Herramientas y preparación

Véase [plan de herramientas y análisis](analysis-plan.md), con fuentes del fabricante/proyecto y criterios de aceptación por etapa. No se han instalado esas herramientas ni adaptado/exportado assets.

Para repetir el inventario desde la raíz del checkout, con Python 3.11 o posterior:

```powershell
python tools/inventory_games.py --root ../Juegos --output docs/research/game-inputs-2026-10-21/inventory.json
python -m unittest discover -s tests -p test_inventory_games.py -v
```

El programa solo abre entradas en modo `rb`, hace lecturas acotadas y escribe un JSON fuera del directorio de entrada. No es extractor, desencriptador ni verificador criptográfico de autenticidad. No exporta bloques de juego ni tickets. Una lectura fallida o sondeo incompleto debe conservarse como error, no como archivo validado.

## Comprobaciones realizadas

Las seis pruebas nuevas usan estructuras sintéticas: truncamiento, límites CIA, metadatos TMD, SFO inválido, extensión ISO engañosa y CRC 7z que cruza una frontera de partes con corrupción deliberada. Todas pasaron. La ejecución amplia encontró un fallo en la prueba UDP preexistente del monitor (0 mensajes recibidos frente a 3 esperados) dentro del entorno restringido; las otras 15 pruebas pasaron. No se modificó el monitor ni se realizó ensayo con Vita. La atribución del fallo al entorno es hipótesis, no diagnóstico demostrado.

Fuentes consultadas el 21-10-2026: [implementación CIA de pyctr](https://github.com/ihaveamac/pyctr/blob/master/pyctr/type/cia.py), [TMD de pyctr](https://github.com/ihaveamac/pyctr/blob/master/pyctr/type/tmd.py), [formato 7z](https://www.7-zip.org/7z.html). Los offsets TMD y alineación CIA se contrastaron con el código de pyctr. Las páginas 3dbrew CIA/TMD devolvieron 403; no se usaron como evidencia leída.

## Actualización de CI y documentación consolidada

CI del commit `1b68b5b` completada correctamente: [Monitor tests](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39547319058) y [Vita agent build](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39547319029). No convierte el fallo UDP local previo en un diagnóstico resuelto ni valida hardware. Véase [estado consolidado](../../PROJECT_STATUS.md) para áreas 01–10 y [catálogo Frontier](../frontier-classic/README.md) para su estado independiente.

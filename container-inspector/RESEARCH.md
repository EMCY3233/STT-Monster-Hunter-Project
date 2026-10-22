# Investigación en plataformas — 23-10-2026

Objetivo: contrastar IVFC RomFS 3DS y hashes por archivo ExeFS para un lector
C++17 propio de solo lectura. Sin claves, descifrado ni cambios a consola.

## Plataformas consultadas

- GitHub: Project_CTR/CTRTool, GodMode9, REA y RomFS-Explorer.
- 3dbrew, también mediante la publicación de Mikage: descripción del formato.
- GBAtemp y Reddit: búsqueda de experiencias con errores IVFC/ExeFS y referencias
  a herramientas. Se usan como pistas de investigación, no como especificación.
- Stack Overflow: la búsqueda específica de RomFS/3DS no produjo una respuesta
  técnica útil para este cambio. No se atribuye una solución a esa plataforma.

No se siguieron tutoriales para descifrar ni reconstruir imágenes; son operaciones
fuera del alcance autorizado de este lector.

## Evidencia primaria empleada

1. 3dbrew, ExeFS:
   https://docs.mikage.app/ExeFS/
   Cabecera de 0x200, diez registros de 16 bytes, offsets relativos a datos,
   hashes SHA-256 en orden inverso.
2. 3dbrew, RomFS:
   https://docs.mikage.app/RomFS/
   IVFC 0x10000, descriptores de tres niveles, metadatos de nivel 3.
3. Project_CTR, ctrtool/ivfc.c, commit fijado:
   https://github.com/3DSGuy/Project_CTR/blob/046bb359ee95423938886dbf477d00690aaecd3e/ctrtool/ivfc.c
   Contraste del orden físico, alineaciones y hash de bloques completos.
4. GodMode9, arm9/source/game/romfs.c:
   https://github.com/d0k3/GodMode9/blob/master/arm9/source/game/romfs.c
   Blob consultado: 28badcc4d04ac3665d7d776327624dc0b3578995.
   Contraste independiente de offsets físicos y capacidad de tablas de hashes.
5. REA, límite del proveedor Ghidra para Windows:
   https://github.com/morluto/rea/blob/main/docs/windows-ghidra-p0.md
   No establece soporte de ARM11/3DS. REA no sustituye este lector.

Se consultaron campos, disposiciones y algoritmos del formato. No se copiaron
implementaciones externas ni se añadió una dependencia de esas herramientas.

## Pistas de comunidad y alcance

- GBAtemp, historial de errores IVFC y exheader:
  https://gbatemp.net/threads/tutorial-how-to-decrypt-extract-rebuild-3ds-cia-cxi-files.383055/page-40
- Reddit, referencia a Project_CTR:
  https://www.reddit.com/r/3dshacks/comments/ye2d6w/
- GitHub, explorador RomFS en consola:
  https://github.com/Ryuzaki-MrL/RomFS-Explorer

Estas páginas no acreditan compatibilidad MH4U ni integridad de la imagen local.
Las afirmaciones funcionales del lector deben apoyarse en pruebas sintéticas,
ejecución local y CI identificadas por commit; los bytes comerciales quedan
fuera del repositorio.

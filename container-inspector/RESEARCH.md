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

## Ampliación: índices de nombres RomFS

La repetición del ciclo se centra en el siguiente pendiente, los buckets de
directorios y archivos. Se contrastó la especificación 3dbrew con libctru y
GodMode9 para el hash padre/UTF-16, módulo del número de buckets y cadena
nextHash. Se valida la tabla completa, no solo una búsqueda concreta.

Fuente primaria adicional:
https://github.com/devkitPro/libctru/blob/master/libctru/source/romfs_dev.c
Blob consultado: ea5c4da46270311b9b3b1fe3d2907d9f3912e032.
Formato de estructuras:
https://github.com/devkitPro/libctru/blob/master/libctru/include/3ds/romfs.h

La búsqueda específica en GBAtemp, Reddit y Stack Overflow se repitió. Las
conclusiones de implementación se apoyan en especificación y fuentes primarias,
sin atribuir validación de la imagen privada a publicaciones de comunidad.

Pruebas nuevas reconstruyen los hashes IVFC tras alterar el índice, de modo que
el rechazo comprueba la semántica de buckets y no solo la integridad de bytes.
También se prueba una cadena válida con colisiones, raíz, árbol anidado, tabla
de archivos vacía, nombres con unidades UTF-16 fuera de ASCII y no mostrar
nombres de archivos cuando solo se verifica el índice.

## Firmas y recursos MH4U

Fuentes primarias adicionales:
- NCCH/exheader y límites de confianza:
  https://docs.mikage.app/NCCH/
  https://docs.mikage.app/NCCH/Extended_Header/
- Perfil RSA público, exponente 01 00 01 y PKCS#1 SHA-256, CTRTool fijado:
  https://github.com/3DSGuy/Project_CTR/blob/046bb359ee95423938886dbf477d00690aaecd3e/ctrtool/ctr.c
- ARC MH4U:
  https://github.com/svanheulen/mhff/wiki/MH4U-rArchive-Format
  https://github.com/svanheulen/mhff/blob/master/n3ds/arc.py
  Blob consultado: cef2abdeeb74ac278bf9fc57e97c529d8d963958.
- TEX MH4U:
  https://github.com/svanheulen/mhff/wiki/MH4U-rTexture-Format
  https://github.com/svanheulen/mhff/blob/master/n3ds/tex.py
  Blob consultado: 1f8f48d4d248479f76e780ffcd60e82d096c0305.

Búsquedas de comunidad: GBAtemp MH4U/MHX ROM Hacking Guide, ZenHAX MH4U ARC
y Reddit MH4U. Se consultaron como pistas; no se descargaron recursos.
Los campos y disposiciones se contrastaron con las fuentes primarias; no se
copiaron implementaciones. Las operaciones criptográficas se limitan a comprobar
una firma pública embebida y datos sintéticos generados durante las pruebas.

La revisión de PR #7 encontró un extractor ya existente para ARC17/MHXX.
La imagen actual declara ARC19/MH4U: no se modifica aquella rama ni se generalizan
sus resultados. El lector nuevo solo comprueba metadatos/rangos ARC19 y cabeceras
TEX A5; conversión, zlib, MOD/MRL/LMT y fidelidad gráfica siguen fuera de alcance.

Con un módulo público aportado por la misma imagen se puede comprobar coherencia
de firma, pero no establecer la confianza del emisor. La ausencia de una raíz
externa confiable mantiene la autenticidad bloqueada. No se incorporan ni
exportan claves de Nintendo o del archivo, ni se elude esta limitación.

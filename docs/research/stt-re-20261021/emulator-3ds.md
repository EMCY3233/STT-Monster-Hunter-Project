# 3DS: Azahar, revisión documental del 21-10-2026

No se ha descargado, instalado ni ejecutado Azahar en esta revisión. Los ensayos locales previos fueron con Citra Nightly 2104; no se convierten en resultados de Azahar. Switch/GU queda fuera del alcance.

## Versión y procedencia

La versión estable observada es **2126.2**, publicada 2026-10-08 23:12 UTC, commit **219d743a1e698101fe1ab8bef43e6563126c3c27**. La página de GitHub la identifica como release inmutable. Fuente: [release](https://github.com/azahar-emu/azahar/releases/tag/2126.2), [commit](https://github.com/azahar-emu/azahar/commit/219d743a1e698101fe1ab8bef43e6563126c3c27). Entre los cambios figuran correcciones de instalación CIA y de los servidores GDB/RPC. La selección estable evita confundirla con 2127 alpha.

La lista oficial expandida conserva tres variantes Windows, aunque la página de descargas enfatice otras: [assets y SHA-256 publicados](https://github.com/azahar-emu/azahar/releases/expanded_assets/2126.2). Son hashes de publicación, **no hashes de descargas verificadas en este entorno**:

| Archivo ZIP portátil | SHA-256 publicado |
| --- | --- |
| azahar-windows-msvc-2126.2.zip | 4412eac8d13123c8840f11890fc26e5b0e4c76d16aa28a608941377b948a9db0 |
| azahar-windows-msys2-2126.2.zip | aa6d4c631c883355e50f5f62fd26a0e053d63e4cc29b8ded6b3b7d175ec3864e |
| azahar-windows-mxe-2126.2.zip | dae9f107d9141ebc0e64ba251f9796393aab651cf3437ab9e083b45354624486 |

URL de cada archivo: `https://github.com/azahar-emu/azahar/releases/download/2126.2/` seguido de su nombre exacto. Para futura instalación, conservar fecha, tamaño real, hash local, URL final y versión del ejecutable. No se necesita sustituir Citra ni utilizar sus perfiles personales.

El [README de 2126.2](https://github.com/azahar-emu/azahar/blob/2126.2/README.md) explica que Azahar reúne Lime3DS y el fork de PabloMK7, derivados de Citra. Documenta Windows 10 de 64 bits, CPU x86-64 con SSE4.2 y rendimiento monohilo Passmark superior a 1.800, GPU OpenGL 4.3 o Vulkan 1.1 y RAM mínima 2 GB/recomendada 4 GB; Windows ARM no está soportado. No se ha comprobado aquí el cumplimiento del ordenador local. La [FAQ oficial](https://azahar-emu.org/pages/faq/) identifica Visual C++ Redistributable como dependencia de la variante MSVC cuando falta MSVCP140_ATOMIC_WAIT.dll.

## Arquitectura e instrumentos

El [núcleo estable](https://github.com/azahar-emu/azahar/blob/2126.2/src/core/core.cpp) selecciona ARM_Dynarmic cuando se habilita JIT en x86-64/ARM64 y ARM_DynCom como alternativa; contiene kernel/servicios HLE y selección DSP HLE o LLE, además de instrumentación GDB. No es una emulación exclusivamente HLE. La [implementación DSP LLE](https://github.com/azahar-emu/azahar/blob/2126.2/src/audio_core/lle/lle.cpp) usa Teakra para ejecutar el DSP. La elección de backend no demuestra exactitud temporal ni compatibilidad de un juego. OpenGL/Vulkan son rutas de representación del hardware gráfico 3DS hacia la GPU anfitriona; la disponibilidad indicada por requisitos no sustituye una prueba visual.

Precisión de licencia: el repositorio incluye [license.txt GPL versión 2](https://github.com/azahar-emu/azahar/blob/2126.2/license.txt); muchos encabezados, incluido loader.cpp, permiten GPLv2 o posterior. **core.cpp en esa misma versión declara GPLv3 o posterior**. Registrar estas declaraciones por componente; no atribuir una licencia uniforme GPL2-only a todo el árbol ni copiar código sin revisar archivo y dependencias. El código del emulador no es el código fuente de Monster Hunter.

El [gestor de rutas](https://github.com/azahar-emu/azahar/blob/2126.2/src/common/file_util.cpp), líneas 863–885, en Windows prefiere `user` junto al ejecutable si existe y, en caso contrario, usa AppData Roaming/Azahar. Por tanto, crear una carpeta de instalación exclusiva con `user` antes del primer arranque y verificar en el log la ruta usada. [common_paths.h](https://github.com/azahar-emu/azahar/blob/2126.2/src/common/common_paths.h) separa config, cache, sdmc, nand, sysdata, log, dump, load y states. Archivar el perfil nuevo completo, sin importar saves existentes. [logging/backend.cpp](https://github.com/azahar-emu/azahar/blob/2126.2/src/common/logging/backend.cpp) rota el log anterior y limita escritura a aproximadamente 100 MiB; conservarlo después de cada ensayo antes del siguiente arranque. GDB/RPC son capacidades documentadas y dependientes de compilación/configuración; aún no se ha verificado que funcionen en un binario local.

## Formatos y bloqueo real

El [loader de 2126.2](https://github.com/azahar-emu/azahar/blob/2126.2/src/core/loader/loader.cpp) reconoce extensiones `.cci`, `.3ds`, `.zcci`, `.cxi`, `.app`, `.zcxi`, `.3dsx`, `.z3dsx`, `.elf` y `.axf`. CIA/ZCIA se instalan a través del servicio AM, no son un ejecutable directo intercambiable. Importante: **la versión estable actual vuelve a reconocer .3ds**; no arrastrar el rechazo de extensiones de versiones anteriores. El reconocimiento de extensión no valida el contenido ni resuelve cifrado.

El [contenedor NCCH](https://github.com/azahar-emu/azahar/blob/2126.2/src/core/file_sys/ncch_container.cpp), líneas 217–219 y 246–248, devuelve ErrorEncrypted si no está activado no_crypto. La [instalación CIA local](https://github.com/azahar-emu/azahar/blob/2126.2/src/core/hle/service/am/am.cpp), líneas 1123–1125, aborta contenido cifrado. Ese archivo también contiene flujos internos de instalación autorizada; su existencia no significa que el usuario pueda abrir una CIA cifrada arbitraria desde la interfaz. No se investiga obtención de claves ni se repite el bloqueo de Citra con las bases cifradas.

Las tres bases CIA locales MH3U/MH4U/MHXX siguen cifradas. **Actualización posterior a esta consulta:** se encontró una entrada NCSD .3ds de MH4U EUR legible y se ejecutó una vez en Citra; véase [revisión nueva](citra-current-inputs.md). No extrapolar el bloqueo CIA a ese archivo distinto. El update MHXX legible **no sustituye la base**; el fallo previo del update aislado en Citra no califica el juego completo en Azahar.

## Compatibilidad pública frente a las entradas locales

Fuente primaria consultada: [compatibility_list.json](https://github.com/azahar-emu/compatibility-list/blob/master/compatibility_list.json), instantánea web del 21-10-2026. El [README del tracker](https://github.com/azahar-emu/compatibility-list) advierte que su clasificación excluye Vulkan; la FAQ avisa de posible antigüedad de informes. La [escala oficial](https://github.com/azahar-emu/compatibility-list/blob/master/CONTRIBUTING.md) denomina 1 Great y 2 Okay. El JSON agrupa títulos/regiones y no aporta por sí solo versión exacta del juego, revisión del emulador ni equipo probado.

| Entrada local | Cobertura del JSON consultado | Interpretación |
| --- | --- | --- |
| MH3U EUR 00040000000B1D00 | ID no encontrado. MH3U listado con USA 00040000000AE400, código 2 | No extrapolar clasificación USA a la base EUR local |
| MH4U EUR 0004000000126100 | ID incluido en agrupación MH4U, código 1 | Evidencia documental favorable para título/región, sin verificación de revisión local |
| MHXX JPN 0004000000197100 | ID no encontrado | Compatibilidad local no verificada; ausencia del tracker no equivale a incompatible |

## Próximas aceptaciones reproducibles

1. **Prioridad independiente de emulación**: comprobar la compresión inversa BLZ/LZSS de la sección `.code` legible del update MHXX y los rangos del exheader; la fuente NCCH de Azahar contiene una implementación de referencia. Entrada ya identificada de 7.419.468 bytes. Aceptación: hashes antes/después, consumo y límites coherentes, tamaño de segmentos explicable, salida privada; ningún salto a hipótesis de IA/hitbox. No ejecutar el update aislado ni añadir valores comerciales al informe público.
2. La entrada .3ds MH4U recién comprobada satisface ahora la precondición de base legible. Para una futura comparación con Azahar, descargar ZIP estable oficial con hash publicado, crear `user` aislado, comprobar hardware y versión. Un único ensayo de 30 s, red y plugins desactivados, sin saves importados: aceptación mínima apertura de base con TitleID correcto, log conservado, salida controlada y hash original sin cambios. Menú visible requiere captura/inspección; log de carga no basta para afirmarlo. No medir gameplay ni FPS si solo carga.
3. Posterior y condicionado al menú: un ensayo acotado para validar GDB o RPC con memoria de una aplicación homebrew propia, antes de instrumentar código comercial. No instalar emuladores ahora solo para volver a observar cifrado.

Bloqueos cerrados documentalmente: las CIA base siguen cifradas, update no base, falta de cobertura pública exacta para MH3U EUR/MHXX y ausencia de prueba local Azahar. La investigación está completada para esta aceptación; esos bloqueos no justifican repetir arranques inalterados.

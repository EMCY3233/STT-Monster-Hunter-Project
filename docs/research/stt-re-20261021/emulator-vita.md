# Vita3K — revisión documental, 2026-10-21

Estado local: no instalado, no ejecutado, sin firmware descargado. La evidencia de compatibilidad siguiente pertenece a terceros y no verifica la copia local.

## Procedencia y mantenimiento

Release oficial mutable `continuous`, Build 4211, publicado 2026-10-21T12:46:36Z, correspondiente a commit `ed0b71271fa9632c2d81532ef87da0cddf2bc970`. API oficial: https://api.github.com/repos/Vita3K/Vita3K/releases/tags/continuous . Windows x64 `windows-latest.zip`, asset ID 662486970, 37,858,850 bytes, digest **publicado por GitHub** SHA256 `e4e551bc4f626fef5b14c6a800ff6a1c8d8348c6546b8aa4cd5bc10727ce9530`, https://github.com/Vita3K/Vita3K/releases/download/continuous/windows-latest.zip . No descarga ni hash local efectuados. El nombre mutable debe acompañarse de asset ID/fecha/commit/digest en cualquier ensayo futuro. La firma verificada del commit no demuestra por sí sola firma Authenticode del ZIP/EXE.

README describe proyecto experimental y GPLv2; los archivos fuente revisados llevan GPLv2-o-posterior. Código abierto del emulador no equivale a código fuente de Monster Hunter. README: https://github.com/Vita3K/Vita3K/blob/ed0b71271fa9632c2d81532ef87da0cddf2bc970/README.md .

## Arquitectura y observación

El `init_cpu` actual construye `DynarmicCPU` directamente; sus callbacks usan `Dynarmic::A32`, registros ARM/Thumb y caché JIT. El callback llamado `InterpreterFallback` registra una instrucción no implementada: no prueba un intérprete general funcional alternativo. No describir Unicorn como backend seleccionable actual basándose en documentación histórica/licencias. Fuentes pinned:

- `vita3k/cpu/src/cpu.cpp`, blob `0b51c46b25073e08e93ee2c5a9465121d790285f`, líneas 43–56.
- `vita3k/cpu/src/dynarmic_cpu.cpp`, blob `54e89f88b4c5c03da0e35b76320d1c10881b2a3d`, callbacks A32; `InterpreterFallback` líneas 292–294.
- `vita3k/config/include/config/config.h`, blob `2f0b102d31435b32230106ec183ed63946bf7cda`: renderer Vulkan por defecto, módulos automáticos, lista LLE, GDB y espera de depurador, trazas, exportación de texturas configurables.
- `vita3k/shader/src/spirv_recompiler.cpp`, blob `28c781b61a810fd902aac9d921c0a410ab23285c`: recompilación shader SPIR-V y conversión GLSL; no implica recuperación del modelo/esqueleto/IA original.

Las rutas de estos archivos se resuelven en https://github.com/Vita3K/Vita3K/blob/ed0b71271fa9632c2d81532ef87da0cddf2bc970/ .

Quickstart oficial: Windows de 64 bits, x86-64, 4 GB y OpenGL 4.4 mínimos; recomienda AVX, 8 GB, Vulkan y shader interlock. Visual C++ 2015–2022 redistributable si falta el runtime. Algunos módulos del sistema necesitan firmware para emulación LLE; la guía enlaza Sony para firmware y menciona paquete de fuentes adicional. Son dependencias documentales, no instaladas. Acepta PKG, VCI, NoNpDrm, FAGDec y contenido manualmente descifrado; archivos instalables ZIP/VPK/VCI. Vitamin no soportado y MaiDump inestable. Copiar directorios no vale genéricamente para NoNpDrm/PKG/VCI. Fuente: https://vita3k.org/quickstart.html . No se adoptan sus procedimientos que modifican la consola.

## Perfil aislado y registros

En Windows, crear un directorio **portable** junto al ejecutable antes del primer inicio hace que `init_paths` sitúe VitaFS en `portable/fs`, configuración y logs dentro de `portable`, caché en `portable/cache`. Código `vita3k/app/src/app_init.cpp`, blob `d7ee705f0e288e05e758127f8f7239a74702f760`, líneas 267 y 283–292. Es más preciso que asumir que cambiar solo `--config-location` aísla todo. `vita3k/main.cpp` también evidencia savedata bajo `ux0/user/00/savedata/<TitleID>`; no apuntar a perfiles personales.

`vita3k/config/src/config.cpp`, blob `78542d3f561edada59f8d809208877467d18129c`: `--config-location`, `--archive-log`, `--log-level`, `--installed-path`, `--self`, `--lle-modules`; `--recompile-shader` procesa GXP hacia SPIR-V/GLSL. `vita3k/util/src/logging.cpp`, blob `816c62970bb7c238e8af71ee8ec2e5989cd0b4a4`: `vita3k.log`, apertura con truncamiento; conservar cada recibo/log por ensayo antes de otro inicio. `vita3k/gdbstub/src/gdb.cpp`, blob `92dc5d1716f65f0fe604493cccc5a93ca1feb9db`: registros, memoria, breakpoints y protocolo GDB implementados; no ejecutados aquí. No habilitar servidor de depuración ni dumps comerciales por defecto.

## Frontier: compatibilidad exacta y límites

| Fuente primaria | Identidad y entorno | Resultado comunicado y límite |
|---|---|---|
| https://github.com/Vita3K/compatibility/issues/2449 | PCSG00350, Z 1.96; v0.2.0 build3572 commit1b0e65e6; Windows11/i7-9750H/GTX1660Ti32GB; Dynarmic, Vulkan/OpenGL | Etiquetas oficiales Bootable/black screen/online-only. No es prueba de Z01.99 local. |
| https://github.com/Vita3K/compatibility/issues/2449#issuecomment-4351432909 | v0.2.1 build3965; LinuxMint22.3/Ryzen5600/RX6600/16GB/Vulkan; commit corto informado9916d86 con enlace defectuoso | Informa sin cambio. No afirma nueva versión app. |
| https://github.com/Vita3K/compatibility/issues/2449#issuecomment-6296770619 | **2026-10-20T17:17:13Z**; v0.2.1 build4208; mismo entorno Linux/Vulkan; commit y revisión app omitidos | Llega a pantalla y se congela, falta texto; autor propone Intro/Online-only/Graphics bug/Missing Text. Propuesta de usuario no reemplaza etiquetas oficiales ni demuestra jugabilidad. Log adjunto no descargado. |
| https://github.com/Vita3K/Vita3K/issues/2509 | Abierto2023-04-21, cerrado; PCSG00350 Z1.99; v0.1.6 build3107-18b85823; OpenGL IntelGen11, Dynarmic | Pantalla amarilla histórica; log carga eboot y módulos, llamadas LLE HTTP/SSL, imports NP no implementados. Coincide TitleID/revisión con patch local, no build actual ni hashes del juego. Cierre del issue no demuestra arreglo ni compatibilidad actual. |

La copia local conocida por el encargo contiene baseG1.00 y patchZ01.99; ZZ no confirmado. La colección app/patch/rePatch no ha sido validada como entrada instalable. Hay 9 metadatos excluidos, sin contenido de licencias examinado; estado PFS/SELF y precedencia rePatch continúan pendientes. Firma SCE no equivale a ejecutable listo. Los JKR/ECD legibles sí permiten experimentos estáticos independientes, pero no demuestran arrancabilidad. La etiqueta online-only y los imports de red documentados impiden prometer funcionamiento offline; no se contactan servicios ni cuentas.

## Siguiente aceptación propuesta

Prioridad baja para arrancar Frontier mientras falte entrada inequívocamente legible/instalable y dependa de red. No instalar Vita3K solo para repetir ese bloqueo. La siguiente prueba PC útil dentro de este frente sería un **clasificador estático de estructura SELF** sobre la copia rePatch ya accesible: comprobar longitudes, versión y límites de cabecera/segmentos sin descifrar ni ejecutar, guardar solo metadatos y SHA256 privado/original antes-después. Aceptación: distinguir SCE/SELF estructuralmente válido de simple magic, o emitir error exacto; cero claves, cero firmware, cero alteración del banco y cero extracción comercial pública. Esto no resuelve PFS/licencias/online ni permite declarar compatible el juego. Antes de codificar, revisar herramientas ya existentes para no repetir análisis de cabeceras completados.

Para futura prueba de emulación condicionada: asset oficial pinned/digest verificado; portable fresco; entrada válida de propiedad del usuario ya disponible, perfil sin red/cuentas/guardados; 15 s máximo para observar solo carga de módulos y estado de pantalla; éxito de loader separado de jugabilidad. No ejecutar aún por bloqueo de entrada y baja utilidad frente al análisis estático accesible.

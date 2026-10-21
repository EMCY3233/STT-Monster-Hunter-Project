# Emuladores y primer descifrado contrastado: MHFU

21-10-2026, Europe/Madrid. El usuario autorizó el descifrado y pidió apoyarse en emuladores. GU Switch continúa excluido. Se realizó una prueba real con PPSSPP; Azahar y Vita3K se investigaron documentalmente y no se presentan como ejecutados.

## PPSSPP 1.20.4: preparación y evidencia

No se localizaron PPSSPP/Azahar/Vita3K en PATH, en el proyecto ni en las ubicaciones estándar consultadas. Esto no es un inventario completo del PC. Se descargó la edición Windows portátil desde el [sitio oficial](https://www.ppsspp.org/download/) y se extrajo en `analysis-local/emulators/ppsspp-1.20.4`, fuera de Git. Sin instalador, cambios de PATH ni configuración de emuladores preexistentes.

- ZIP oficial: `https://www.ppsspp.org/files/1_20_4/ppsspp_win.zip`, SHA-256 `a60f04ebdb0b5f1655422bd7f88349a46999b17ad5115d6ddb290c3934bd5163`.
- Ejecutable x64: versión `v1.20.4`, SHA-256 `27d3edbb06dc623dab60877d3e3a975aef4034c7d4fac464e92fd4998864d2ec`.
- Authenticode: firma verificada por Windows. El hash identifica esta descarga; no se presenta como cotejo con un digest independiente publicado.
- El ZIP contiene ejecutables gráficos x86/x64, **sin PPSSPPHeadless**. Las opciones nuevas del código `master` no se asumieron disponibles en este binario estable.

El [código de la versión 1.20.4](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Windows/main.cpp) confirma que, sin `installed.txt`, la memoria portátil reside junto al ejecutable. Se creó configuración propia en esa carpeta, con actualizaciones y WLAN desactivadas. Se usó D3D11, proceso oculto y límites de tiempo; no se abrieron partidas existentes, no se inyectaron controles ni se instalaron firmware/plugins. Los procesos propios quedaron terminados al alcanzar el límite.

## Prueba de carga y descifrado

Entrada única: ISO MHFU, SHA-256 `5ebab623367e78c68033bb4b40e454b84ea974c4aa5e9819641232181d3f8139`. Dos ensayos controlados:

1. Arranque diagnóstico de unos 20 s. El log identifica ULES01213, carga `disc0:/PSP_GAME/SYSDIR/EBOOT.BIN`, registra descifrado de envoltura ~PSP y carga de ELF. Posteriormente hay ejecución de hilos, llamadas de audio y presentación de framebuffers.
2. Arranque de unos 6 s con la opción soportada **DumpFileTypes=1**, que habilita exclusivamente la salida EBOOT del emulador. Se obtuvo un archivo local en `memstick/PSP/SYSTEM/DUMP/ULES01213_EBOOT.BIN`.

La opción se contrastó con [Config.cpp](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/Config.cpp), [ConfigValues.h](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/ConfigValues.h), [el cargador de módulos](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/HLE/sceKernelModule.cpp) y [la escritura del volcado](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/System.cpp). No se reprodujo el algoritmo criptográfico ni se buscaron claves de terceros.

**Resultado del volcado:** 1.910.384 bytes, SHA-256 `64937c521286fc8423076e644089881c5fe051bed2565e5061dda8aec0b45e10`, cabecera ELF32 LE/MIPS y 620 secciones reconocidas por el lector local. El prefijo de **1.910.044 bytes es idéntico byte por byte a BOOT.BIN** del mismo ISO, SHA-256 `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`.

Los **340 bytes adicionales no son todos cero**. Su contenido y significado no se validaron: no se tratan como instrucciones, secciones nuevas ni parte canónica del ELF. La longitud del buffer que exporta el emulador puede superar la longitud del ELF útil. No se infiere que el hash del volcado completo vaya a ser estable entre ejecuciones; la comparación reproducible relevante es el prefijo idéntico al BOOT ya conocido.

En ambos ensayos el ISO conserva su SHA-256 completo antes y después. El archivo descifrado permanece **solo local**; no se publica código, volcado de memoria, ISO, clave ni recurso comercial. Obtener el mismo ELF que BOOT no identifica todavía funciones de combate/IA ni descifra DATA.BIN.

## Qué prueba y qué no prueba la ejecución

El segundo log contiene 15.883 líneas: un segmento cargable copiado, 6.192 registros de cambio de contexto y 116 registros de presentación de framebuffer. Estos conteos describen eventos del log, no FPS, imágenes visualmente correctas ni rendimiento medido. No hubo validación visual o partida jugada.

Se registraron cinco errores al añadir fuentes TTF del frontend y uno al abrir `font/zh_gb.pgf` ausente. Se conservan esos fallos; no se descargaron fuentes/firmware para ocultarlos. El proceso se terminó por el límite del ensayo: su código de salida 1 **no es una terminación normal del juego ni prueba por sí sola de fallo de arranque**.

Los logs completos permanecen locales. [emulator-evidence.json](emulator-evidence.json) contiene procedencia, recibos y comparación. No se publica su transcripción completa ni se declara que todo el juego sea compatible por esta prueba breve.

## Frontier: nueva revisión y corrección del sondeo

Se detectó un error en el lector previo: los marcadores candidatos ECD/EXF estaban invertidos. Las cadenas correctas son `ecd`/`exf` seguidas de 0x1A, según [la documentación del proyecto](https://github.com/Houmgaor/FrontierTextHandler). Se corrigió el lector y se añadieron cuatro pruebas sintéticas. Los informes anteriores se conservan como antecedentes y no se reinterpretan como pruebas de ausencia de esos formatos.

Relectura con el lector corregido, 06:55:21 UTC:

- 4.673 rutas enumeradas; 4.663 archivos leídos, 2.504.734.845 bytes.
- Nueve entradas de licencias/paquetes excluidas sin lectura de su contenido; un `.partial` excluido.
- Dos SFO reconocidos y 4.661 archivos sin coincidencia con las firmas del sondeo. No se detectó una capa ECD/EXF/JKR directamente en esas cabeceras; no es prueba de inexistencia bajo otra capa.
- La enumeración siguió cambiando durante el ensayo; la copia completa no se da por verificada.

Metadatos legibles: base `app/PCSG00350` con título Frontier G/APP_VER 01.00; ahora hay también `patch/PCSG00350`, cuyo SFO indica **Frontier Z/APP_VER 01.99**, CATEGORY gp y el mismo TITLE_ID. Esto supera la observación anterior de que solo existía la base G. **No demuestra versión ZZ ni compatibilidad funcional**.

También están disponibles en la copia local `sce_pfs/files.db` (1.183.744 bytes) y `unicv.db` (9.995.264 bytes). La estructura es coherente con un conjunto PFS; no basta por sí sola para demostrar la causa de cada cabecera no reconocida. No se ejecutó ReFrontier contra entradas de capa exterior desconocida.

## Azahar y Vita3K: aplicación real al bloqueo

| Emulador/herramienta | Evidencia primaria | Decisión para esta etapa |
|---|---|---|
| Azahar / 3DS | [Publicación 2124.3](https://github.com/azahar-emu/azahar/discussions/1702): soporte de extensión .3ds restaurado, aplicaciones cifradas siguen sin soporte | No se instala como supuesto descifrador de los CIA base. El parche MHXX por sí solo no acredita una aplicación base arrancable. Preparar prueba cuando haya entrada completa legible. |
| Vita3K / Vita | [Quickstart](https://vita3k.org/quickstart.html): requiere datos de sistema y un formato de entrada soportado; contempla varios tipos de dump/importación | No se instala ni se modifica firmware para probar una copia incompleta y con capa exterior sin identificar. No se confunde importar un juego con validar sus modelos/IA. |
| psvpfstools / PFS | [README del autor](https://github.com/motoharu-gosuto/psvpfstools): permite trabajo en PC, requiere material específico y backend criptográfico para el conjunto PFS | Falta material criptográfico verificado en este encargo. Su backend puede usar un servicio externo: no se contactó ni se enviaron datos/licencias a ningún servicio. No se buscaron claves públicas o de terceros. |
| ReFrontier | [Proyecto del autor](https://github.com/Houmgaor/ReFrontier): ECD/EXF y JKR son capas propias de datos Frontier | No aplicar automáticamente a archivos que no presentan esas firmas. Identificar primero el contenedor exterior. |

## Reproducción y siguiente paso

Herramienta propia: `tools/stt_re/run_ppsspp_probe.py`. Requiere una copia portátil aislada, sin `installed.txt`. Si existe una configuración distinta de la creada por el ensayo, se detiene para no sobrescribirla. Con volcado habilitado rechaza un ejecutable dentro de Git. Los destinos deben ser nuevos.

```powershell
& $python tools/stt_re/run_ppsspp_probe.py --exe "$projectRoot/analysis-local/emulators/ppsspp-1.20.4/PPSSPPWindows64.exe" --iso "$projectRoot/Juegos/MHFU/Monster Hunter Freedom Unite.iso" --out "$projectRoot/analysis-local/ppsspp-probe-new" --seconds 6 --dump-eboot
```

La configuración adicional del ensayo habilita solo la salida EBOOT, sin habilitar PRX/audio ni plugins. El emulador no sobrescribe un dump ya existente; la herramienta entregada además rechaza una carpeta DUMP no vacía cuando se pide extraer, para no atribuir una salida antigua a una ejecución nueva. Para otra extracción independiente debe prepararse otra copia portátil de trabajo. No borrar evidencias ni reutilizar perfiles de usuario.

Prioridades: mapear imports/relocaciones del ELF PSP contrastado; estudiar DATA.BIN por separado; verificar la copia Frontier una vez terminada y resolver su capa exterior/material de acceso; conservar los experimentos LMT de MHXX. Las **40 pruebas sintéticas** de lectores pasan. La prueba del emulador es una evidencia adicional distinta de esos tests y de cualquier prueba física en PS Vita.

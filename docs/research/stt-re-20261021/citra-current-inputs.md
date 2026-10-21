# CIA y nueva base MH4U .3ds: revisión con Citra

Fecha: 2026-10-21. Petición directa del usuario: «revisa los archivos cia y 3ds con el emulador». Resultado: cinco archivos CIA cotejados con pruebas anteriores y **una nueva ejecución de una base NCSD .3ds de MH4U EUR**. No se descargaron juegos, claves o firmware ni se alteró el banco.

## Entrada nueva realmente accesible

Ruta: `Juegos/Monster Hunter 4 Ultimate (Europe) (En,Fr,De,Es,It)/Monster Hunter 4 Ultimate (Europe) (En,Fr,De,Es,It).3ds`.

- Tamaño: **4.294.967.296 bytes** (4 GiB).
- SHA256 antes y después: **`3832beef353d134bcba6ef83dc987e7ae228c43dc32a6ba52519f5f103f52581`**, idénticos.
- Firma exterior NCSD; particiones NCCH 0, 1 y 7 dentro del archivo, con `no_crypto=true` en las tres cabeceras.
- Program ID leído: **0004000000126100**, corresponde a la base MH4U EUR identificada por el proyecto. Revisión exacta del juego/actualización: **no acreditada**; no inferirla del nombre o del formato NCCH.
- Procedencia acreditada: presencia y lectura en la carpeta local del usuario. Fuente de adquisición y coincidencia con un volcado externo: no verificadas. No se ha descargado esta entrada durante el encargo.

La nueva entrada es legible por su contenido, no por terminar en .3ds. La CIA MH4U anterior tiene otro tamaño/hash y está cifrada; no se ha demostrado equivalencia de contenido/revisión entre ambas. No se convirtió ni descifró la CIA para producir esta NCSD.

| Partición | Offset | Longitud | Límite y flag |
|---|---:|---:|---|
| 0 | 16.384 | 2.727.489.536 | dentro del archivo, NCCH no_crypto |
| 1 | 2.727.505.920 | 7.258.112 | dentro del archivo, NCCH no_crypto |
| 7 | 2.734.764.032 | 32.186.368 | dentro del archivo, NCCH no_crypto |

## Ensayo nuevo y alcance de lo observado

Citra Nightly2104 / HEAD-0ff3440, ejecutable SHA256 **`53087fb66a5e76bf6fe23bfe324c25c257c39b97fb1eefd8c69a8c917a104f27`**. Se copió el portátil existente a un directorio exclusivo `analysis-local/citra-mh4u-3ds-20261021/app`, con perfil `app/user` nuevo y configuración propia; sin claves, firmware o partidas importadas. La procedencia histórica del binario y sus límites siguen en [citra.md](citra.md).

Primer intento del wrapper anterior abortó **antes de lanzar Citra**, porque su comprobación de perfil vacío rechazaba la configuración recién escrita. Se conserva ese error. El wrapper privado del ensayo verificó que el perfil solo contenía esa configuración antes del lanzamiento. Hubo **una ejecución real**, sin pulsaciones.

Límite solicitado: 15 segundos; duración medida del proceso **15,641 s** incluyendo parada. `terminated_after_timeout=true`, código de salida **1 por terminación controlada**; no se presenta como un crash espontáneo. Telemetría configurada desactivada; no se activó multijugador. El registro **sí informa de un cliente UDP de entrada hacia 127.0.0.1:26760**: no afirmar aislamiento de red probado o ausencia de sockets. No se realizó análisis de tráfico ni conexión FTP.

El log identifica el perfil, Nightly2104, JIT, OpenGL, carga del título y actividad de servicios. A los ~7,16 s carga un componente DSP HLE y solicita inicializar hardware DSP; genera caché de shaders para 0004000000126100. También registra funciones no implementadas y archivos de datos de sistema/guardado ausentes o inicializados en el perfil nuevo. Estos mensajes acreditan progreso de ejecución respecto al rechazo de cifrado anterior; no acreditan que la imagen sea correcta ni que el audio suene bien.

Registro privado `app/user/log/citra_log.txt`: **16.548 bytes**, SHA256 **`6f3b4ebb2248ec15a08ebc3d6f4773df9213939a1fbfc7e99228b20aa49d6823`**. Recibo: `analysis-local/citra-mh4u-3ds-20261021/actual-trial/receipt.json`; conserva configuración, tiempos, hashes y lista de archivos creados. Se generaron metadatos nuevos dentro del perfil aislado; no se usaron guardados personales. Ningún log bruto, shader o recurso derivado comercial se publica.

**Aceptado:** base NCSD distinta, no cifrada según cabeceras, consumida por Citra, progreso de loader/servicios/DSP, original sin cambios. **Pendiente:** observación de pantalla, menú/intro, audio, controles, estabilidad prolongada y jugabilidad. `visual_observation=false`, `gameplay_verified=false`; FPS desconocidos.

## CIA actuales y resultados previos aplicables

Se releen cinco archivos físicos, cuatro hashes únicos. Todos coinciden con entradas de recibos previos de Citra; **no se repiten esas instalaciones**. [Evidencia actual con rutas/tamaños/hashes completos](citra-current-inputs-evidence.json), [resultados previos](citra.md).

| Entrada | Tamaño bytes | Revisión de esta campaña | Resultado del ensayo anterior |
|---|---:|---|---|
| CIA MH3U EUR | 1.871.489.344 | SHA actual coincide con recibo mh3u | CommonKey0 ausente; instalación rechazada |
| CIA MH4U EUR recompuesta | 2.734.762.304 | coincide con mh4u | mismo bloqueo cifrado; distinta de nueva NCSD |
| CIA MHXX JPN, original y copia local | 2.330.896.704 cada una | ambas coinciden con mhxx | mismo bloqueo cifrado |
| CIA update inglés MHXX | 36.897.728 | coincide con mhxx-patch y mhxx-patch-short | instalación acreditada en ruta corta; update no sustituye base; ensayo anterior directo del NCCH terminó con 0xC0000005 |

La actualización nueva corrige la conclusión general anterior «no hay base 3DS legible»: ahora hay una para MH4U. No cambia el estado cifrado de las CIA MH3U/MH4U/MHXX ni valida el update aislado de MHXX.

## Próxima aceptación útil

Una comprobación visual acotada de esta misma base con perfil nuevo puede aportar evidencia diferente. Necesita control/captura visual fiables en este entorno; los logs por sí solos no lo suplen. La superficie CUA disponible anuncia APIs nativas deshabilitadas, por lo que esta entrega **no declara observación visual realizada** ni repite el arranque solo para añadir los mismos mensajes. Capturas comerciales, si se obtienen en una fase con herramienta adecuada, permanecerán locales. Alternativa independiente: validar compresión y segmentos de .code MHXX ya legible, con flag y límites antes de descomprimir.

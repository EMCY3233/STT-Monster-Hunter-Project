# Emuladores: utilidad real para las entradas STT

Consulta: 2026-10-21, Europe/Madrid. Campaña documental sobre fuentes primarias y recibos locales anteriores. PSP/MHFU, 3DS/MH3U–MH4U–MHXX y Vita/Frontier; Switch/GU excluidos por indicación del usuario. La comparación documental no instaló ni ejecutó emuladores. Después, por petición directa del usuario, se ensayó una nueva entrada MH4U .3ds una vez en el Citra existente, con copia portátil y perfil nuevo: [resultado](citra-current-inputs.md). No se instaló Azahar ni Vita3K.

## Decisión y grado de evidencia

| Opción | Versión fijada para evaluar | Aplicación local y límite | Prioridad |
|---|---|---|---|
| PPSSPP / PSP | 1.20.4, commit `fa50bb1976065c4f8b1b47af227d367fe9771555` | ISO MHFU ULES01213 1.01 legible, portátil ya ensayado. Carga de secciones corroborada; menú, FPS, combate y lectura concreta del puntero importado no acreditados | Primera opción si una nueva observación de ejecución justifica otro arranque |
| Azahar / 3DS | 2126.2, commit `219d743a1e698101fe1ab8bef43e6563126c3c27` | Opción mantenida; las tres bases CIA cifradas siguen bloqueadas. El parche MHXX legible no sustituye la base | Preferido para futuras entradas compatibles; no instalar para repetir el bloqueo |
| Citra / 3DS | Nightly 2104, HEAD `0ff3440`, histórico | Ya ensayado: bases rechazadas por CommonKey ausente; parche instalado en ruta corta y arranque directo terminó con fallo del proceso | Conservar recibos; no repetir instalación o arranque sin un cambio causal |
| Vita3K / Vita | Continuous build4211, commit `ed0b71271fa9632c2d81532ef87da0cddf2bc970` | Experimental. Copia local PCSG00350 G1.00/Z01.99 no equivale a paquete instalable; PFS/licencias/ejecutable y servicios online pendientes | Documentación y diagnóstico de formatos primero; arranque pospuesto |

**Hechos locales** proceden de recibos con hash, no de listas públicas. **Hechos documentales** describen una versión o un informe de terceros. **Hipótesis** incluyen que un emulador ayude a observar estructuras aún desconocidas. Ninguna de estas categorías demuestra por sí sola hitboxes, IA, movimientos, rigs o viabilidad de un port.

El código fuente abierto de un emulador implementa una máquina y sus servicios. No es el código fuente del juego, ni demuestra una descompilación del ejecutable comercial.

## PSP: PPSSPP

Fuentes: [descarga oficial](https://www.ppsspp.org/download/), [desarrollo](https://www.ppsspp.org/docs/development/), [CLI](https://www.ppsspp.org/docs/reference/command-line/), [gráficos](https://www.ppsspp.org/docs/settings/graphics/) y código del commit fijado. Licencia del proyecto GPL-2.0-or-later, con atribuciones de componentes en LICENSE.TXT. CPU MIPS/VFPU mediante intérprete o recompilador JIT; también rutas IR. HLE implementa servicios PSP en el anfitrión, sin necesitar BIOS para uso normal. Esto no garantiza temporización idéntica al hardware.

Windows ofrece paquetes portátiles x64 y ARM64. Backends actuales Vulkan, OpenGL y Direct3D11; Direct3D9 fue retirado en 1.20. La documentación general de requisitos no establece un mínimo fiable para MHFU/1.20.4: no convertir una FAQ antigua en especificación actual. Loaders.cpp reconoce ISO/CSO/CHD, PBP PSP y ELF/PRX según firma/contexto; comprimir la ISO no resolvería sus formatos internos.

El [listado exacto ULES01213_1.01](https://report.ppsspp.org/game/ULES01213_1.01) incluye un autoinforme Windows64/Intel UHD600/1.20.4 «Perfect» de 2026-10-18 y resultados discrepantes con otros equipos/versiones. No coteja el hash de nuestra ISO ni certifica nuestra prueba. El recibo local documenta exe SHA256 `27d3edbb06dc623dab60877d3e3a975aef4034c7d4fac464e92fd4998864d2ec`, dos arranques limitados y logs de carga; ningún FPS ni validación visual. [Evidencia anterior](emulators.md), [contraste de imports](mhfu-import-runtime-review.md).

Sin installed.txt, Windows intenta usar memstick junto al ejecutable, pero recurre a Documents si no puede escribir. Una prueba aislada debe verificar la ruta efectiva y no reutilizar partidas. SAVEDATA y PPSSPP_STATE cumplen funciones diferentes. Logs, depurador remoto, visores JIT/shader y breakpoints pueden aportar evidencia. **Breakpoints.h advierte cobertura incompleta de accesos HLE**: ausencia de hits en un watchpoint no descartaría lectura por el loader. No activar un nuevo dump para repetir datos ya disponibles.

## 3DS y Vita

[3DS: requisitos, formatos, licencias, hashes publicados y compatibilidad](emulator-3ds.md). [Vita3K: arquitectura, perfil, binario y Frontier](emulator-vita.md). Azahar estable acepta actualmente .3ds además de .cci y rechaza NCCH cifrado. Su licencia debe revisarse por archivo: license.txt GPLv2 y core.cpp GPLv3-o-posterior. Vita3K actual usa Dynarmic; no confundir notas antiguas sobre Unicorn con backend actual. Frontier conserva informes de fallos, incluido un reporte build4208 de 2026-10-20, sin acreditar jugabilidad ni revisión local exacta. [Citra: resultados locales](citra.md) conserva la cadena de procedencia del binario histórico y sus límites de autenticidad. Su ZIP preservado en un archivo de terceros, enlazado desde el archivo mantenido por desarrolladores, no tiene una firma del desarrollador acreditada en este encargo.

## Plan de aceptación y bloqueos

| Orden | Experimento acotado | Entrada y condición previa | Aceptación; condición de parada |
|---|---|---|---|
| 1 | Auditar alfa de un lector TEX sobre una carga ya legible | TEX A6/ETC1A4 de 84 bytes, hash ya fijado; función revisada y pruebas sintéticas | Distinguir lectura de bytes de fidelidad de píxel; si el lector descarta alfa, documentar fallo y no presentarlo como decoder fiel |
| 2 | Revisar BLZ y segmentos del .code MHXX ya legible | ExHeader y .code del mismo parche, sin otra extracción o base cifrada | Confirmar flag de compresión, rangos/longitudes y salida acotada mediante referencia; parar si flag o límites no justifican descompresión |
| 3 | Observación visual inicial MHFU | PPSSPP existente, perfil efectivo aislado y hash ISO antes/después | Una observación identificada de menú/intro, sin pulsaciones ni partidas, con límite temporal; no inferir combate/FPS de una captura |
| 4 | Observar acceso a un import PSP | Antes de arrancar, demostrar que se puede armar instrumentación y que cubre el acceso relevante | Evento con dirección/tamaño/PC y origen CPU/HLE identificado; si no cubre HLE o se arma tarde, cerrar límite sin arranque repetido |
| 5 | Azahar con juego 3DS | MH4U .3ds recién hallado cumple base legible/hash; no Azahar instalado | Carga de base/parche correctos y diagnóstico nuevo; las CIA cifradas no sirven para este contraste; usar la nueva base .3ds si se justifica comparar versiones |
| 6 | Vita3K/Frontier | Requiere primero explicar capas locales, ejecutable utilizable, dependencias y condiciones online | Solo entonces ensayo de loader aislado; no equiparar pantalla inicial con juego funcional ni prometer servidor/offline |

Para cualquier ejecución futura: fijar fuente oficial, versión/commit y SHA256 del binario; perfil PC nuevo y ruta efectiva verificada; no montar originales en escritura, no usar partidas personales, no habilitar red por defecto y conservar recibo pre/post. No hace falta reinstalar una herramienta existente para repetir una prueba equivalente.

## Entrega a las áreas

02: diferencia entre CPU/HLE y fuente del juego; loader/segmentos antes de semántica. 03: ningún autoinforme aporta ventanas de ataques o hitboxes verificadas. 04: Frontier conserva revisión Z01.99 y dependencia online sin promesa ZZ. 05: CIA MH3U EUR bloqueada, sin evidencia acuática nueva. 07: la auditoría TEX debe separar RGB, alfa, orientación y uso real. 10: matriz diferencia fuente documental, ejecución, fidelidad y hardware; mantener contratos y hashes. Esta entrega actualiza necesidades documentales; no afirma nuevas respuestas de esos chats.

Fuentes y recibos de consulta: [catálogo trazable](emulator-sources.json). No se publican juegos, licencias de plataforma, claves, imágenes o vectores comerciales. Los metadatos y herramientas propias se entregan en PR7; PR3 y el banco compartido permanecen separados.

# Herramientas y protocolo de estudio

**Actualización posterior del 21-10-2026:** [herramientas y extracción local](extraction-tools.md). Los dos conjuntos 7z ya pasaron prueba íntegra y extracción; hay metadatos de sus CIA y listado RomFS del parche. Los párrafos iniciales que indican «sin prueba de carga» o «herramientas no disponibles» describen la primera etapa, superada donde lo precisa ese informe. MHXX es el nombre japonés relacionado con Generations Ultimate; se conserva por separado la plataforma 3DS observada en el CIA.


Estado: preparado, sin extracción de assets ni ejecución de juegos. Seleccionar herramientas por firma y versión real, no solo extensión. No se demuestra conversión nativa a Vita.

## Herramientas identificadas

| Entrada / objetivo | Herramienta candidata y fuente primaria | Capacidad documentada | Disponibilidad y límite local |
|---|---|---|---|
| Todas: identidad y referencia | [Herramienta propia](../../../tools/inventory_games.py), Python stdlib | Hash en streaming, cabeceras limitadas, TMD público, ISO/SFO, CRC de cabeceras 7z divididas | Ejecutada con Python del entorno; metadatos en inventory.json |
| MH4U y MHXX: listar/probar conjunto | [7-Zip](https://www.7-zip.org/7z.html) | Manejo de 7z; usar listado y prueba sobre `.001` con ambas partes presentes | No localizado en PATH ni instalación estándar comprobada. No instalado; carga comprimida no probada |
| MH3U, MH4U y MHXX 3DS: CIA/NCCH/ExeFS/RomFS | [CTRTool](https://github.com/3DSGuy/Project_CTR/blob/master/ctrtool/README.md) | Información, extracción y comprobaciones de formatos 3DS | No localizado en PATH. Comenzar por info; registrar versión y hash del ejecutable antes de usar |
| Alternativa 3DS: vistas de contenedores | [ninfs](https://github.com/ihaveamac/ninfs/blob/main/README.md) | Sistema virtual para CIA, NCCH, ExeFS y RomFS, entre otros | No localizado en PATH; dependencias FUSE/Windows pendientes. No montar en esta tarea |
| MHFU: ISO9660 y SFO | Sondeo propio de lectura; extractor ISO si se requiere después | Enumerar entradas sin copiar datos de juego | Ejecutado; futura extracción selectiva solo fuera del repo |
| MHFU: ejecutable PSP legible | [PRXTool](https://github.com/pspdev/prxtool/blob/master/README.md) | Analizar PRX, desensamblar, producir ELF/IDC | No localizado en PATH. `~PSP` por sí solo no confirma que PRXTool pueda leer el ejecutable actual |
| Ejecutables ya legibles | [Ghidra](https://github.com/NationalSecurityAgency/ghidra/wiki/Frequently-asked-questions) | Procesadores ARM y MIPS, entre otros | No localizado en PATH; instalación fuera de PATH no descartada. PSP requiere confirmar Allegrex/VFPU y loader; 3DS confirmar ARM/Thumb y segmentos |
| Archivos de recursos tras identificar firma | [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2), [RevilLib](https://github.com/PredatorCZ/RevilLib) | Toolkit de archivos de juegos; biblioteca/herramientas MT Framework y RE Engine respectivamente | Candidatos, no compatibilidad confirmada con estos juegos/versiones. No ejecutados ni instalación comprobada |
| Formatos gráficos 3DS compatibles | [Ohana3DS Rebirth](https://github.com/gdkchan/Ohana3DS-Rebirth) | Proyecto de visor/herramientas 3DS | Condicional a identificar un formato que soporte; no asumir soporte de recursos propietarios de Monster Hunter |

No se descargaron ejecutables de terceros, claves ni assets. La búsqueda local de herramientas fue acotada a PATH y ubicaciones indicadas, no un inventario completo de aplicaciones del PC. Python stdlib disponible; py7zr, pycdlib y Crypto no disponibles en el intérprete consultado. Fijar versión, procedencia y SHA-256 de cada herramienta antes de una etapa nueva; no recomendar una versión como probada sin ejecutarla.

## Orden del estudio

1. **Referencia de entrada:** conservar nombres y hashes actuales; cualquier derivado tendrá `source_sha256`, herramienta/versión/hash, parámetros, fecha y hash de salida. Rechazar modificación del original. Datos comerciales y claves siempre locales fuera del checkout.
2. **Contenedores divididos:** listar MH4U/MHXX y hacer prueba completa sin extraer. Registrar archivos internos, tamaños declarados y errores. CRC de cabeceras no sustituye esta prueba. Si faltan volúmenes o contraseña, registrar bloqueo sin adivinar contenido.
3. **Identidad 3DS:** leer metadatos CIA/NCCH accesibles, contrastar Title ID base/actualización/parche, región y versión. Mantener base y parche separados. No aplicar parche al original ni afirmar que el nombre v2 equivale a revisión del juego. Si el cifrado impide leer, documentar el requisito de una copia de análisis legible obtenida legítimamente; no buscar ni publicar claves.
4. **Ejecutables:** primero estructura, endian, plataforma, CPU/ABI, segmentos, entry point y compresión/envoltura. Solo después desensamblado estático de muestra local. Comparar código/datos y grado de confianza de funciones. No ejecutar binarios desconocidos ni generar un port por convertir un ejecutable.
5. **Recursos:** examinar firma e índice del contenedor, límites, compresión, alineación y relación entre entradas. Para DATA.BIN no hay extractor validado todavía. Probar herramienta con copia de trabajo o fragmento local mínimo y salida aislada; no subir fragmentos, modelos ni texturas.
6. **Ficha de modelo/rig:** índice, origen/hash, firma/versión, jerarquía, huesos, matriz de bind, skin weights, ejes, unidades, materiales y texturas. Registrar campos desconocidos, no inventar nombres de huesos.
7. **Ficha de animación:** origen, rig asociado, canales, compresión, duración y unidad temporal, frecuencia si existe, root motion, marcadores y bucle. Diferenciar lectura de metadatos de reproducción correcta; no inferir hitboxes/daño por animación.
8. **Texturas/audio/VFX/tablas:** formato, dimensiones/canales, compresión, paleta o codec, vínculos e índices; confirmar con parser y comparación estructural. El hecho de poder visualizar no prueba derecho a adaptar ni fidelidad.
9. **Validación independiente:** una muestra de ida solo para lectura; checks de conteos, límites y dependencias; anotar errores reproducibles. No adaptar recursos comerciales sin autorización válida documentada. Las pruebas funcionales futuras usarán recursos propios.

## Coordinación por interfaces

| Área | Entrada documental | Salida requerida |
|---|---|---|
| 02 — Arquitectura | Hashes, formatos, TMD/SFO, envolturas, contenido cifrado y accesibilidad | Clasificación CPU/loader y límites de análisis; no prometer adaptación Vita |
| 04 — Frontier | Ausencia de Frontier; distinción MHFU/Frontier; MHXX por nombre frente a MHGU | No elevar estas entradas a pruebas de Tierra/Cielo/Tormenta; mantener catálogo pendiente |
| 07 — Modelos y animaciones | Candidatos a contenedores y fichas de recursos | Identificar rig/formato antes de proponer reutilización; separar lectura, reproducción y adaptación |

Las tres áreas recibieron estos hallazgos con encargo exclusivamente documental. Su recepción/respuesta se registra en [coordinación](coordination.md), sin activar sus chats de Work ni tareas en consola.

## Publicación de resultados

Publicable: hashes, tamaños, nombres técnicos, tablas de formatos, herramientas, hipótesis, metodología, código propio y pruebas sintéticas. Excluido: juegos, partes de archivos comprimidos, ejecutables originales o derivados, proyectos de desensamblado con bytes comerciales, tickets, claves, volcados, imágenes, audio, rigs y animaciones. Revisar lista explícita de archivos antes de publicar; no añadir carpetas amplias del proyecto.

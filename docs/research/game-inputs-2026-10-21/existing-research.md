# Investigación existente: descifrado, extracción y decompilación

Búsqueda del 21-10-2026, a petición del usuario. Se revisaron resultados de GitHub, GameBanana, GBAtemp, Reddit y catálogos de proyectos. Las afirmaciones técnicas siguientes se apoyan en páginas de autores/proyectos; foros y catálogos se usan para descubrimiento, no para acreditar funcionamiento. No se descargaron imágenes de juegos, volcados, claves ni recursos de terceros.

## Qué significa «ya está hecho»

- **Descifrar:** obtener contenido legible de una copia; no reconstruye código fuente.
- **Descomprimir/extraer:** separar entradas de un contenedor; no demuestra que se entiendan sus modelos o animaciones.
- **Decompilar:** reconstruir código a partir del ejecutable, con distintos grados de correspondencia.
- **Recompilación estática:** traducir código máquina para otra plataforma; puede seguir dependiendo de servicios emulados y datos originales.

Un proyecto público de decompilación no equivale a ofrecer el juego completo descifrado ni a resolver la accesibilidad de nuestro CIA concreto.

## Hallazgos comprobados documentalmente

| Objetivo | Proyecto / fuente | Qué publica o declara | Aplicación y límite local |
|---|---|---|---|
| MHXX/MHGU | [Arc Explorer](https://github.com/Paxlord/pax_arc_explorer) | Herramienta de archivos ARC, con soporte anunciado de XX 3DS y GU Switch | Sirve para contenedores, no decompila el juego. El piloto local se hizo con lector propio contrastado con su estructura, no ejecutando Arc Explorer |
| MHGU | [Tutorial de extracción del autor](https://gamebanana.com/tuts/18644) | Flujo Kuriimu2/SaladSoftware y RevilLib para modelos; señala que no fue probado con MHXX | Referencia de recursos, sin garantía para nuestra variante 3DS. La revisión de compatibilidad es anterior a cualquier conversión |
| MH4U USA 1.3.0, 3DS | [MH4UltimateDC, README](https://github.com/CompaLarios18/MH4UltimateDC) | Recompilador estático y herramientas; declara código generado localmente desde una copia propia y backend basado en el core 3DS de Azahar | Proyecto público verificable por documentación; jugabilidad, rendimiento y exactitud son afirmaciones del autor, no pruebas nuestras. No incluye juego o claves. Nuestro inventario es EUR base y no coincide con el objetivo USA 1.3.0 |
| MH4U EU 1.1, 3DS | [mhvuze/mh4u-decomp](https://github.com/mhvuze/mh4u-decomp) | Declara seguimiento de matching mediante report.json; expresa que todavía no publica fuentes, herramientas ni datos de juego | Útil para conocer progreso/metadatos; no permite descargar una decompilación completa ni reemplaza nuestro ejecutable |
| Portable 2nd G, PSP | [tclamb/mhp2g-decomp](https://github.com/tclamb/mhp2g-decomp) | Proyecto de decompilación byte-matching | Relacionado con MHFU, pero objetivo de versión distinto. No se ha compilado ni contrastado con ULES01213/1.01; no se afirma decompilación completa |
| MH3U USA, Wii U | [glinesbdev/mh3u-port](https://github.com/glinesbdev/mh3u-port) | Se presenta como recompilación estática para Windows/Linux que requiere copia propia | Plataforma y arquitectura distintas del CIA 3DS local. No probado ni adoptado; no es prueba de un port Vita |
| Monster Hunter original, PS2 | [2Tie/mh1j](https://github.com/2Tie/mh1j) | Decompilación de la edición japonesa inicial | Otro juego y plataforma; no se inspeccionó código ni se incorporó al proyecto. No resuelve MHXX/MHGU |

No se halló, en estas consultas, una fuente primaria que demuestre una decompilación completa pública de MHXX/MHGU lista para utilizar con nuestros archivos. Es un resultado limitado de búsqueda, no una afirmación de inexistencia absoluta. No se adoptan porcentajes de catálogos como prueba de finalización.

## Resultado práctico para STT

El trabajo existente más cercano al bloqueo actual es el de **formatos/extractores**, no una descarga de juego ya preparado. Nuestro [piloto ARC](arc-pilot.md) comprobó descompresión de 782 entradas y exportación local de dos muestras; aún faltan geometría, rig y animaciones.

Para 02: estudiar interfaces y documentación de recompiladores sin extrapolar arquitecturas/regiones; exigir entrada compatible y resultados reproducibles antes de adoptar código o dependencias. Para 07: contrastar formatos concretos y licencias de herramientas; una firma MOD no garantiza importación correcta. Para 04: ninguna referencia de otro juego sustituye evidencia histórica de Frontier.

No se han clonado, instalado ni ejecutado estos proyectos de decompilación/recompilación. No se enviaron mensajes a sus autores ni se incorporó su código. El registro conserva enlaces y límites para una revisión posterior.

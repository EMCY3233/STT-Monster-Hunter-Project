# Banco local de archivos — 2026-10-21

Banco general, sin clasificación por armas ni búsqueda de relaciones con Espada Larga.

## Estado comprobado
- 1627 archivos físicos registrados: 7 originales, 3 contenedores derivados, 1609 archivos RomFS y 8 muestras previas.
- SHA-256 de contenido completo, tamaño, ruta de origen, formato observado y estado de lectura para cada archivo.
- 1228 ARC del parche MHXX 3DS: 21696 entradas descomprimidas, tamaño y SHA-256 verificados, sin errores.
- 8823 objetos únicos locales, 31612051 bytes. Las repeticiones conservan todos sus registros de procedencia y comparten objeto por hash.
- Los siete originales coinciden con sus hashes del inventario inicial.
- SQLite integrity_check: ok. Cinco pruebas sintéticas pasaron, incluyendo deduplicación con procedencia, conservación de fuentes, fallo de descompresión registrado, destinos inválidos y consulta por nombre sin interpretar comodines.
- Comprobada una consulta real contra el catálogo terminado.

## Ubicación y contenido
Desde la carpeta del proyecto: `analysis-local/resource-bank/`.
- `catalog.sqlite`: tablas files, entries y objects; índices por hash y ruta.
- `catalog-files.jsonl`: registro completo de los 1627 archivos.
- `catalog-entries.jsonl`: registro completo de las 21696 entradas ARC.
- `objects/HH/SHA256`: contenido descomprimido, sin reutilizar rutas internas como rutas de disco.
- `summary.json` y `verification.json`: alcance, conteos, cotejo de originales y hashes de catálogos.

Los archivos físicos existentes se referencian por su ubicación; no se duplican los juegos completos en el banco. Se almacenan los contenidos extraídos de ARC. Los originales y los derivados previos permanecen en sus carpetas.

## Consulta
Desde la raíz del checkout independiente:
```powershell
python tools/search_resource_bank.py --bank ../analysis-local/resource-bank nombre --limit 50
```
También admite SHA-256 completo. Abre SQLite en modo de solo lectura y devuelve rutas de origen, índices y objetos. Cada categoría limita el número de resultados según --limit; no es un conteo total de coincidencias.

## Repetición en un banco nuevo
```powershell
python tools/build_resource_bank.py --root originals=../Juegos --root containers=../analysis-local/containers --root romfs=../analysis-local/romfs --root samples=../analysis-local/samples --bank ../analysis-local/resource-bank-new
```
La carpeta de destino debe ser nueva, fuera de Git y de los orígenes. La herramienta nunca escribe en las fuentes. Los nombres internos solo son metadatos; los objetos usan SHA-256. Las versiones comerciales no se infieren de extensiones ni firmas: el inventario inicial conserva los metadatos de versión ya observados.

## Límites
«Todos» se refiere a los archivos físicos de las cuatro raíces indicadas y a las entradas de los ARC compatibles presentes allí. No implica haber abierto todos los formatos internos de todos los juegos. Las CIA base cifradas, el contenedor DATA.BIN de PSP y otros formatos quedan registrados como archivos, pendientes de análisis interno.

Descomprimir correctamente no valida semántica, reproducción, geometría ni autenticidad del juego. Las etiquetas de formato son firmas candidatas o extensión declarada, según el campo correspondiente. No se buscaron asociaciones con armas.

## Publicación
En GitHub se publican esta documentación, resumen, recibo de verificación y herramientas propias. El catálogo detallado y los contenidos comerciales permanecen locales. No se usó PS Vita ni FTP.

Esta etapa amplía el análisis anterior de 87 cargas seleccionadas: ahora se comprobaron las 21696 cargas ARC del parche. El alcance sigue limitado a ese parche para la extracción interna.

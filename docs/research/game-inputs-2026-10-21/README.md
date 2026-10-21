# STT — Banco de archivos y evidencias técnicas

Estado documental del **21 de octubre de 2026**. Este índice reúne los resultados actuales; los inventarios y recibos fechados conservan el alcance de cada etapa. Consulta [sincronización](synchronization.md) para responsables, ramas y dependencias.

## Estado actual comprobado

| Elemento | Resultado | Evidencia |
|---|---|---|
| Catálogo físico | 9.888 archivos con rutas, tamaños y SHA-256 registrados | [Banco y consulta](resource-bank.md) |
| Cargas ARC del parche MHXX 3DS | 21.696 entradas, 8.823 objetos únicos | [Cierre del banco inicial](resource-bank.md) |
| Copia Frontier Vita | 8.261 archivos, 5.212.490.427 bytes; transferencia y registro terminados | [Censo completo](frontier-complete.md) |
| Identidad Frontier | PCSG00350; base G 01.00 y parche Z 01.99 | [Metadatos y hashes](frontier-complete-summary.json) |
| Derivado Frontier enlazado | Dos salidas JKR de 349 y 1.884 bytes; el patrón parcial de la primera no aparece en la segunda. Gramática interior pendiente | [Procedencia](bank-derivatives.md) y [sondeo textual](frontier-jkr-text-regions.md) |
| Coherencia del catálogo | Sin errores de referencias/estados/tamaños en la auditoría; 161 grupos físicos de hashes repetidos conservados | [Auditoría y límites](bank-catalog-audit.md) |

El derivado se enlaza en `derivatives.jsonl`, separado de SQLite y de sus objetos ARC. No incrementa los conteos de esas tablas ni duplica sus bytes. Los tamaños y hashes no autentican una edición comercial ni demuestran jugabilidad.

El catálogo cubre las raíces que documenta su creación y los archivos de la copia Vita incorporada. Nuevos archivos de ensayo creados en otros directorios de `analysis-local` no quedan registrados automáticamente. No se presenta como inventario permanente de todo el disco.

## Abrir y consultar el banco

Ubicación desde la carpeta del proyecto: `analysis-local/resource-bank/`.

| Archivo local | Contenido |
|---|---|
| `catalog.sqlite` | Archivos físicos, entradas ARC y objetos |
| `catalog-files.jsonl` | Manifiesto físico completo del alcance registrado |
| `catalog-entries.jsonl` | Manifiesto de las entradas ARC |
| `derivatives.jsonl` | Referencias a salidas derivadas y sus recibos |
| `vita-registration.json` | Cierre de incorporación de la copia Vita |
| `README.md` | Guía local |

Desde la raíz de `inventory-work`:

```powershell
python tools/search_resource_bank.py --bank ../analysis-local/resource-bank PCSG00350 --limit 20
python tools/search_resource_bank.py --bank ../analysis-local/resource-bank 592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c
```

La búsqueda admite nombre/ruta o hash y devuelve `files`, `entries` y `derivatives`. El límite se aplica por categoría. Consultar metadatos no vuelve a comprobar todos los bytes ni garantiza que un archivo externo permanezca en su ubicación; conservar las salidas y recibos enlazados.

Los juegos, objetos extraídos y manifiestos detallados permanecen locales. GitHub conserva documentación, metadatos seleccionados y herramientas propias.

## Formatos y límites de acceso

| Conjunto | Lo comprobado | Lo pendiente |
|---|---|---|
| MH3U, MH4U y MHXX base 3DS | Identidad de contenedores y flags de cifrado; los dos conjuntos 7z pasaron prueba íntegra y extracción | Acceso interno y ejecución; no hay claves ni autenticidad comprobadas |
| Parche MHXX 3DS | RomFS extraído; 1.228 ARC inspeccionados y todas sus cargas descomprimidas; 83 cargas MOD y cuatro bibliotecas LMT localizadas | Geometría, pistas completas, rig, reproducción y FPS de esos recursos |
| Frontier Vita | Copia local completa en el alcance seleccionado; 44 cabeceras JKR, cinco ECD y una envoltura SCE contrastadas | Contenidos de ECD/SCE, mayoría de formatos y semántica; no se acredita ZZ |
| Una muestra JKR | Descompresión obtenida por investigación y fuente/salida/recibo cotejados al enlazar | Identificar el interior; no extender el éxito a los otros 43 JKR |
| MHFU PSP | Inventario inicial y estudios de ejecutable/DATA.BIN en el frente de investigación | Interpretación funcional y compatibilidad; consultar el informe de ese propietario |
| MHGU Switch | No incluido en el alcance actual de investigación | No equiparar sus formatos con los de MHXX 3DS |

[Herramientas y extracción](extraction-tools.md), [modelos y animaciones localizados](located-models-animations.md), [candidatos Frontier](frontier-container-candidates.json) y [resultados de investigación, PR #7](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/7) contienen los detalles y límites por versión.

No se atribuye un tipo de recurso por extensión o nombre. No se clasifica por armas ni se busca relación con Espada Larga.

## Interfaces con los prototipos originales

| Revisión | Evidencia | Pendiente explícito |
|---|---|---|
| STT/1–3 offline | [15 casos sintéticos](protocol-interop-review.md) | STT/3 requiere soporte explícito; emisor UDP Vita y recepción física pendientes |
| Asset Lab → Vita | [192 poses de la muestra propia](asset-bridge-review.md) | Ejes, avance, redondeo, política temporal e importador; sin GUI o hardware acreditados por este recorrido |
| Archivos compartidos de PR #8–#11 | [36 lecturas de blobs a commits fijos](prototype-overlap-review.md) | Consolidar changelogs y revisar integración; no se ha fusionado ni probado una combinación de ramas |

La muestra STT Asset/1 es original del proyecto. Las evaluaciones y propuestas de formato no equivalen a un importador, presupuesto de memoria aprobado ni adaptación de materiales comerciales.

## Evidencia de las etapas anteriores

- [Inventario inicial JSON](inventory.json) y [SHA-256 de los siete originales](SHA256SUMS.txt): referencia inicial, no manifiesto de los 9.888 archivos actuales.
- [Plan inicial de análisis](analysis-plan.md) y [coordinación inicial](coordination.md): planificación fechada; el estado vigente está en [sincronización](synchronization.md).
- [Piloto de tres ARC](arc-pilot.md): 782 entradas en esa etapa; fue ampliado al censo completo del parche.
- [Investigación pública](existing-research.md): fuentes y límites de lo que se pudo verificar; no prueba ausencia global de otros proyectos.
- Los estados antiguos del índice permanecen en el historial Git. No repetir la afirmación inicial de que Frontier no estaba disponible o de que los 7z no habían pasado prueba completa.

## Continuación autorizada

Analizar formatos y estructuras con límites y evidencia; registrar hipótesis y bloqueos; preservar contratos con áreas 02, 04 y 07. No repetir pruebas sin cambios ni duplicar FTP o registro del banco.

Esta tarea no instala ni ejecuta juegos, modifica originales, firmware, plugins, montajes o partidas, ni publica recursos comerciales, claves o licencias. La copia FTP de lectura expresamente autorizada ya terminó. No iniciar adaptación comercial sin activos legales ni fusionar PR automáticamente.

[Estado consolidado del proyecto](../../PROJECT_STATUS.md) · [Changelog](../../../CHANGELOG_MASTER.md).

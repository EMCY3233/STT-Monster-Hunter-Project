# Frontier Vita: cierre de copia y censo completo — 21-10-2026

## Resultado comprobado
La transferencia y el registro terminaron correctamente: **8261 archivos,5212490427bytes**. El banco contiene ahora **9888 archivos físicos**. Se mantienen21696 entradas ARC y8823 objetos únicos del parche MHXX; las cargas internas de Frontier no se han añadido como objetos descifrados.

Fuentes de cierre locales: vita-copy-PCSG00350.json con completed=true, vita-bank-status.json con phase=complete y resource-bank/vita-registration.json. Ambos procesos terminaron con código0. No quedan archivos.partial. Se cotejaron los hashes actuales de SQLite y ambos manifiestos con el recibo de registro; integridad SQLite:ok.

## Identidad leída de los archivos terminados
| Capa | Archivos locales | Identidad SFO | APP_VER | VERSION |
|---|---:|---|---|---|
|app |4492 |Monster Hunter Frontier G;PCSG00350 |01.00 |01.00 |
|patch |3666 |Monster Hunter Frontier Z;PCSG00350 |01.99 |01.00 |
|rePatch |103 |Sin SFO en este conjunto |No inferida |No inferida |

Los8262archivos inicialmente enumerados incluían una licencia work.bin que no se copió. addcont respondió550 y no forma parte de la copia. No se extrajeron partidas ni aplicaciones ajenas. Estos metadatos confirman el título y versión del parche, no ZZ ni una instalación reproducible o descifrada.

## Censo posterior completo
Se reutilizó, sin modificarlo, tools/stt_re/inspect_frontier_local.py del frente de investigación. SHA-256 del código:d18e3fca5741b700faf58faabd21fcb36dde99c0c08c882d47467ffd014eee6e.
Resultado independiente:8252archivos leídos íntegramente, todos con tamaño/hash coincidentes con el banco; nueve archivos de metadatos sce_sys/package omitidos por la política de esa herramienta. Esos nueve ya conservan verificación de descarga y registro; no se cuentan como releídos por este censo. Sin cambios de conjunto de archivos, errores ni lecturas inestables.

Firmas candidatas:44JKR,5ECD,1envoltura SCE,2SFO,2PNG y2HTML. Otros8196archivos no clasificados por el sondeo. Extensiones observadas incluyen1634.pac,125.abn,105.mot,263.txb,2035.bin,766.mus,2643.vsnd y288.vsnp: los nombres no confirman formatos ni cantidades de animaciones, modelos o sonidos decodificados.

Los eboot de app y patch siguen sin firma reconocida por este lector; rePatch/eboot.bin presenta envoltura SCE. Ninguno se declara ELF descifrado ni se ejecuta.

## Correspondencias entre capas
Sobre los8252archivos leídos:7591rutas lógicas,597presentes en varias capas. De esas,56conservan el mismo hash y541difieren. Se registra correspondencia, sin construir una instalación fusionada ni asumir precedencia en ejecución. No se modificaron ni renombraron recursos.

## Evidencia y próximos pasos
- [Resumen de censo, SFO y cotejos](frontier-complete-summary.json).
- [Candidatos y ejecutables por ruta/hash](frontier-container-candidates.json),50registros:49candidatos de contenedor y1envoltura ejecutable SCE.
- Inventario completo local:analysis-local/frontier-complete-census-20261021/inventory.json; SHA-256:f9064d4b92397d495bc1af5810f34c2e5d5bf60c143a9aa97a4da5f56bbe2c15.
- Banco:analysis-local/resource-bank. Sus catálogos detallados y bytes comerciales siguen locales.

El frente de investigación recibió el cierre y los candidatos para su siguiente análisis estructural en PR7. Este chat mantiene inventario, procedencia y documentación en PR3. No duplicar decodificadores ni pruebas ya realizadas. Referencias documentales:[ReFrontier](https://github.com/Houmgaor/ReFrontier),[importador Frontier](https://github.com/Houmgaor/MHFrontier-blender-addon); consultarlas no demuestra compatibilidad de esos flujos con la copia Vita.

Próxima aceptación:estructura acotada de candidatos y relación de entradas/rangos, con evidencia reproducible, antes de afirmar descompresión, descifrado o compatibilidad. Sin clasificar por armas, adaptar recursos comerciales, publicar contenidos ni modificar consola. La continuación automática conserva estos límites.

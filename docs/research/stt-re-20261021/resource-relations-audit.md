# Auditoría de integridad del índice de relaciones MH4U

Auditoría agregada del banco local cerrado, 22-10-2026. No repite extracción, conversión, lectura de recursos ni hashes de objetos. Solo lee tablas SQLite y el propio archivo de índice. No utiliza consola, FTP, emulador ni instrumentación del juego. No reabre los bloqueos de rig o BLZ.

## Resultado

El índice contiene 113.280 apariciones de recursos y 59.553 identidades de contenido, con 64.420 referencias candidatas. `PRAGMA integrity_check` devuelve `ok`; los IDs de recursos son enteros no negativos y únicos, los hashes tienen forma SHA-256 válida y todas las apariciones apuntan a una identidad de contenido existente. Esto comprueba el índice, no vuelve a validar los bytes de los recursos.

| Comprobación | Resultado |
|---|---:|
| Orígenes de enlace sin identidad o aparición de recurso | 0 |
| Destinos sin ruta exacta o normalizada existente | 0 |
| Grupos de enlaces duplicados, antes/después de normalizar | 0 |
| Contadores de aparición o indicadores semánticos inválidos | 0 |
| Referencias cuyo destino exacto tiene varios contenidos | 3.670 |
| Rutas de destino ambiguas distintas referidas | 1.730 |
| Referencias candidatas al mismo contenido de origen | 1.607 |
| Relaciones semánticas confirmadas independientemente aquí | 0 |

Las 64.420 referencias utilizan la categoría `exact_normalized_ascii_path`. Todas conservan `semantic_verified=0`. Hay 18.084 contenidos de origen y 33.382 rutas de destino distintas entre ellas. Una referencia al mismo contenido no se elimina automáticamente: podría ser una referencia interna válida o una coincidencia de nombre; esta auditoría no decide su significado.

En el índice global hay 56.081 rutas distintas. De ellas, 23.716 tienen más de una aparición y 11.871 corresponden a más de un contenido. Repetición y ambigüedad son comprobaciones diferentes: repetir una ruta con un mismo hash no crea por sí solo ambigüedad de contenido. En esta muestra no hay grupos adicionales de alias por normalización de separador y mayúsculas/minúsculas.

## Implicación para la consulta

No seleccionar el primer resultado de una ruta como dependencia certificada. Para las 3.670 referencias ambiguas hace falta conservar la lista de candidatos y resolver el contexto de archivo contenedor, variante regional, versión o escena mediante evidencia adicional. Compartir archivo contenedor puede orientar la investigación, pero no demuestra por sí solo el vínculo.

La tabla de tipos contiene 21 asociaciones candidatas nombre/CRC. Las 21 cumplen la fórmula usada por el catálogo: `(crc32(nombre_utf8) ^ 0xffffffff) & 0x7fffffff`. Esto prueba consistencia aritmética de esa tabla; no prueba interpretación semántica ni compatibilidad de un parser. Los enlaces de recursos de esta muestra son coincidencias de ruta, no enlaces demostrados mediante CRC.

La base no declara claves foráneas. Por ello, el resultado vacío de `foreign_key_check` no basta para certificar sus relaciones: las comprobaciones explícitas de pertenencia entre tablas son necesarias y se incluyen en el auditor.

## Método reproducible y conservación

Código propio: `tools/stt_re/audit_resource_relations.py`. Abre SQLite con `mode=ro`, activa `query_only`, usa una transacción de lectura y rechaza índices con WAL/journal no vacío. Comprueba el esquema requerido, identidades, pertenencia entre tablas, rutas exactas y normalizadas, conjuntos de contenidos, duplicados, contadores, indicadores y CRC. Emite exclusivamente cifras agregadas: no rutas internas, nombres de recursos ni hashes individuales de contenido.

```text
python tools/stt_re/audit_resource_relations.py --database RUTA_PRIVADA/resources.sqlite --out INFORME_FUERA_DEL_BANCO.json
python tests/test_stt_re_resource_relations.py
```

La salida debe ser nueva y estar fuera de la carpeta del banco histórico. No hay correcciones ni borrados automáticos. El auditor no abre ni recorre archivos de recursos. Esta auditoría no demuestra que todas las referencias del juego estén presentes, no inspecciona ciclos funcionales y no confirma que una textura, modelo, animación o efecto se use durante el juego.

El índice mantuvo SHA-256 antes/después `7abc060d796c70ea591351171646375ae23fa2896bce8915be50b7d995802ad0`. Los recuentos y ambos hashes están en [resource-relations-audit-evidence.json](resource-relations-audit-evidence.json). No se modificó el banco.

Pasaron cinco pruebas sintéticas: repetición sin ambigüedad de contenido; orígenes/destinos ausentes y contadores inválidos; alias normalizados y duplicados; separación entre indicador semántico almacenado y confirmación independiente, junto con CRC discrepante; y apertura de solo lectura con bytes de índice intactos. Las pruebas no usan recursos comerciales.

La publicación incluye únicamente este resumen, evidencia agregada, código propio y pruebas sintéticas. No incluye la base, catálogos completos ni recursos comerciales.

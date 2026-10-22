# MHXX 3DS: evidencia de enlaces MOD–MRL–TEX

22 de octubre de 2026. Trabajo independiente de la sesión de Citra/MH4U.

Se creó un analizador de metadatos de solo lectura. Verifica SHA-256 y tamaño de cada MOD/MRL/TEX utilizado contra el manifiesto de extracción antes de analizarlo. No ejecuta contenido del juego ni usa las rutas internas como destinos. Los recursos y el catálogo detallado permanecen locales.

## Resultado reproducido

En `common.arc` (SHA-256 `8694d2381e6c2e4b892831ca36c744d0ba6da9d5b2ce18e6376263659d9910c1`):

- 51 MOD230 y 51 MRL versión 32 comprobados contra manifiesto.
- 99 nombres de material leídos de campos MOD de 128 bytes.
- Los 99 valores `~CRC32(nombre) & 0xffffffff` aparecen como palabras alineadas en el MRL de la misma ruta de archivo. Ningún MOD quedó fuera de soporte en este lote.
- 91 cadenas terminadas en NUL con rutas de texturas en MRL; las 91 tienen coincidencia textual exacta con entradas TEX del mismo ARC.
- Seis pruebas sintéticas pasaron: CRC conocido, tabla truncada, nombre sin terminador, referencia exacta frente a prefijo, referencia sin terminador y versión incompatible.

Caso pequeño: MOD entrada 377, nombre de material `XfBAW_1__m00_` en offset 160. Su CRC complementado `813e69ea` aparece en MRL 376, offset 260. El MRL contiene en offset 40 la ruta exacta de TEX 375. La geometría y la textura ya tenían conversores locales previos; este trabajo agrega evidencia para relacionarlas.

## Grado de verificación

Hechos: tamaños/hashes de las entradas, bytes de nombres y rutas, coincidencias CRC y coincidencias exactas de rutas. La hipótesis de identificación de material por CRC está respaldada por 99/99 observaciones, pero falta un lector estructural de registros MRL: una búsqueda de palabra no demuestra su función por sí sola. Una colisión CRC sigue siendo posible.

La lista de texturas de un MRL NO demuestra qué textura corresponde a cada material en MRL con varios materiales. No se generó un OBJ+MTL que invente dicha asignación. Los parámetros del shader, blending, animación UV, orientación en juego y slots siguen sin verificar. Tampoco se convirtió esqueleto ni animación en esta intervención.

## Reproducción local

Desde la raíz del proyecto, con Python 3.11 o posterior:

```powershell
python analysis-local/resource-fork-01a16188/link_materials.py analysis-local/arc-extractor-acceptance-20261022/common analysis-local/resource-fork-01a16188/common-links-new.json
python -m unittest discover -s analysis-local/resource-fork-01a16188 -p test_link_materials.py -v
```

El destino JSON debe no existir. El catálogo detallado está en `common-links.json`. No se publican recursos comerciales ni bytes derivados de geometría/texturas.

## Prioridad y bloqueo siguiente

1. Parsear tablas/offsets de MRL versión 32 y validar contra todos los 51 casos; conservar los enlaces por material, no por archivo completo.
2. Resolver slot de textura y transformaciones UV. Solo entonces producir MTL con asignaciones verificadas, con vista previa comparada en juego por la sesión principal.
3. Ampliar a modelos con esqueleto y LMT después de validar jerarquía, pesos y coordenadas por separado.

No es necesario intervenir en Citra para estas etapas estáticas. Se preservaron los originales, las salidas anteriores, el banco de recursos y `research-work`/PR #7. PR #7 estaba abierta en `49ad4e7f14b64bbe8f4b7101e491d3a21210ab78` al comprobarla.

## Referencias consultadas

[RevilLib material.hpp, commit fijado](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/material.hpp): declara nombres de material MOD de 128 bytes. No valida el formato MRL de este juego ni la relación CRC; esta se obtuvo de muestras locales. No se copió código de RevilLib.

[mhff importador, commit fijado](https://github.com/svanheulen/mhff/blob/6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf/n3ds/io_import_scene_mod.py): `load_mrl` está sin implementar. No constituye una referencia de conversión de materiales.

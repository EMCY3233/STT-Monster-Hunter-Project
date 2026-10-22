# MHXX: una muestra MOD230, límites y malla parcial

Fecha: 2026-10-21. Se revisó primero la evidencia anterior: solo comprobaba la cabecera común de 24 bytes en 83 candidatos MOD230; no cubría tablas, atributos ni índices. Este ensayo trata una sola muestra, sin visualización, exportación de geometría o adaptación comercial.

## Selección y procedencia comprobada

Menor tamaño entre los MOD230 del manifiesto previo, desempate SHA-256: **990 bytes**, hash `ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0`. Fuente: `MHXX-patch/arc/village/common.arc`, entrada **377** (índice desde cero), type ID `58A15856`; ruta interna `effect\base\cm080_000` registrada únicamente para procedencia, sin inferir función.

Objeto existente: `analysis-local/resource-bank/objects/ec/ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0`. Se consultó SQLite en modo lectura, cotejó tamaño/hash y creó una copia nueva `analysis-local/mod230-smallest-20261021/source.mod`. No se cambió banco ni registro de derivados.

Contraste adicional acotado: se decodificó **solo esa entrada** con el lector ARC ya existente. Su tabla declara 990 bytes; carga zlib de 274 bytes, offset 2.196.177. Tamaño, terminación zlib y ausencia de sobrantes correctos; salida idéntica byte a byte al objeto y copia. SHA-256 del ARC: `8694d2381e6c2e4b892831ca36c744d0ba6da9d5b2ce18e6376263659d9910c1`. La discrepancia interna descrita abajo no nace de nuestra copia o extracción individual.

## Límites observados

La referencia RevilLib relaciona versión 230 (0xE6) con LoadMODXE5. Con esa disposición LE32:

| Región | Offset | Bytes | Estado |
|---|---:|---:|---|
| Cabecera ampliada | 0 | 64 | en archivo |
| Grupo, una entrada | 128 | 32 | en archivo |
| Material, una entrada | 160 | 128 | en archivo, sin interpretar nombre/material |
| Malla, una entrada | 288 | 48 | en archivo |
| Buffer de vértices | 484 | 448 | en archivo |
| Índices globales declarados, 30 u16 | 932 | 60 | acabaría en 992: excede dos bytes |
| Índices utilizados por la malla, 28 u16 | 932 | 56 | acaba en 988: en archivo |

Las regiones comprobadas, excluyendo el rango global inválido, no se solapan. Quedan huecos/bloques sin interpretar. Desde el puntero de índices hasta EOF caben **29 u16**, frente a 30 declarados globalmente y 28 usados por la malla. No se añade relleno ni se inventa un índice. No se atribuye corrupción: puede haber una particularidad del formato/variante o un dato inconsistente aún sin explicar.

## Atributos e índices accesibles

Formato `0x59DC400B`, stride **28**, presente en la tabla pública de atributos. Layout referenciado: posición f32x3 en +0; normal snorm8x4 en +12; UV f32x2 en +16; tangente snorm8x4 en +24. **16 × 28 = 448 bytes**, sin sobrepasar el buffer. Se leyeron 16 posiciones y 16 pares UV: todos finitos. Se comprueban tamaño/ubicación de normal y tangente; no se verificaron longitudes unitarias, orientación o shader.

Material/grupo de la malla apuntan a entradas existentes. Sus 28 índices caben en archivo, no incluyen 0xFFFF y todos quedan entre 0 y 15 después del ajuste vertexStart=0. El código de primitiva 4 corresponde a triangle strip en la referencia: 26 ternas consecutivas, seis con tres índices distintos y veinte con repetición. No se afirma área no nula, orientación correcta ni fidelidad visual.

Los campos denominados minVertex/maxVertex en la referencia valen 0/0, mientras el rango observado es 0–15. Es otra diferencia que queda registrada; no se usa para corregir índices. Cabecera: cero huesos y cero skins; campo de número de pesos cero; el layout consultado no contiene índices/pesos óseos. Esta muestra **no permite validar skinning ni jerarquía**, ni concluir que otras muestras carezcan de ellos.

## Fuentes, método y aceptación

RevilLib, commit `e17f9718ea571f040a7e1f331c28a4d45a6066b5`, consultado como referencia de campos; no se compiló ni ejecutó:

- [header.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/header.hpp): MODHeaderCommon/XE5, campos y punteros.
- [serialize.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/serialize.cpp), blob `b599dc118442471c6e2cc00c161dadd0e61cb432`: selección XE6→XE5 y lectura global de índices.
- [mesh.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/mesh.hpp), blob `4d1e0bfa734d182be437c87980d858c1d943e39b`: registro y bitfields.
- [common.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/common.cpp), blob `5435277ef757c0f6c7bdeae7efd0837fe44df8f1`: tabla del formato y cálculo de spans.
- [traits.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/traits.hpp), blob `61f901ad82bd674592682aaed26ab2d4e59eeb3d`: tipos de malla/material.

Lector propio: `tools/stt_re/inspect_mod230_mesh.py --input <copia> --expected-sha256 ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0 --out <JSON nuevo>`. Presupuesto 1 MiB; checks de firma, versión, conteos, intervalos y solapamiento; no devuelve arrays de vértices/índices ni texto comercial. Registra discrepancias globales sin leer fuera de archivo.

[Evidencia pública](mod230-smallest-evidence.json) combina procedencia, cotejo ARC, checks estructurales y hashes de los recibos privados. Ocho pruebas sintéticas nuevas aprobadas: rangos válidos, desfase global, índice inválido, NaN, stride, tablas fuera de archivo/solapadas y firma. No se repitieron censo, otras muestras o batería completa.

Aceptación parcial: cabecera extendida, tablas indicadas, span de vértices y rango de índices de una malla comprobados; layout referenciado y finitud de posición/UV comprobadas. **Geometría completa no validada.** Próximo bloqueo: explicar la cuenta global de índices y min/max en esta misma muestra frente a un lector específico de MOD230/MHXX; después verificar área/winding y transformaciones. No ampliar a otros modelos para ocultar esa discrepancia ni abrir más JKR.

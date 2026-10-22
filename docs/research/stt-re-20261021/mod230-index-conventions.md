# MOD230: discrepancia delimitada mediante lectores primarios

Fecha: 2026-10-21. Continúa [la misma muestra de 990 bytes](mod230-smallest.md); no cambia ninguna fuente, copia, índice o cabecera. SHA-256 `ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0`. Sin nuevos modelos, JKR, visualización, utilidades externas ejecutadas o relleno de bytes.

## Contraste documental aplicable

[mhff/n3ds/io_import_scene_mod.py](https://github.com/svanheulen/mhff/blob/6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf/n3ds/io_import_scene_mod.py), commit `6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf`, blob `0da950c275caf78bfcfa310f6a45c488e890d94b`, se presenta como importador **MH4U** y comprueba explícitamente versión **0xE6**. No declara por sí solo compatibilidad MHXX. Se leyó el código; no se importó bpy, instaló Blender o ejecutó ese importador.

Su cabecera es de 64 bytes; sus registros de malla tienen 48. Usa el mismo puntero de índices y los mismos campos de inicio/cantidad de esta muestra, pero solicita `mesh_info[10] * 2 + 2` bytes. Lee, por tanto, **un u16 adicional por malla** respecto a la cantidad de su registro. No lee el buffer completo mediante el contador global y no explica en comentarios el significado de ese contador o de la unidad adicional.

RevilLib, commit `e17f9718ea571f040a7e1f331c28a4d45a6066b5`, [serialize.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/serialize.cpp), blob `b599dc118442471c6e2cc00c161dadd0e61cb432`, pide tantos u16 como `header.numIndices`. [common.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/common.cpp), blob `5435277ef757c0f6c7bdeae7efd0837fe44df8f1`, crea el span de cada malla con su cantidad propia, sin sumar un índice.

## Comprobación acotada en la copia existente

| Convención | Cantidad u16 | Bytes desde offset 932 | Final | Resultado |
|---|---:|---:|---:|---|
| Contador global, RevilLib | 30 | 60 | 992 | excede EOF por 2 bytes |
| Cantidad de malla, RevilLib | 28 | 56 | 988 | cabe; quedan 2 bytes |
| Cantidad de malla +2 bytes, mhff/MH4U | 29 | 58 | 990 | coincide exactamente con EOF |

Se leyeron únicamente los dos bytes existentes adicionales, amparados por esa convención primaria, y se compararon ambas ventanas. Todos los índices de ambas quedan en 0–15, sin 0xFFFF. La ventana de 28 produce 26 ternas consecutivas, seis con índices distintos; la de 29 produce 27, **también seis con índices distintos**. El índice adicional solo añade una terna con repetición. No se comprueban área geométrica, orientación, transformaciones o función de esa terna.

Esto explica cómo el lector MH4U podría consumir la cola física de esta malla sin desbordar ni inventar bytes. **No explica todavía por qué el contador global vale 30**; no se cambia a 29 ni se declara demostrado un padding virtual, centinela omitido o corrupción.

## Min/max: semántica no confirmada

En [mesh.hpp de RevilLib](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/mesh.hpp), blob `4d1e0bfa734d182be437c87980d858c1d943e39b`, los bytes relativos 40 y 42 reciben nombres `minVertex` y `maxVertex`; ambos son cero en la muestra. En el lector mhff, esos cuatro bytes se leen como **un u32** (`mesh_info[13]`) que no se utiliza al construir caras. El contraste no acredita que los nombres genéricos sean semántica obligatoria en MHXX. La observación 0/0 frente al rango efectivo 0–15 queda como **diferencia de interpretación**, no como validación de que el archivo tenga límites corruptos.

Como contraste secundario se leyó [MH3U MOD.bt de Silvris](https://github.com/Silvris/MH-Tools-and-Scripts/blob/18a51a92cb028f3c0d16134fbfb4a37276f61f5c/MH3U%20MOD.bt), commit `18a51a92cb028f3c0d16134fbfb4a37276f61f5c`, blob `bcb9894041d2976b85401100c2d213e05a05f28b`. Nombra el campo global `vertexIds` y deja campos finales de malla como desconocidos, pero **no se adopta como esquema validado**: toma `version2` en +4 y `version` en +5, y condiciona la malla a `version==230`; en nuestra cabecera LE los bytes son 230/0 y esa condición no se cumpliría. El nombre MH3U o un campo parecido no establece aplicabilidad a este MOD230/MHXX. No se ejecutó la plantilla ni se cambió su interpretación automáticamente.

## Reproducción y cierre de la aceptación

Lector propio de contraste: `compare_mod230_index_conventions.py --input <copia existente> --expected-sha256 ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0 --out <JSON nuevo>`. Solo una malla LE230, límite 1 MiB, ventanas comprobadas antes de leer y hash de origen conservado. [Recibo público](mod230-index-conventions-evidence.json); original privado `analysis-local/mod230-smallest-20261021/index-conventions.json`. Cuatro pruebas sintéticas aprobadas: comparación sin relleno, límites de cabecera, rechazo de otro alcance y versión.

**Aceptación cerrada como delimitación, no resolución total.** Hay una convención primaria MH4U/E6 de lectura por malla que encaja exactamente y una semántica genérica min/max cuya aplicabilidad MHXX no está probada. Falta una fuente específica MHXX que establezca el contador global 30 y el significado de la cola. Geometría completa sigue sin validar. No se amplían modelos ni se repiten ensayos ya aceptados para ocultar ese bloqueo.

# MOD230: una jerarquía con tres huesos

**Nota editorial de consolidación (22-10-2026):** La propiedad numérica posterior A29no confirmó el modelo de matrices. Rangos, jerarquía y finitud anteriores permanecen; no existe rig funcional aceptado. Véase [el índice de aceptaciones](acceptance-index.md).

2026-10-22, Área07. Aceptación distinta del MOD de990bytes: solo cabecera y tablas del esqueleto de **una** muestra ya catalogada con bone_count>0. No se busca otra geometría para ocultar la discrepancia anterior, ni se asocia LMT por nombres.

## Selección reproducible

Manifiesto anterior `resource-headers.json`, SHA256 `0b98e274b925a2db76e6148e7652e9e4dafd82a86fb050a10c11dfe7227e09da`:83MOD230,3con huesos y3objetos existentes. Orden `(bytes, SHA256)`; para ocurrencias duplicadas, desempate contenedor/índice. Se usa metadata ya catalogada y solo se abre el objeto elegido.

Seleccionado: **26.402bytes**, SHA256 **`6d98d22019ceafc1c44801ed45692610ed5c0b2db461dc1fb813526c7af374be`**. `MHXX-patch/arc/village/common.arc`, entrada466desde0, ruta interna `effect\base\cm400_000`, registrada únicamente como procedencia. Objeto `analysis-local/resource-bank/objects/6d/6d98d22019ceafc1c44801ed45692610ed5c0b2db461dc1fb813526c7af374be`.

No se extrae de nuevo el ARC, copia el binario, cambia SQLite o registra un derivado en el banco. Se escriben solo selección/recibo/aceptación privados. SHA256 del objeto antes/después idéntico. Dos pasadas de hash leen todo el objeto; el **parseo estructural se limita a804bytes**, incluyendo cabecera64y tablas740. Los bytes de geometría atravesados por el hash no se interpretan.

## Layout y fuentes primarias

**RevilLib `e17f9718ea571f040a7e1f331c28a4d45a6066b5`**, referencia documental GPLv3-o-posterior, no compilada/ejecutada:

- [header.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/header.hpp), blob `1c4b820fad1afbb58498eea989faf96d8ae91c15`: cabecera XE5 de64bytes y punteros LE32.
- [serialize.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/serialize.cpp), blob `b599dc118442471c6e2cc00c161dadd0e61cb432`: XE6/230 se dirige a LoadMODXE5; lee bones, refPoses, transforms,256remaps y skinRemaps consecutivos. Reflect convierte parentIndex0xFF a raíz0xFFFF.
- [traits.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/traits.hpp), blob `61f901ad82bd674592682aaed26ab2d4e59eeb3d`: MODBoneV1_5,256remaps y24entradas por skin map.
- [bones.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/bones.hpp), blob `742e88d2f7eaaa31a9ccdcf3581d86d948ca8fb3`: index/parent/mirror u8, alineación antes de floats y tres componentes de posición.
- [common.hpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/common.hpp), blob `94b23b325ceaa6ea52f8be7d9bb79a06a4330848`: vectores de Matrix44 y skin map count-u32+24u8.
- [mod_to_gltf.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/toolset/mod_to_gltf/mod_to_gltf.cpp), blob `028e077b99021c53e6f40e5484083c04a93dd914`, ProcessSkeletons: enlaza `nodes[b.parentIndex]`; usa posición del registro para la jerarquía, no una búsqueda por el campo index. Se consulta esa regla, **no se ejecuta ni exporta glTF**.

Submódulo **Spike `e83f3855e0a96b29eee3dcec98f428c1787ffad4`**, fijado por el árbol de RevilLib. [vectors_fwd.hpp](https://github.com/PredatorCZ/Spike/blob/e83f3855e0a96b29eee3dcec98f428c1787ffad4/include/spike/type/vectors_fwd.hpp), blob `7c09ca0df9c1bfc8f76dc9f32a7b908c06a50af0`, y [vectors.hpp](https://github.com/PredatorCZ/Spike/blob/e83f3855e0a96b29eee3dcec98f428c1787ffad4/include/spike/type/vectors.hpp), blob `0ba400c5df939e933141992e072a2bdf78b14544`: Vector=t_Vector<float>, tres floats. [matrix44.hpp](https://github.com/PredatorCZ/Spike/blob/e83f3855e0a96b29eee3dcec98f428c1787ffad4/include/spike/type/matrix44.hpp), blob `c371667c8ac07a3d1137fcedeb381175b9da6d18`, y [vectors_simd.hpp](https://github.com/PredatorCZ/Spike/blob/e83f3855e0a96b29eee3dcec98f428c1787ffad4/include/spike/type/vectors_simd.hpp), blob `7a0585cb17ac7c8a831584c81c729bfb0f3182fa`: cuatro vectores de cuatro floats por Matrix44. [binreader_ref.hpp](https://github.com/PredatorCZ/Spike/blob/e83f3855e0a96b29eee3dcec98f428c1787ffad4/include/spike/io/binreader_ref.hpp), blob `f3bfb100c1be8b5377fdd025dd4d9ea3439331bf`: contenedores ordinarios leídos mediante sizeof(T), sin padding adicional entre arrays. Fuentes Apache2.0, consultadas como layout.

Derivación aplicada: registro de hueso24bytes, con floats en+4; matriz64bytes. El ajuste exacto de todos los bloques a la frontera siguiente respalda aplicabilidad estructural en esta muestra. No se presenta como validación independiente de SDK/hardware o semántica completa de transformaciones.

## Rangos comprobados

| Región | Offset | Bytes | Fin |
|---|---:|---:|---:|
| Cabecera |0|64|64|
|3huesos ×24|128|72|200|
|3refPoses ×64|200|192|392|
|3transforms ×64|392|192|584|
|remaps|584|256|840|
|1skin map ×28|840|28|868|

Todas en archivo y sin solapamiento; fin868coincide con el puntero al siguiente bloque de grupos. El hueco64–128no se interpreta. El skin map declara count2≤24: se valida capacidad, **no sus índices, pesos o semántica**. Materiales, mallas, vértices e índices no se parsean.

## Resultado de jerarquía y finitud

**3huesos,2raíces** en slots0y1; un enlace no raíz, padre en rango y profundidad máxima1. Sin autorreferencias ni ciclos. La raíz se reconoce por parentIndex0xFF según Reflect. El grafo se comprueba por slots, respaldado por ProcessSkeletons.

El campo denominado index en la referencia contiene2valores únicos para3registros: un duplicado y no coincide con los slots. No se corrige ni exige unicidad para resolver padres; el conversor distingue índice de registro e index al nombrar nodos. Esta observación se conserva como límite de semántica de IDs, sin reinterpretar bytes para forzar un rig.

Los3registros contienen solo floats finitos en los cinco campos leídos por registro. **Seis matrices,96floats, todos finitos**:3refPoses y3transforms. No se publican matrices, posiciones u otros valores comerciales; solo conteos, rangos, hashes y estado de comprobaciones. No se verifican inversas, unidades, ejes, escalas, orientación o efecto de aplicar esas matrices.

## Pruebas y aceptación

Herramienta propia `inspect_mod230_skeleton.py --input <objeto existente> --expected-sha256 6d98d22019ceafc1c44801ed45692610ed5c0b2db461dc1fb813526c7af374be --out <JSON nuevo>`. Fuente≤1MiB, parseo≤64KiB, huesos1..255, skins≤256; no sobrescribe salida. No importa código RevilLib/Spike.

**10pruebas sintéticas nuevas aprobadas**: bosque con dos raíces e IDs duplicados, padre fuera de rango, ciclo mutuo, ciclo propio, NaN de matriz, infinito de hueso, tablas truncadas, solapamiento, rechazo de cero huesos y count de skin map fuera de capacidad. Ayuda CLI comprobada. No se repiten campañas anteriores ni se suman como si se hubiera ejecutado una suite nueva completa.

[Recibo público](mod230-skeleton-evidence.json); selección/recibo originales privados en `analysis-local/mod230-skeleton-20261022/`. **Aceptado:** layout/rangos de estas tablas, jerarquía por slots y finitud. **No aceptado:** rig funcional, skinning, geometría, asociación LMT, render o adaptación comercial.

La [muestra anterior de990bytes](mod230-smallest.md) y su [discrepancia de índices](mod230-index-conventions.md) **siguen abiertas e intactas**. Este resultado no las resuelve. Los bloqueos de independencia BLZ/LMT tampoco se reabren.

Próximo criterio: sobre esta misma muestra, acreditar convención/relación de las dos familias de matrices mediante fuente compatible y una comprobación numérica acotada (sin publicarlas), antes de afirmar transformaciones funcionales. Una asociación a animación requeriría evidencia explícita de correspondencia de joints; los nombres no bastan. No ampliar a otras muestras para eludir esa condición.

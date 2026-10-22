# Una pista LMT67: segunda referencia y bloqueo de independencia

Fecha: 2026-10-21. Se consultaron [lmt-vectors.md](lmt-vectors.md) y los recibos ya existentes antes de actuar. Se reutilizan sus cuatro informes derivados **para seleccionar**, no se vuelven a decodificar las cuatro bibliotecas. Se lee la fuente de una sola pista para fijar hash y límites. Sin rig, rotaciones, vista previa, ejecución de herramientas externas, descifrado o cambios de banco/originales.

## Selección determinista y trazable

Se consideran únicamente registros existentes `vector_keys_decoded`, codec 4/5 y payload no vacío; se elige el mínimo de `(payload_bytes, source_sha256, slot, track)`. Hay 90 candidatos en los informes previos. Antes de seleccionar se cotejan sus hashes con `lmt-vectors-receipt.json`; sus valores no se publican ni se recalculan.

Elegida: **common_entry_0085.lmt**, 99.304 bytes, SHA-256 `35fb4bd3efaba3fc321821c92258aebfc90bd93bb29385008f97631c839faf08`; **slot 8, pista 2** (índices desde cero), codec 5, tipo de pista 1. Payload **8 bytes**, dos claves cuantizadas; clip de 171 frames declarados. Descriptor en 32.180, buffer en 32.984, extremos en 32.720. Coinciden con la fuente y caben en ella.

Informe derivado anterior: `analysis-local/lmt-vector-decoding-20261021/common_entry_0085.vectors.json`, SHA-256 `b9568c7c9115b9354a1a13758bd5f8511020436aa4c7dc77cb9f63bc887f0345`. La selección queda en `analysis-local/lmt-one-track-review-20261021/selection.json`. Solo se publican identificadores, offsets, conteos y estado de aceptación; ninguna clave o valor vectorial comercial.

## Segunda referencia primaria consultada

[wowo-dot/mhw-anim-tools](https://github.com/wowo-dot/mhw-anim-tools/tree/38967df523d4ec3b317b7c41be756be559a94f96), commit **`38967df523d4ec3b317b7c41be756be559a94f96`**. No se instaló/importó/ejecutó código del proyecto:

| Fuente | Blob | Evidencia relevante |
|---|---|---|
| [decoder.py](https://github.com/wowo-dot/mhw-anim-tools/blob/38967df523d4ec3b317b7c41be756be559a94f96/core/formats/lmt/decoder.py) | `dc869625155db39a2fc686cfb8a243a0a756400c` | `_normalized_unsigned`, `_apply_lerp_xyzw`, `_decode_u8_vector_lerp` |
| [reader.py](https://github.com/wowo-dot/mhw-anim-tools/blob/38967df523d4ec3b317b7c41be756be559a94f96/core/formats/lmt/reader.py) | `6e57739995e2147db87e3ed39a781be765e99f98` | cabecera de 16 bytes, offsets `<Q`, pistas de 48 bytes |
| [test_lmt_decoder.py](https://github.com/wowo-dot/mhw-anim-tools/blob/38967df523d4ec3b317b7c41be756be559a94f96/tests/test_lmt_decoder.py) | `13740aa990ebee3abc17ad1bfac0a58cbc2fa021` | ejemplo sintético codec 5, emisión en frame 0 y acumulación del delta posterior |
| [README](https://github.com/wowo-dot/mhw-anim-tools/blob/38967df523d4ec3b317b7c41be756be559a94f96/README.md) | `e8efcf785e95cc024e9110c739653a2a2e43e387` | alcance declarado Monster Hunter World; implementación propia mantenida |
| [Créditos](https://github.com/wowo-dot/mhw-anim-tools/blob/38967df523d4ec3b317b7c41be756be559a94f96/docs/credits-and-acknowledgements.md) | `ef660ccd414c7824b8693c5684ad827a10a7b7e3` | linaje cita MT Framework tools/Lukas Cone y MHW-LMT-Loader |

La referencia base del lector local es RevilLib. Su [lmt.inl](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_lmt/lmt.inl), commit `e17f9718ea571f040a7e1f331c28a4d45a6066b5`, blob `dcb93a3784981475bd6611095ba8174ef75db371`, distingue LMT67 del formato MHW92/95. [codecs.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_lmt/codecs.cpp), blob `7beb0d9341253e5904f5aaf6ee039aebb1fd2106`, contiene las reglas base de extremos.

## Lo que coincide y lo que no se acredita

Para buffers u8 de cuatro bytes, la segunda fuente documenta `q / 255` y después `valor_normalizado × escala + base`. Su decoder empieza el acumulador en cero, emite la clave y **después** suma el delta; conserva la base de referencia por separado. Eso coincide documentalmente con la aritmética y acumulación **sin frame de referencia** del lector local. No confirma FPS, interpolación, referencia/basis o convención temporal completa del LMT67/MHXX.

La compatibilidad del contenedor **no** queda establecida: aquí hay cabecera de ocho bytes, punteros de cuatro y pistas de 36; la referencia examinada usa 16, ocho y 48, respectivamente. Su lector recoge el número de versión, pero no selecciona un layout LMT67 de 32 bits; aceptar una firma o versión sin rechazo explícito no basta. Adaptar a mano sus objetos de pista partiendo de nuestra interpretación no proporcionaría por sí solo independencia de la lectura original.

Los créditos compartidos no prueban copia de código, y el proyecto declara implementación propia; tampoco acreditan independencia real de la investigación sobre este codec/variante. **Independencia no demostrada**, no se afirma que el código sea necesariamente dependiente. Otra implementación Python o repetir la misma fórmula no equivalen a una segunda validación.

## Aceptación cerrada como bloqueo explícito

No se ejecutaron dos decoders sobre los valores de la pista, ni se fabricó una comparación numérica. Error máximo, error temporal y tolerancias de validación independiente quedan **null**, no cero. No se informa un porcentaje de coincidencia. El contraste realizado es documental y de aplicabilidad.

**Bloqueo concreto:** falta una segunda referencia acreditada independiente y aplicable a codec 5 dentro de LMT67/MHXX LE32, o una especificación primaria que justifique equivalencia de payload y convención temporal entre variantes. Se conserva esa misma pista como control y no se amplía a otras pistas/bibliotecas. `fps=null`, unidades/ejes desconocidos, rig no asociado; ninguna función de arma/juego inferida.

[Recibo público](lmt-one-track-review-evidence.json) fija selección, fuentes, límites y bloqueo. No se modificó el decoder local ni se añadieron pruebas que repitan la fórmula y aparenten independencia; las pruebas sintéticas previas conservan su alcance. No hay nuevas pruebas de fidelidad de animación ni validación cruzada que declarar.

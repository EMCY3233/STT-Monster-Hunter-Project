# Primera conversión local: MOD230 a OBJ y TEX A6 a PNG — 22-10-2026

## Entregado y comprobado

Se convirtió la muestra MOD230 de efecto existente (990 bytes, SHA-256 ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0) en un **OBJ de 16 vértices y seis triángulos**, con UV y normales. Se generó una vista geométrica en cuatro proyecciones y se inspeccionó visualmente: forma piramidal simple de la muestra de efecto, no un monstruo. No se atribuye función concreta al efecto.

También se convirtieron dos TEX A6 a **PNG RGBA**: la muestra previa de 8×8 ETC1A4 conserva dos valores de alfa, y una entrada 16×16 ETC1 con el mismo prefijo de nombre que el MOD conserva alfa opaco. Esta segunda coincidencia de nombres permite una asociación candidata, pero **no se enlazó como material del OBJ**: el MRL y los enlaces de material no están interpretados y una coincidencia textual no basta.

Todos los derivados comerciales y la vista geométrica permanecen en `analysis-local/first-conversion-20261022/`. No se modificaron los originales, los recibos históricos ni el banco compartido. Se publicó únicamente código, pruebas y metadatos.

## Conversor geométrico

`convert_mod230_obj.py` admite exclusivamente MOD230 sin huesos, atributo 0x59DC400B/stride28 y primitive4/strip. Usa posiciones f32x3, normales snorm8 y UV f32x2 del esquema previamente delimitado. Conserva coordenadas y UV nativos; no inventa escala, eje vertical o inversión de UV. Rechaza atributos no finitos, índices fuera de rango, otros formatos y skinning.

Convierte cada strip con alternancia de orientación, reinicio 0xFFFF y eliminación de ternas repetidas o de área exactamente cero. El OBJ de prueba tiene índices válidos, seis triángulos no degenerados y límites [-1.5,0,-1.5] a [1.5,4,1.5]. Las caras orientadas coinciden, salvo rotación cíclica de sus índices, con el lector mhff fijado al blob previamente auditado. La lectura alternativa con un u16 extra no añade ninguna cara no degenerada en esta muestra.

Persiste la discrepancia histórica del contador global de índices: declara dos bytes más allá del final. El conversor usa exclusivamente las ventanas propias de malla ya comprobadas; no rellena el archivo ni altera su contador. Esto permite esta conversión estática acotada, no declara resuelta la semántica global ni compatibilidad completa con todos los MOD230.

## Conversor de textura y alfa

`convert_tex3ds_png.py` admite TEX A6 con una imagen, un mip, swizzle0, dimensiones múltiplo de ocho, ETC1/ETC1A4 y encaje exacto del payload. Reorganiza tiles8×8 y subbloques4×4, adapta el u64 little endian de 3DS al ETC1 estándar, convierte la salida BGRA del backend a RGBA y aplica cada nibble alfa A4 a su coordenada, expandido por 17. El PNG se escribe con biblioteca estándar y CRC; no se descarta transparencia.

Backend aislado texture2ddecoder1.0.6, rueda verificada con los metadatos oficiales PyPI, SHA-256 1bad8209d9dfbfc7daf13ea2e545236ea2bbc1e423b2992b6e7563909975a47b. No se instaló globalmente. Las coordenadas de filas exportadas se mantienen en el orden nativo adoptado; **orientación exacta en juego sin verificar**. No se trata una previsualización como prueba de fidelidad al juego.

La reapertura de ambos PNG mediante Pillow recupera exactamente sus bytes RGBA. El RGB de ambos coincide píxel por píxel con la implementación independiente mhff ya auditada tras invertir la convención de filas; esa función no sirve para validar alfa porque lo descarta. El alfa se contrastó por patrones sintéticos de extremos y nibbles/coordenadas, además de la fórmula del decoder de Citra. No se afirma verificación exhaustiva de todos los bloques ETC1 válidos o todos los tamaños de textura.

Ocho pruebas correctas: alternancia/reinicio de strip, paridad tras degeneración, rechazo de índice, dimensiones PNG, extremos de alfa con RGB invariante, mapa espacial de nibbles, colocación de cuatro bloques/endian/canales y ETC1 opaco. Las pruebas que requieren backend se omiten explícitamente si falta la dependencia; en esta ejecución las ocho se ejecutaron y aprobaron.

## Reproducción

```text
python convert_mod230_obj.py modelo.mod --expect-sha256 HASH --out carpeta_nueva
python convert_tex3ds_png.py textura.tex --expect-sha256 HASH --decoder-path carpeta_del_backend --out carpeta_nueva
```

No se sobrescriben destinos y se impide usar el árbol de publicación o un checkout Git como salida comercial. Los conversores requieren los lectores existentes junto a ellos. Para pruebas: STT_TEXTURE_DECODER_PATH debe señalar la instalación aislada del backend antes de ejecutar unittest sobre test_stt_re_first_conversion.py.

## Fuentes y próximos límites

- [mhff MH4U/E6, revisión fijada](https://github.com/svanheulen/mhff/blob/6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf/n3ds/io_import_scene_mod.py): comparación acotada de caras y RGB, sin importar Blender o ejecutar el módulo completo.
- [Citra texture_decode.cpp, revisión exacta](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/video_core/texture/texture_decode.cpp): orden de subtiles y alfa A4, líneas175–204.
- [Pruebas oficiales del backend](https://github.com/K0lb3/texture2ddecoder/blob/master/tests/test_main.py): salida BGRA; [PyPI1.0.6](https://pypi.org/pypi/texture2ddecoder/1.0.6/json).

La etapa estática sí produjo archivos utilizables: OBJ y PNG. No incluye rig, huesos, pesos, materiales enlazados ni animaciones LMT. Antes de animar un monstruo deben convertirse una malla con skinning y su esqueleto, resolver matrices/paletas y después asociar tracks LMT. Las muestras de esta etapa son MHXX3DS; no se presentan como una conversión probada de recursos obtenidos de la sesión MH4U ni de Switch/GU.

# MHXX: una carga TEX, cabecera y rangos sin píxeles

**Nota editorial de consolidación (22-10-2026):** El alcance de este ensayo era solo cabecera. A22ensayó después el alfa de una carga y detectó pérdida en el lector; no valida ETC1A4 completo ni aspecto visual. Véase [el índice de aceptaciones](acceptance-index.md).

Fecha: 2026-10-21. La evidencia anterior solo contaba 220 firmas TEX, sin validar sus cabeceras. Se selecciona **una sola carga**, sin decodificar imagen, visualizar, exportar píxeles ni cambiar banco/originales.

## Selección y fuente

Consulta SQLite de solo lectura sobre objetos/entradas ya catalogados: firma TEX del parche MHXX, mínimo `(bytes, sha256)`; para ocurrencias duplicadas del objeto, desempate contenedor/índice. Resultado: **84 bytes**, SHA-256 `0e5ae51392aa2a13b0800e41f2969b15a2b1b609ca9e0e1181bc3a07af110f52`.

Fuente `MHXX-patch/arc/village/common.arc`, entrada **631** desde cero, file_id 1238, type ID `241F5DEB`, ruta interna `effect\base\cm200_106_BM_NOMIP`. El nombre no determina dimensiones ni mips: se leen de cabecera. Objeto `objects/0e/0e5ae51392aa2a13b0800e41f2969b15a2b1b609ca9e0e1181bc3a07af110f52`; copia nueva privada `analysis-local/tex-smallest-20261021/source.tex`, cotejada por tamaño/hash. No se extrae otra entrada ARC ni se recataloga el banco.

## Referencias primarias aplicadas

Kuriimu2, commit **`6babcdc3562975f445f258f0b7f1d9bd8e5e2a83`**, solo rama **N3DS** consultada, no ejecutada:

- [MtTexSupport.cs](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/plugins/Capcom/plugin_mt_framework/Images/MtTexSupport.cs), blob `348b885b6996a56d7a792facf506d491648945be`: cabecera empaquetada LSB-first, versión de 12 bits, dimensiones/mips, imágenes y formato; CtrFormats relaciona 0x0C con ETC1A4.
- [MtTex.cs](https://github.com/FanTranslatorsInternational/Kuriimu2/blob/6babcdc3562975f445f258f0b7f1d9bd8e5e2a83/plugins/Capcom/plugin_mt_framework/Images/MtTex.cs), blob `05f1906e88c22b28bb8aa7cf5db2bdaeb61005f7`: Load3ds usa cabecera 16 bytes; para versiones distintas de A3/A4, tabla de offsets de cuatro bytes por mip/imagen; offsets **relativos al comienzo de datos después de la tabla**. No se aplican lectores de otra plataforma.

Contraste MH4U/3DS: [mhff io_import_scene_mod.py](https://github.com/svanheulen/mhff/blob/6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf/n3ds/io_import_scene_mod.py), commit `6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf`, blob `0da950c275caf78bfcfa310f6a45c488e890d94b`, load_tex y decode_etc1: mismo empaquetado de dimensiones/mips; formato 12 usa alfa de cuatro bits con ETC1, 16 bytes por bloque de 16 píxeles. Se revisa la fórmula del código, **sin ejecutar la decodificación**.

## Resultado estructural

| Campo o región | Observación |
|---|---|
| Firma | TEX seguido de cero, LE |
| Campo de versión | **0x0A6 / 166**, en los 12 bits documentados |
| Dimensiones | **8 × 8** |
| Imágenes / mips | **1 / 1** |
| Formato | **0x0C**, ETC1A4 según tabla 3DS |
| Campo denominado swizzle en la referencia | 0; no se aplica bloque adicional de 0x6C |
| Cabecera | [0,16) |
| Tabla de un offset | [16,20); valor relativo 0 |
| Datos comprimidos calculados | [20,84), **64 bytes** |
| Sobrantes o desbordes | cero |

Fórmula justificada para estas dimensiones completas: `(8/4) × (8/4) × 16 = 64` bytes. Coincide con el cálculo de ocho bits por píxel usado por la rama 3DS para este formato. No se generaliza a mips menores que un tile, dimensiones no múltiplo de ocho, otros formatos o padding desconocido.

Otros campos se conservan sin inferir función: nibble alto de la primera palabra=2; campo size-shift=0; u16 final=1. Los nombres/semántica completos de flags no se consideran verificados. La compatibilidad del layout y los rangos no demuestra imagen correcta, swizzle, alfa visual ni uso dentro del juego.

## Reproducción y aceptación

`tools/stt_re/inspect_tex3ds_header.py --input <copia existente> --expected-sha256 0e5ae51392aa2a13b0800e41f2969b15a2b1b609ca9e0e1181bc3a07af110f52 --out <JSON nuevo>`. Límite 1 MiB; alcance explícito A6/LE, un mip/imagen, swizzle cero, dimensiones múltiplos de ocho y formatos 0x0B/0x0C. Solo consulta cabecera/tabla y longitud; no interpreta los 64 bytes de bloques.

[Recibo público](tex-smallest-evidence.json) reúne selección, hash y rangos. Evidencia privada `analysis-local/tex-smallest-20261021/`. **Siete pruebas sintéticas aprobadas**: rango completo sin píxeles, tabla/carga truncadas, offset relativo fuera de archivo, dimensiones cero, versión ajena al alcance y formato desconocido. Sin repetir otros formatos, imágenes o batería completa.

Aceptación estructural cumplida para esta carga: firma/versión interpretadas mediante referencia, dimensiones, un mip, formato y rango coherentes. Validación funcional o visual queda fuera de alcance. Se conserva la fuente y no se amplía a las otras TEX automáticamente.

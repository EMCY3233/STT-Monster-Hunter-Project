# Campaña de regresión PC: matriz de aceptación

Fecha: 2026-10-21, Europe/Madrid. **106/106 pruebas sintéticas aprobadas**, cero fallos, errores o saltos. **21/21 herramientas** pasan compilación de sintaxis en memoria y **21/21 CLI `--help`** terminan con código cero, sin stderr. No se instalaron dependencias.

Snapshot probado: commit **`c4215e801bc14d5158321860a3afddeda790d561`**. Runtime local Windows, **CPython 3.12.14**, ejecutable SHA-256 `b07b03b9ba866a341a3c13ee69710fbc8d43d4ce2523dee13f6df5c25378d15b`. Los archivos de código/pruebas no cambian en el commit que publica esta matriz; se agregan solo resultados/documentación y su manifiesto.

## Matriz de pruebas

En todas las filas: versión **c4215e8 / Python 3.12.14**. Evidencia detallada y hash del log de unittest en [pc-regression-evidence.json](pc-regression-evidence.json), identificadas por el módulo de la segunda columna. Los números son casos sintéticos, no archivos comerciales reinterpretados.

| Prueba | Módulo de evidencia | Resultado | Límite de lo acreditado |
|---|---|---:|---|
| ARC: tabla, spans, zlib y límites | test_stt_re_arc | 8/8 | Fixtures; sin reextraer archivos ARC reales |
| ELF: secciones y entry respaldado | test_stt_re_elf_sections | 7/7 | Rangos sintéticos; no revalidación de 620 secciones ni ejecución |
| Firmas Frontier | test_stt_re_frontier_signatures | 4/4 | Marcadores; no cifrado, corrupción ni semántica |
| Cabeceras Frontier candidatas | test_stt_re_frontier_candidates | 6/6 | Longitudes/offsets; no descifrado ECD/SCE |
| Bordes de regiones suministradas | test_stt_re_frontier_layout | 5/5 | Límites y NUL; no codificación/gramática confirmada |
| Comparación de un par Frontier | test_stt_re_frontier_pair | 3/3 | Patrón parcial; no función ni formato interior |
| Cabeceras comunes MOD/LMT | test_stt_re_headers | 10/10 | Declaraciones/rangos; no geometría o reproducción |
| JKR/LZ | test_stt_re_jkr_lz | 13/13 | Ramas de token, truncamiento, backreferences y presupuestos |
| Selección JKR determinista | test_stt_re_jkr_selection | 5/5 | Filtros, desempate, no expansión de presupuesto |
| Vectores LMT | test_stt_re_lmt_vectors | 11/11 | Valores sintéticos; no decoder independiente, FPS o rig |
| TOC de DATA.BIN PSP | test_stt_re_mhfu_toc | 6/6 | Orden, centinela y límites; no repetir 6.657 transformaciones |
| Malla MOD230 | test_stt_re_mod230_mesh | 8/8 | Rango/stride/NaN/índices sintéticos; geometría completa pendiente |
| Convenciones de índices MOD230 | test_stt_re_mod230_conventions | 4/4 | Ventanas sin relleno; contador MHXX aún no explicado |
| Una referencia PSP de imports | test_stt_re_psp_import_reference | 5/5 | Archivo vs BSS, mapa sección/PT_LOAD; no invocación |
| TEX 3DS A6 | test_stt_re_tex3ds | 7/7 | Header/tabla/rangos; sin decodificación o validación de píxeles |
| Contraste de logs PPSSPP | test_stt_re_ppsspp_import_logs | 4/4 | Solo anuncios exactos nombre/dirección/tamaño, no desreferencia |
| Sintaxis de herramientas | syntax, por ruta/hash | 21/21 | Compilación en memoria, no ejecución operativa de sus lectores |
| Interfaz CLI | cli_help, por ruta/hash | 21/21 | `--help`, imports y argumentos; no procesa juegos ni arranca emuladores |

## Integridad y evidencias

- Se cotejaron **78 entradas** del SHA256SUMS del snapshot; ninguna diferencia. El archivo de manifiesto no se incluye a sí mismo. Su contenido se contrastó con el publicado en c4215e8 normalizando CRLF/LF; los hashes de código/pruebas son idénticos. La copia binaria local del manifiesto probado queda preservada para interpretar su propio SHA-256.
- SQLite del banco **antes y después**: `1ad910c69269f951f41d9ff086d66521eda6bc2d96227042f82234e64a095ce1`, sin cambio. No se recataloga ni se escribe en banco/originales.
- Informe privado: `analysis-local/pc-regression-20261021/report.json`, SHA-256 `c65108bd63750c7ded343743fd5de7d545b698ce44ef615223ad63d0430d5713`.
- Log unittest privado: `analysis-local/pc-regression-20261021/unittest.log`, SHA-256 `414d48d3318a50c3915610e23e9645d7b85e8c7202b9021058e532a371e56bce`.
- Ayudas CLI y stderr vacíos se conservan en ese directorio; el JSON público solo recoge tamaños, códigos, rutas relativas y hashes de fuentes. No publica contenido comercial o logs de juegos.

## Reproducción y decisión runtime

Desde la raíz del código de PR7, con Python 3.12:

```text
python -m unittest discover -s tests -p "test_stt_re*.py" -v
```

Para los 21 archivos `.py` de `tools/stt_re`, la campaña compiló su texto con `compile(..., 'exec')` **sin ejecutarlo** y lanzó separadamente `python <herramienta> --help`, con límite de diez segundos por proceso y ventana oculta. No se usan opciones de extracción, escaneo o emulación. El driver local y los resultados se conservan en analysis-local; no se reinstala nada.

No hay una aceptación runtime nueva que justifique otro arranque: [el contraste de logs existente](mhfu-import-runtime-review.md) ya delimita lo corroborado y lo ausente. **Cero ejecuciones de emulador, dumps, extracciones, decodificaciones comerciales o censos nuevos** durante esta campaña. No se convierten framebuffers en FPS ni se acredita fidelidad visual/comercial.

## Bloqueos que la regresión no elimina

Siguen pendientes: independencia/compatibilidad de la validación LMT67; semántica MHXX del contador global MOD230; entradas base 3DS cifradas sin material propio aportado; gramáticas interiores Frontier y uso runtime de la referencia PSP. El resultado global de pruebas es satisfactorio dentro del alcance del código probado, **no «todos los recursos descifrados y validados»**. No se amplían modelos, pistas o JKR por pasar esta batería.

# Compatibilidad regional USA/EUR — MH4UltimateDC frente a MH4U EUR (2026-10-24)

Autor: Claude (rol: investigación y compatibilidad regional, orden de coordinación multiagente del 2026-10-24).
Alcance: investigación y documentación. No se integra código. No se incorpora ROM, ejecutable, clave, volcado, recurso comercial ni pseudocódigo. No se tocó Vita/FTP/firmware.

## Etiquetas de evidencia

Se usan las mismas etiquetas que en la auditoría del PR #50:

| Etiqueta | Significado |
|---|---|
| **E** | Código o metadato público inspeccionado por `git show` en el SHA indicado. |
| **R** | Resultado reportado por el mantenedor y no reproducido aquí. |
| **H** | Hipótesis sin demostrar. |

Las fuentes son las siguientes:

- **MH4UltimateDC main** en `e06b0ca30b9b2d66ec7785f277ead4bb35374b28` (abreviado `MH@e06b0ca`).
- **MH4UltimateDC native** en `a6b71de1221e895312273d0378b7a2e8513955fa` (abreviado `MHn@a6b71de`).
- **STT main** en `f199bd07b4e05ee4f7e56ed616840518374f3300`.

## 1. Conclusión

MH4UltimateDC está atado a una única imagen binaria: **USA v1.3.0, `code.bin` con SHA-1 conocido**. Solo una parte pequeña del proyecto es independiente de la región: el método de recompilación, el decoder ARM/Thumb/VFP, el runtime de contexto, los arneses de prueba y los servicios HLE de native.

Todo lo que da valor práctico al port está indexado por direcciones absolutas de ese ejecutable. Eso incluye la tabla de funciones, los hooks, los tunables, los símbolos, las clases MT, las entradas extra y las funciones reescritas a mano.

Un perfil EUR **no es un cambio de configuración**. Requiere regenerar o remapear esas tablas a partir de una imagen EUR propia del usuario, y validarlas desde cero.

No hay evidencia pública verificada aquí de que EUR y USA compartan `code.bin`. Mientras no se demuestre lo contrario, se tratan como binarios distintos (H, conservadora).

## 2. Cómo se fija la versión en MH4UltimateDC (E)

- **Huella de versión:** `config/versions.json` contiene una sola versión, `"target": true`, con estos datos:
  - Nombre: *USA v1.3.0*.
  - `program_id` `0004000000126300` y `update_title_id` `0004000E00126300`.
  - `title_version` 1072.
  - SHA-1 del `code.bin` descomprimido y del exheader.
  - `code_size` `0xF82000` y segmentos `text` `0x00100000`+`0x00CEC734`, `rodata`, `data` y `bss` con direcciones fijas.
- **Comprobación en la construcción:** `tools/build_game.py` (alrededor de las líneas 224-226) calcula el SHA-1 del `code.bin` y lo busca en `versions.json`. Así, la construcción de la biblioteca de código se ancla a un hash conocido.
- **Comprobación en tiempo de ejecución:** según `port/README.md` línea 120, si el código cargado no es el recompilado, el backend lo registra e interpreta todo. Es un respaldo seguro, pero no sirve para EUR: EUR caería a interpretación completa, sin recompilación ni hooks.
- **Identificador de título en la app:** `port/app/launcher/checks.h` líneas 14-16 define `MH4U_USA = 0x0004000000126300` y `UPDATE_VERSION = 1072`. El mismo identificador aparece repetido en `lobby.cpp:18`, `multiplayer.cpp:57`, en las rutas de texturas `load/textures/0004000000126300/` y en el nombre de la biblioteca `recomp/<program id>.so`.
- **Documentación:** `FAQ.md` líneas 25-26 dice que EUR y JPN no están soportadas todavía, y solo USA v1.3.0 (`0004000000126300`). `.github/ISSUE_TEMPLATE/bug_report.yml:49` y las release notes exigen USA y v1.3.0.
- **Región en native:** `MHn@a6b71de docs/native/DECISIONS.md` D38 lee la región de consola del `icon.bin` ExeFS, o de `--region`. Esto hace que la región de la consola no esté fijada en código, pero no cambia que las tablas sigan siendo de USA. `ROADMAP.md:207` sitúa «other regions» en N7, la etapa opcional.

## 3. Matriz de compatibilidad USA/EUR

La primera columna indica el tipo de componente:

| Tipo | Significado |
|---|---|
| **I** | Independiente de la región. |
| **D** | Dependiente de direcciones o estructuras binarias. |
| **V** | Requiere validación específica. |

| Componente (MH@e06b0ca salvo indicación) | Tipo | Evidencia | Qué hace falta para EUR |
|---|---|---|---|
| Decoder ARMv6K/VFPv2/Thumb-1 (`tools/recomp/arm.py`, `thumb.py`) | I | E: opera sobre codificaciones, no sobre direcciones del juego (RECOMPILER.md §2) | Nada específico de región. Revisar la licencia antes de reutilizarlo |
| Emisor C, CFG, jump tables, `rc_call`, caché inline (`emit.py`) | I (método) | E: RECOMPILER.md §3-4 | Reejecutar el análisis sobre el binario EUR. Los resultados (3.475 jump tables resueltas, R) son de USA |
| Runtime `recomp.h` (`RCtx`, VFP, TLS, ciclos) | I | E | Sin cambios por región |
| Fibers (`port/src/fiber.h`, pila de 8 MiB) | I | E | Sin cambios por región. Para Vita, el tamaño de la pila es un problema aparte (§6) |
| `config/versions.json` | D | E: solo una entrada USA | Nueva entrada EUR con hashes, `program_id`, `title_version` y segmentos medidos en el dump propio del usuario |
| `config/functions.tsv`, 31.410 entradas | D | E: cada fila empieza por una dirección absoluta (por ejemplo `0x00100000 entry`). Estados: 30.828 todo, 570 replace y 11 done | Regenerar la tabla con el mismo pipeline (Ghidra y la segunda pasada) sobre el binario EUR. No reutilizar las direcciones USA |
| `config/extra_entries.txt`, 597 entradas | D | E: cabecera «USA v1.3.0» | Regenerar con `missing_targets.txt` de gametest sobre EUR |
| `config/symbols.txt`, 173 entradas | D | E: cabecera «Accepted names for USA v1.3.0» | Remapear por firma o similitud, o volver a identificar. Cada nombre necesita evidencia propia |
| `config/mt_classes.tsv`, 993 entradas | D | E: direcciones de vtable y de padre por clase | Remapear. La jerarquía (nombres y tamaños) podría coincidir (H) |
| `config/hooks.txt`, 31 hooks | D + V | E: cabecera «USA v1.3.0 addresses» | Localizar cada función hook en EUR y validar que su semántica sea igual |
| `config/tunables.txt`, 3 tunables (dirección e inmediato original) | D + V | E: RECOMPILER.md avisa si el inmediato no aparece exactamente una vez | Localizar en EUR. El mecanismo ya detecta un desajuste |
| `port/src/hooks.cpp`, 86 literales de dirección (por ejemplo `QUEST_HUD 0x0108260c`, la tabla de filtros `0x00e5…`) | D + V | E: líneas 731, 981, 1143 y 1315-1331 | Remapear todas las constantes y validar los offsets de estructura (`+0x9788` y similares) |
| `src/unsorted/func_<addr>.c` (reescrituras «replace» y «done») | D + V | E: el nombre lleva la dirección. Difftest 1000/1000 sobre USA (R) | Asociar con la función EUR y repetir el difftest |
| `tools/build_game.py`, `verify_dump.py`, `verify_ncch.py` | I (lógica) + D (datos) | E | Que acepten el perfil EUR a través de `versions.json` sin relajar la comprobación de hash |
| Launcher y app (`checks.h`, `lobby.cpp`, `multiplayer.cpp`, rutas de texturas) | D (constante de título) | E | Parametrizar el identificador por perfil |
| Mods de código (`code_mods`) y texturas | D + V | E/H: hashes y rutas por título | Los parches binarios no son transferibles. Los packs de texturas dependen del hash de textura, posiblemente igual (H) |
| `azahar.patch` y plataforma Azahar | I | E: la plataforma emula la 3DS, no el juego | Sin cambios por región, salvo la configuración de región y idioma |
| native: servicios HLE (fs, cfg, ptm, apt, dsp, gsp…) | I + V | E: D38 deriva la región de `icon.bin` | Idioma y región de cfg correctos para EUR. Los ficheros de RomFS y guardado podrían diferir en rutas y tamaños (H) |
| native: golden sessions G1-G8 y perfiles de comparación | D (datos) | E/R: se graban con el juego USA en el PC del mantenedor | Grabar golden EUR propias. Las sesiones USA no sirven como referencia EUR |
| Red (salas, NEX) | V | E: FAQ:54, salas compatibles con Azahar oficial | Sin verificar si EUR y USA pueden jugar juntas (H) |
| STT `arm-leaf-lab` (#45/#48) | I | E: fixtures sintéticos originales | No depende de región. Puede quedarse como banco de equivalencia |

## 4. Diferencias USA/EUR

**Conocidas (E, con fuentes):** ninguna diferencia binaria está documentada en las fuentes inspeccionadas. Sí consta que MH4UltimateDC solo admite USA v1.3.0 (`FAQ.md:25-26`, `versions.json`).

**No verificadas (H). Hay que medirlas en el dump propio del usuario:**

1. El `program_id` EUR, el `update_title_id` y la `title_version` de la última actualización. No se encontró una fuente pública fiable en esta sesión, así que no se escribe ningún valor.
2. Si el `code.bin` EUR difiere del USA. Previsión conservadora: sí, por localización multilingüe y versión de parche distinta.
3. El tamaño de los segmentos y las direcciones base de `text`, `rodata`, `data` y `bss`.
4. Si el desplazamiento es uniforme por segmento, lo que permitiría remapear con un delta, o no uniforme, lo que obliga a reidentificar función por función.
5. Si la actualización EUR equivalente contiene los mismos cambios de juego que la v1.3.0 USA.
6. Si las estructuras de datos (offsets de miembro en hooks) coinciden.
7. Si RomFS, idiomas y texturas tienen los mismos hashes.
8. Si hay compatibilidad de red entre regiones.

## 5. Estrategia propuesta: perfiles regionales

1. **El perfil como dato y no como código.** Un directorio por versión, por ejemplo `config/profiles/<program_id>-v<title_version>/`, con su propio `versions`, `functions`, `hooks`, `symbols`, `mt_classes`, `extra_entries` y `tunables`. El perfil USA actual sería solo el primero.
   - Lo que se commitea son hashes y direcciones obtenidos por el usuario de su copia. Nunca bytes del juego.
   - Antes de añadir ficheros de perfil, hay que confirmar con la política de datos del proyecto (LEGAL y CONTRIBUTING) que esas tablas de direcciones son aceptables (V).
2. **Selección por hash.** `build_game` y el backend eligen el perfil por el SHA-1 del `code.bin`. Si no hay perfil, se mantiene el respaldo actual (interpretar) y nunca se aplica una tabla de otra versión.
3. **Remapeo asistido, no automático.** Una herramienta local puede proponer correspondencias USA→EUR por firmas, por ejemplo con hashes de bloques normalizados sin direcciones, o por referencias cruzadas. Esa herramienta solo genera tablas en el equipo del usuario.
   - Cada correspondencia propuesta empieza en `todo` y solo pasa a `done` tras el difftest.
   - El código de la herramienta debe ser original, o reutilizado cumpliendo la GPL-3.0-or-later.
4. **Hooks por contrato.** Cada hook declara su firma y sus efectos esperados. Un hook EUR solo se activa si su test de contrato pasa en esa versión.
5. **Separación estricta.** La compatibilidad regional se trata en PC. Vita queda fuera de este trabajo (§6), tal como pide la orden.

## 6. Implicaciones para el futuro runtime de PS Vita (H)

- **Cada perfil regional es un artefacto independiente:** cada uno requiere una recompilación completa y su propia validación. El tamaño de código y la memoria se miden por perfil.
- **Lo independiente de región también es lo portable:** decoder, emisor, `RCtx` y servicios HLE. Lo dependiente de región (hooks de FPS/HUD y widescreen) es lo menos prioritario para Vita.
- **La elección de región no reduce los bloqueos de Vita:** GPU PICA200, DSP, memoria y fibers con pila de 8 MiB siguen ahí (ver PR #50, §PS Vita). No se da ninguna cifra de rendimiento ni de memoria.

## 7. Bloqueos

| Bloqueo | Tipo |
|---|---|
| Sin dump EUR propio no se puede medir nada de §4. No se usarán copias de terceros | Datos |
| STT no tiene licencia declarada, así que no se puede importar código GPL-3.0-or-later (ver PR #50) | Legal |
| Las tablas de MH se generaron en parte con Ghidra en el PC del mantenedor. Reproducirlas para EUR exige ese pipeline y entradas privadas | Herramientas |
| Las golden sessions native son USA y privadas, así que no sirven como oráculo EUR | Validación |
| La política de MH sobre commitear tablas de direcciones (permitido hoy en el repo) aún no está contrastada con la política de STT | Política |

## 8. Plan de validación del perfil EUR

Todas las pruebas son locales, sobre la copia propia del usuario, y sus resultados se reportan de forma agregada, sin bytes del juego.

| Puerta | Prueba | Criterio |
|---|---|---|
| R0 | Identificar la versión: `program_id`, `title_version`, SHA-1 del `code.bin` y el exheader, y segmentos | Los valores quedan registrados como E en la entrada de perfil |
| R1 | Comparar estructuras de USA y EUR: tamaños de segmento y presencia o ausencia de las 31 funciones hook por firma | Informe con el número de funciones mapeadas, no mapeadas y ambiguas |
| R2 | Recompilar con el perfil EUR y ejecutar `gametest` con todas las funciones | Ningún «different state». Los inconclusos y los fallos coincidentes se cuentan por separado y no cuentan como pass |
| R3 | Difftest 1000/1000 de cada función `replace` y `done` remapeada | Todas pasan. Las que fallan se quedan sin reescribir |
| R4 | Test de contrato de cada hook EUR | Un hook sin test pasado no se activa |
| R5 | Boot en PC: sesiones equivalentes a G1/G2 grabadas en EUR (Azahar como referencia, recompilado como candidato) | Mismas escenas y mismo orden. Las tolerancias se documentan como D76 |
| R6 | Idioma, región y guardado: cfg EUR y datos de guardado propios | Sin errores de región ni de idioma |
| R7 | Vita | Fuera de alcance. Requiere una autorización futura específica |

## 9. Reutilización y licencias, evaluación inicial

- MH4UltimateDC es GPL-3.0-or-later (E: `LICENSE`, `README.md:68-70`), y su main deriva de Azahar, que es GPL-3.0. Reutilizar código obliga a que el conjunto distribuido cumpla la GPL: aviso, fuente correspondiente y misma licencia.
- **Reutilizable como diseño sin copiar:** el esquema de perfil por hash, la tabla de estados de funciones, los hooks por contrato y la metodología de difftest y gametest.
- **Reutilizable como código solo tras decidir la licencia de STT:** decoder, emisor, `recomp.h` y herramientas de verificación.
- **No reutilizable para EUR:** todas las tablas de direcciones USA y `hooks.cpp` tal como está. Además no aportan nada a EUR sin remapeo.
- La GPL del tooling no concede derechos sobre el juego. Las tablas EUR derivadas del dump del usuario deben revisarse según §5.1.

## 10. Siguiente paso recomendado

1. Codex: añadir al laboratorio STT un caso sintético de selección de perfil por hash, que rechace un perfil desconocido sin aplicar tablas.
2. OpenCode: revisar esta matriz y contrastar las etiquetas E con los SHA citados.
3. Usuario: si quiere avanzar, ejecutar localmente la puerta R0 sobre su copia EUR y compartir solo los metadatos (identificadores, versión, hashes y tamaños de segmento).

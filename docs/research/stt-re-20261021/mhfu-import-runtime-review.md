# MHFU: contraste de la referencia con registros PPSSPP existentes

Fecha: 2026-10-21. Tras cerrar la carga TEX, se consultaron los logs previos antes de decidir sobre otro arranque. **Cero ejecuciones y cero dumps nuevos** en esta etapa; se reutilizan dos ejecuciones históricas, artefacto y recibos. No se instalan emuladores/firmware ni se cambia perfil, partida, WLAN, plugins, ISO o consola.

## Evidencia cotejada

Emulador portátil existente: PPSSPP **1.20.4**, ejecutable SHA-256 `27d3edbb06dc623dab60877d3e3a975aef4034c7d4fac464e92fd4998864d2ec`, vuelto a comprobar contra ambos recibos. Los registros completos permanecen privados:

| Registro histórico | Bytes | SHA-256 | Líneas cotejadas |
|---|---:|---|---|
| ppsspp-probe-20261021/ppsspp.log | 8.575.268 | `79a21291a537a17bf56e66c0e16a5f6eb2c4fa8a3f6aca56fd6dd4f50f6972de` | 903 y 910 |
| ppsspp-decrypt-20261021/ppsspp.log | 2.200.208 | `8b5b5c8fc8eb244a8779d1c8b1e714932c3320552b69203336870df5f2104a03` | 912 y 919 |

En **ambos** aparecen anuncios de sección del loader con valores exactos:

- `.lib.stub`: VA `0x0890E6D4`, tamaño `0x2A8` = 680 bytes.
- `.rodata.sceNid`: VA **`0x0890EC78`**, tamaño `0xC80` = 3.200 bytes.

Coinciden con las secciones origen/destino del [mapa estático de una referencia](mhfu-import-reference.md). La evidencia estática y su recibo también se verifican por hash. Se busca nombre, dirección **y tamaño**, no un número hexadecimal aislado.

Los recibos históricos conservan ISO SHA-256 antes/después `5ebab623367e78c68033bb4b40e454b84ea974c4aa5e9819641232181d3f8139`, fuente sin cambios y terminación del proceso propio por límite. Son comprobaciones **de aquellos ensayos**, no hashes presentados como resultado de un arranque nuevo. El segundo registro corresponde al volcado antiguo ya conservado; no se vuelve a producir.

## Qué significa el anuncio y qué no demuestra

Fuente primaria de interpretación: [PPSSPP Core/ELF/ElfReader.cpp, tag v1.20.4](https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/ELF/ElfReader.cpp), blob **`e4fd7e2bf898068de37b8a4386388a0fff7e81af`**. El mensaje Data Section found calcula `writeAddr = sh_addr + baseAddress`, marca una subasignación y anuncia nombre/tamaño desde la cabecera de sección. Se consultó código, sin ejecutarlo de nuevo.

**Corroborado:** el loader de las ejecuciones previas anuncia esas mismas direcciones/tamaños de secciones. Confirma correspondencia entre el mapa estático y la asignación anunciada durante carga. La dirección de destino de nuestra referencia cae al inicio de la sección NID anunciada.

**No corroborado:** que el loader o el juego lean específicamente el campo de puntero en VA `0x0890E6E0`, offset `0x0010CC94`, y desreferencien su destino; identidad de los tres NID, resolución de una función o invocación posterior. El anuncio se deriva de las cabeceras, no de una traza de lectura de ese campo ni una inspección independiente del contenido de memoria. No convierte una coincidencia de dirección en comportamiento demostrado.

No se cuentan presentaciones de framebuffer como FPS ni se afirma validación visual, progreso jugable, combate o IA. `fps=null`, `visual_validation=false` e identificación/invocación funcional sin verificar.

## Decisión sobre nuevo arranque

No se repite por duración: la coincidencia de secciones ya está en dos logs cotejados. Otro arranque con las mismas clases de mensajes no sería un método para probar la desreferencia concreta. La aceptación termina con **corroboración parcial de dirección/tamaño**, y bloqueo explícito del vínculo runtime↔lectura/uso del puntero. Para esa aceptación haría falta una traza o evento que identifique ese acceso concreto, no más tiempo de ejecución; no se añade instrumentación ni se amplía a otras referencias en esta etapa.

## Reproducción y pruebas

`tools/stt_re/compare_ppsspp_import_logs.py --root <proyecto> --out <JSON nuevo>`. Verifica hashes de logs/recibos y ejecutable existente, coteja únicamente las dos secciones de la referencia y publica metadatos/líneas, sin logs completos o bytes del juego. [Recibo público](mhfu-import-runtime-evidence.json), original privado `analysis-local/psp-import-runtime-review-20261021.json`.

Cuatro pruebas sintéticas nuevas aprobadas: anuncio exacto, rechazo de otra sección en igual dirección, tamaño discordante y dirección sin contexto de anuncio. No se repiten censos/baterías completas ni se altera banco, partidas, originales o ramas ajenas.

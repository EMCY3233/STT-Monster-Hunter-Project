# Índice consolidado de aceptaciones PR7

**Nota de herramientas posterior al índice:** [sky mediante computer-use](native-visual-surface.md) tiene importación/listado nativo comprobados. La limitación previa solo se acreditó para CUA REPL; captura de Citra aún no probada, sin nuevo arranque ni cambio de estado A21.

Consolidación documental: 22-10-2026, Europe/Madrid. Fuente: los 23 commits de PR7 hasta [e8a0c7b](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/e8a0c7bcb65ca0ef474285087d4f15c2a7d50c88). Este índice no incorpora pruebas, censos o lecturas nuevas de juegos. Los recibos originales se conservan.

**29 aceptaciones:** 22 verificadas dentro de su alcance, 2 negativas y 5 bloqueadas. Una aceptación verificada no implica semántica, jugabilidad, rig funcional o fidelidad de hardware.

Los commits identifican la entrega de cada aceptación. Los hashes de documentos JSON en [el índice estructurado](acceptance-index.json) fijan la evidencia del snapshot fuente; los informes Markdown pueden llevar notas editoriales posteriores. Los IDs de entrada se resuelven al final con SHA256 completos. Para conjuntos no se inventa un hash agregado: se listan miembros o se identifica el recibo, expresamente como documento.

## Aceptaciones y criterios de reapertura

| ID / alcance | Estado y resultado delimitado | Commit / entradas | Criterio para avanzar o reabrir |
|---|---|---|---|
| [A01 · Auditoría inicial de archivos y banco](README.md) | **verificado** · Snapshot de 10.641 archivos y originales/catálogo cotejados; no censo actual. | [d1765f9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/d1765f984deaa5dd830e335b44c0fcac045dcd4c); AUDIT | Reabrir solo con un conjunto de entradas cambiado y alcance de auditoría nuevo. |
| [A02 · Ejecutables legibles iniciales](README.md) | **verificado** · ELF/ExeFS y hashes iniciales; descompresión y secciones eran pasos posteriores. | [d1765f9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/d1765f984deaa5dd830e335b44c0fcac045dcd4c); BOOT, MHXX_NCCH, MHXX_CODE_COMP | Solo ampliar una propiedad no cubierta; no repetir cabeceras equivalentes. |
| [A03 · Secciones ELF PSP](continuation.md) | **verificado** · 620 secciones declaradas verificadas en alcance estático; no funciones. | [e4b40c4](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/e4b40c4c224315d99a3af84c44d5638bdab2f7b2); BOOT | Referencia nueva con VA/offset y límites, no recuento repetido. |
| [A04 · Frontier parcial, snapshot histórico](continuation.md) | **verificado** · Lecturas parciales de 1.027/1.653 archivos; no representaban copia completa. | [e4b40c4](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/e4b40c4c224315d99a3af84c44d5638bdab2f7b2); FRONTIER_PARTIAL | No reabrir como estado actual: sustituido por A09; conservar errores/recibos. |
| [A05 · Vectores LMT67 limitados](lmt-vectors.md) | **verificado** · 90 pistas/1.772 claves vectoriales; sin rotaciones, FPS o vínculo rig. | [3bdce7d](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/3bdce7d6d1cfcda0314fd372a0f1ce8ea7a85441); LMT_SET | Referencia compatible e independiente para la misma pista antes de fidelidad. |
| [A06 · PPSSPP y EBOOT MHFU](emulators.md) | **verificado** · Arranques acotados y dump cuyo prefijo coincide con BOOT; no visual/FPS. | [097f64f](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/097f64f31b4133f6f721cdd25d69efc51700f867); ISO, EBOOT | Solo observación nueva con instrumentación útil; no dumps repetidos. |
| [A07 · Instalación CIA con Citra](citra.md) | **bloqueado** · CIA base cifradas; update instalado en ruta corta, pero ejecución aislada falló. | [097f64f](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/097f64f31b4133f6f721cdd25d69efc51700f867); CIA_SET, MHXX_NCCH | Cambio causal en entrada compatible; la NCSD MH4U es distinta y no resuelve CIA. |
| [A08 · MHFU DATA.BIN completo](mhfu-data.md) | **verificado** · 6.657 entradas asignadas procesadas y round-trip; longitudes sin padding/semántica no probadas. | [097f64f](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/097f64f31b4133f6f721cdd25d69efc51700f867); DATA | Gramática interior de una entrada con criterio nuevo, no otra extracción masiva. |
| [A09 · Frontier completo y 50 candidatos](frontier-complete-headers.md) | **verificado** · Censo completo comunicado por otro frente; aquí 44 JKR/5 ECD/1 SCE cotejados. | [ee9bcd4](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/ee9bcd4f848428a2382490692fce7db46c1c8092); FRONTIER_CANDIDATES | Una propiedad semántica acotada; no repetir censo ni afirmar jugabilidad/ZZ. |
| [A10 · Primera muestra JKR/LZ](frontier-jkr-sample.md) | **verificado** · 238→349 bytes, flujo completo; formato interior desconocido. | [bf1f41c](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/bf1f41c38856dd9dab83fc748831b39e13e0feba); JKRA, JKRA_OUT | Nueva gramática primaria aplicable a esa salida; no abrir otras42 por analogía. |
| [A11 · Bordes/gramáticas del JKR A](frontier-jkr-layout.md) | **bloqueado** · Anclas y patrón parcial observados; estructuras candidatas no validan gramática. | [d9b940d](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/d9b940dc5a701d9367b30a5ffa8dcaba9015a3ec); JKRA_OUT | Evidencia primaria que explique offsets/longitudes sin texto comercial publicado. |
| [A12 · JKR B y comparación del patrón](frontier-jkr-pair.md) | **verificado** · 1.058→1.884 bytes; patrón de A no se generaliza a B, sin gramática interior. | [90dc6d1](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/90dc6d1081a6abeec1ccd89f6ade40e9a0c2b0bc); JKRA_OUT, JKRB, JKRB_OUT | Hipótesis de formato nueva y presupuesto explícito sobre estas mismas muestras. |
| [A13 · MOD990: malla parcial](mod230-smallest.md) | **verificado** · Spans de una malla/atributos finitos e índices locales; geometría completa no. | [10f3f10](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/10f3f1076e076eadc8ed6112610a8354a4137d8d); MOD990 | Explicar discrepancia global en esta muestra antes de ampliación geométrica. |
| [A14 · MOD990: convenciones de índices](mod230-index-conventions.md) | **bloqueado** · 29 u16 caben con convención MH4U; contador global 30 y min/max pendientes. | [4d0e9a9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/4d0e9a9a800c945f735af896d41e94696953a9af); MOD990 | Referencia específica MOD230/MHXX que resuelva el contador sin rellenar bytes. |
| [A15 · Una referencia de imports PSP](mhfu-import-reference.md) | **verificado** · Puntero NID mapeado por sección y PT_LOAD; no funciones/invocación. | [c529799](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/c52979925181539b70ff5335bec30f06d1e35c7b); EBOOT, BOOT | Observación instrumental que cubra la lectura relevante, no etiquetas por nombres. |
| [A16 · Independencia/compatibilidad LMT](lmt-one-track-review.md) | **bloqueado** · Fórmulas documentales compatibles; independencia y contenedor no acreditados. | [19d6e9d](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/19d6e9d1bc8c987de7262764f992578a31c30804); LMT_TRACK | Nueva evidencia primaria independiente compatible con LMT67 LE32; no repetir búsqueda igual. |
| [A17 · Una cabecera TEX3DS](tex-smallest.md) | **verificado** · A6/8×8/ETC1A4, tabla y 64 bytes de bloques encajan; sin fidelidad visual. | [3f95616](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/3f95616430bb156008fe6ef7c2b9e0fec93daa41); TEX84 | Decoder alfa correcto e independiente con controles antes de otra carga. |
| [A18 · Logs previos PPSSPP vs mapa](mhfu-import-runtime-review.md) | **verificado** · Dos logs anuncian secciones coincidentes; no prueba desreferencia o llamada. | [c4215e8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/c4215e801bc14d5158321860a3afddeda790d561); PSP_LOGS, EBOOT | Instrumentación armada antes del acceso y cobertura HLE demostrada. |
| [A19 · Regresión PC106/21CLI](pc-regression-matrix.md) | **verificado** · Snapshot106 tests,21 sintaxis/21 ayudas; no nueva evidencia comercial o hardware. | [f2417f4](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/f2417f43282a65de8c3ff97808d6702e5f3b31f0); PC_SNAPSHOT | Solo repetir checks cuando cambios o fallos lo justifiquen; no sumar campañas. |
| [A20 · Comparativa emuladores](emulator-comparison.md) | **verificado** · Fuentes/versiones fijadas; no instalación Azahar/Vita3K ni compatibilidad local prometida. | [964770a](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/964770ad40a6c7dfc7df6bc4294858521ae7ff55); EMULATOR_SOURCES | Cambio de versión/entrada o ensayo con aceptación nueva; no reabrir cifrado inalterado. |
| [A21 · Base MH4U NCSD en Citra](citra-current-inputs.md) | **verificado** · Una ejecución15s con loader/DSP y hash intacto; sin pantalla/FPS/jugabilidad. | [964770a](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/964770ad40a6c7dfc7df6bc4294858521ae7ff55); MH4U_NCSD | Control visual fiable u otra observación distinta; no mismos logs de arranque. |
| [A22 · Alfa descartado por lector TEX](tex-decoder-audit.md) | **negativo** · Controles alfa0/FF y muestra local confirman pérdida de alfa en mhff. | [964770a](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/964770ad40a6c7dfc7df6bc4294858521ae7ff55); TEX84 | Decoder que aplique alfa con controles independientes; no asumir RGB/orientación. |
| [A23 · BLZ del update MHXX](mhxx-code-blz.md) | **verificado** · 13.045.760 bytes, flujo/prefijo 84 y páginas coherentes; update no base. | [3e9bbdb](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/3e9bbdb032cf448194b09c07499fb5ee4ecde264); MHXX_NCCH, MHXX_CODE_COMP, MHXX_CODE_OUT | Referencia independiente compatible o propiedad estática distinta; no otro BLZ propio. |
| [A24 · Entrada derivada del loader MHXX](mhxx-entry-reference.md) | **verificado** · VA 0x00100000→offset 0/text r-x y A32 esperado según loader; no ejecución. | [d419d6b](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/d419d6b41e7c21ee9cb11025df50fb120f0a75f2); MHXX_CODE_OUT | Evidencia de ruta/estado observados si fuese viable; no función atribuida a opcode. |
| [A25 · Partición0/ExeFS base MH4U](mh4u-ncsd-executable.md) | **verificado** · Cabeceras/tres hashes íntegros, CPU como solicitudes, pie BLZ coherente. | [1bdf73e](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/1bdf73ecd6f3535b2d83c105b1847f3f9806ccca); MH4U_NCSD, MH4U_CODE_COMP | La fase solo-declaración fue ampliada por A26; no repetir cabeceras. |
| [A26 · BLZ de la base MH4U](mh4u-code-blz.md) | **verificado** · 16.261.120 bytes, flujo/prefijo 76 y backing; rehash por rango, no imagen completa. | [93455dc](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/93455dcab83d823d1b4218b039aa29e951e5e7a1); MH4U_CODE_COMP, MH4U_CODE_OUT | Contraste independiente acreditado, manteniendo whole_image_unchanged_reverified=false. |
| [A27 · Independencia BLZ](mh4u-blz-independent-review.md) | **bloqueado** · CTRTool/CUE/3dstool revisados; segunda comparación no realizada, igualdades=null. | [a914801](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/a914801aa3865a516aba848a214d055243ca6284); MH4U_CODE_COMP, MH4U_CODE_OUT | Linaje independiente compatible acreditado antes de otro decoder; no búsqueda repetida. |
| [A28 · Una jerarquía MOD230](mod230-skeleton.md) | **verificado** · 3 huesos/2 raíces/0ciclos,6 matrices finitas y tablas encajan; no rig funcional. | [16111d8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/16111d8ee806d46b835b72b6a7541bc6d7366d3f); MOD3 | Nueva semántica específica de matrices; A29 no confirma el modelo probado. |
| [A29 · Relación jerarquía↔matrices](mod230-matrix-property.md) | **negativo** · Modelo global×inversa al 1e-4:0/3 pares, residuo143,626968; fuente intacta. | [e8a0c7b](https://github.com/EMCY3233/STT-Monster-Hunter-Project/commit/e8a0c7bcb65ca0ef474285087d4f15c2a7d50c88); MOD3 | Fuente específica de espacios/convención para esta variante; no ajustar tolerancia/órdenes. |

## Conclusiones históricas superadas

Las afirmaciones siguientes se conservan en sus informes fechados. Cambia su aplicabilidad actual, no se reescribe lo observado entonces. Las salvedades aún abiertas no se consideran superadas.

| ID / afirmación histórica | Estado posterior acreditado | Límite que permanece |
|---|---|---|
| H01 · Frontier ausente o copia parcial/incompleta | Copia local completa comunicada:8261 archivos; este frente verificó50 candidatos, no todos los 8261 de nuevo. (A09) | ZZ, ejecutable funcional, capas y online siguen sin validar. |
| H02 · Ninguna base 3DS legible | Existe MH4U EUR .3ds NCSD legible, distinta de CIA; loader/DSP y análisis estático acreditados. (A21, A25, A26) | Las CIA MH3U/MH4U/MHXX siguen cifradas; no equivale a jugabilidad. |
| H03 · .code MHXX no descomprimido | Una descompresión del update13.045.760 bytes en A23. (A23, A24) | Update no base; semántica e independencia pendientes. |
| H04 · MH4U: solo tamaño BLZ declarado | Una descompresión real16.261.120 bytes, consumo/prefijo/backing en A26. (A26) | No hash independiente; imagen entera no reverificada después. |
| H05 · Solo cabeceras MOD, sin jerarquía | Una muestra de 3 huesos acredita estructura; modelo numérico de matrices posterior falló0/3. (A28, A29) | No rig funcional; MOD990 y sus índices siguen abiertos, no sustituidos. |
| H06 · TEX: no ensayo de píxeles/alfa | Auditoría posterior de una carga y controles sintéticos demostró descarte de alfa por mhff. (A22) | No decoder ETC1A4 completo, RGB/orientación o aspecto en juego aceptados. |
| H07 · BOOT visible; EBOOT sin descifrado probado | Dump PPSSPP local con prefijo idéntico a BOOT y cola340 bytes sin interpretar. (A06, A15) | No identifica funciones ni ejecución del import. |
| H08 · Cifras globales de archivos/tests como estado actual | Cada cifra pertenece a un recorrido/campaña fechado; no censo ni suite nuevos en esta consolidación. (snapshots fechados) | No sumar campañas como nueva suite; no proyectar7 originales sobre entradas añadidas. |
| H09 · Frontier soloG sin patchZ acreditado | SFO baseG1.00 y patchZ01.99 observados en etapa posterior; copia local cerrada. (A06, A09) | ZZ sigue sin confirmarse; nombre de carpeta o emulador no lo acredita. |
| H10 · Investigación inicial también incluía Switch/GU | Usuario excluyó GU/Switch; referencias antiguas quedan como antecedentes. (A03, A20) | Sin nuevas pruebas ni compatibilidad Switch declarada. |

## Identidades de entrada

SHA256 completos siguientes, de recibos existentes: **no son hashes recalculados de juegos en esta consolidación**. MH4U_NCSD conserva el hash completo histórico; A26 solo reverificó cabeceras/rango y mantiene whole_image_unchanged_reverified=false.

| ID / objeto o evidencia | Identidad | Tipo y alcance |
|---|---|---|
| AUDIT · Recibo de auditoría inicial | `218503b92323f69c415ed0bd209adb20a96d68e12278252deae94ef6223e3595`; 1128 bytes | evidence document, not a game-set aggregate hash |
| FRONTIER_PARTIAL · Recibos de cortes parciales Frontier/ELF | `7ac9bf60880a4404d756bc1ca79152db0e96665fe3281ffbe0d2611da4f9c91f`; 3523 bytes | evidence document, not a game-set aggregate hash |
| FRONTIER_CANDIDATES · Manifiesto externo de50candidatos Frontier | `b990d19577b07448a03d8d261e5014aca712aec2d06740adcaf782f0be2f50be` | candidate catalogue document |
| BOOT · Prefijo canónico BOOT.BIN PSP | `74a0b779ea98f16dc8a9498487a8df6a712891e83a07ef4d533a948df1f4f4df`; 1910044 bytes | game file or derived range |
| EBOOT · Dump EBOOT PSP, con cola excluida del mapa | `64937c521286fc8423076e644089881c5fe051bed2565e5061dda8aec0b45e10`; 1910384 bytes | game file or derived range |
| ISO · ISO MHFU ULES01213/1.01 | `5ebab623367e78c68033bb4b40e454b84ea974c4aa5e9819641232181d3f8139` | game file or derived range |
| DATA · Rango DATA.BIN MHFU | `4c65ae5c58f5b983321131391db0dce1d72ccd53b4cd28520429121333a82dec`; 772732928 bytes | game file or derived range |
| LMT_SET · Cuatro fuentes LMT67 | Miembros detallados debajo | set with constituent hashes, no aggregate invented |
| ↳ LMT_SET · common_entry_0084.lmt | `a4cf8054ebecebfa53f82bae923353b0e1221f2fc46242ee507e1bfe7df39fa9` | Miembro; no recurso adicional por duplicación |
| ↳ LMT_SET · common_entry_0085.lmt | `35fb4bd3efaba3fc321821c92258aebfc90bd93bb29385008f97631c839faf08` | Miembro; no recurso adicional por duplicación |
| ↳ LMT_SET · common_entry_0086.lmt | `ad1a8ae24be18ab64c4a857f0fbeec64c00b04c98a505f26ff230f2904f758ee` | Miembro; no recurso adicional por duplicación |
| ↳ LMT_SET · common_entry_0087.lmt | `2ef3c57d4075c57ff71805d3aa8cd6631f9e0c0dd54008b17e73596e9f5e1aae` | Miembro; no recurso adicional por duplicación |
| LMT_TRACK · Fuente de pista LMT seleccionada, slot8/track2 | `35fb4bd3efaba3fc321821c92258aebfc90bd93bb29385008f97631c839faf08` | parent LMT file; 8-byte track is a range within it |
| JKRA · rePatch/PCSG00350/dat/load/uc/uc00_001_03.bin | `4fcc62ad49f42b315d69013b2d312845b2d301dc97d47526047497f37125d385`; 238 bytes | game file or derived range |
| JKRA_OUT · Salida privada JKRA | `592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c`; 349 bytes | game file or derived range |
| JKRB · rePatch/PCSG00350/dat/load/uc/uc00_000_01.bin | `29d9e008ccd705a82185c3574f7e58327d6a77f4ccedb9ad89d5599c62fb2463`; 1058 bytes | game file or derived range |
| JKRB_OUT · Salida privada JKRB | `fa22ddcc947003496640007bd8f9cd5153e25b61a33b98e430bb1b4eb88352c8`; 1884 bytes | game file or derived range |
| MOD990 · MOD230 anterior sin huesos | `ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0`; 990 bytes | game file or derived range |
| TEX84 · TEX A6/ETC1A4 mínima | `0e5ae51392aa2a13b0800e41f2969b15a2b1b609ca9e0e1181bc3a07af110f52`; 84 bytes | game file or derived range |
| PSP_LOGS · Dos registros PPSSPP ya existentes | Miembros detallados debajo | set with constituent hashes |
| ↳ PSP_LOGS · ppsspp-probe-20261021 | `79a21291a537a17bf56e66c0e16a5f6eb2c4fa8a3f6aca56fd6dd4f50f6972de` | Miembro; no recurso adicional por duplicación |
| ↳ PSP_LOGS · ppsspp-decrypt-20261021 | `8b5b5c8fc8eb244a8779d1c8b1e714932c3320552b69203336870df5f2104a03` | Miembro; no recurso adicional por duplicación |
| PC_SNAPSHOT · Código sometido a la campaña106tests | Git `c4215e801bc14d5158321860a3afddeda790d561` | Git commit, not SHA256 |
| EMULATOR_SOURCES · Catálogo de fuentes de emuladores | `0cbfb286d8229b96a250a83601b1d83bb3416e7a9d5cf981f4876194f05027d2`; 15897 bytes | evidence document, not a game-set aggregate hash |
| CIA_SET · Cinco CIA físicas, cuatro hashes del recibo existente | Miembros detallados debajo | set with constituent hashes, not a new inventory |
| ↳ CIA_SET · Juegos\MH3U\EUR - Monster Hunter 3 Ultimate(00040000000b1d00).cia | `aa108914574a1a28b87e13964322441e2b619814a6d97401affce9f68ddcfd4f` | Miembro; no recurso adicional por duplicación |
| ↳ CIA_SET · Juegos\MHGU\MHXX_MHGU_English_Patch_v2.cia | `8438c0c026203c20b9dd81fc3b6ec9c31c94abc80e5bb7f6618cd58f804ac4ac` | Miembro; no recurso adicional por duplicación |
| ↳ CIA_SET · analysis-local\containers\MHXX\Monster Hunter XX  JPN (0004000000197100).cia | `195570856aa2cd623001d00aaa7c7e20d1e563fe8782979e054570ac83982245` | Miembro; no recurso adicional por duplicación |
| ↳ CIA_SET · analysis-local\containers\MH4U\EUR - Monster Hunter 4 Ultimate (0004000000126100).cia | `3b11095265bd96436306cbde7aa6256e7550164e83914d3ec9f8a139902e8069` | Miembro; no recurso adicional por duplicación |
| MHXX_NCCH · NCCH plaintext del update MHXX | `1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473`; 36868096 bytes | game file or derived range |
| MHXX_CODE_COMP · .code MHXX comprimido | `251399daef52a2a23bf77375a94ac4e6746bacb9b6d67e1b0654c82f57964f93`; 7419468 bytes | game file or derived range |
| MHXX_CODE_OUT · .code MHXX descomprimido privado | `6f66928e0deecdcd20c3b0e67c614e6313dfe92c8dc0b9ba2d7a906d1efe4fe8`; 13045760 bytes | game file or derived range |
| MH4U_NCSD · Base MH4U EUR NCSD/4GiB | `3832beef353d134bcba6ef83dc987e7ae228c43dc32a6ba52519f5f103f52581`; 4294967296 bytes | game file or derived range |
| MH4U_CODE_COMP · .code MH4U comprimido | `655e5b4f896d16ab1a745c3f516ef13c6cf482f3aa676b5c9927f3fa8ee57d83`; 9091360 bytes | game file or derived range |
| MH4U_CODE_OUT · .code MH4U descomprimido privado | `63940d7ef1fecc119f9fb820f5f6a2cf2f2a5549e4a70f00319fbd6c9c1ad8dc`; 16261120 bytes | game file or derived range |
| MOD3 · MOD230 de3huesos | `6d98d22019ceafc1c44801ed45692610ed5c0b2db461dc1fb813526c7af374be`; 26402 bytes | game file or derived range |

## Límites y uso del índice

- Los resultados negativos A22 y A29 no son errores a ocultar: documentan pérdida de alfa y falta de coherencia bajo un modelo fijado. No prueban corrupción de los juegos.
- Los bloqueos de independencia BLZ/LMT requieren evidencia nueva; no se reabren por repetir búsquedas, cambiar lenguaje o ejecutar otra traducción del mismo código.
- MOD990, jerarquía MOD3 y propiedad de matrices son aceptaciones distintas: el éxito estructural de una no corrige la geometría de otra.
- IA, hitboxes, movimiento funcional, colisiones, natación, audio/HUD/VFX/misiones completos y fidelidad en hardware no tienen una aceptación funcional positiva en este índice. Nombres/tipos documentales no los sustituyen.
- La coordinación registrada en coordination.md es histórica. Esta consolidación no envía mensajes a otros chats; resultados accesibles aquí y en PR7.
- Ninguna cifra de tests se suma como nueva suite ejecutada. Las campañas106/116/124 y los grupos de tests posteriores quedan fechados por sus propios recibos.
- No se modifican banco, originales, otras ramas, consola, firmware, plugins o montajes; sin FTP, nuevos ejecutables, juegos, claves o recursos comerciales publicados.

Para auditoría: abrir la aceptación concreta, su commit y JSON de evidencia; verificar la identidad del objeto correcto antes de cualquier nueva propuesta. El estado actual de un juego no se infiere del estado de un parser.

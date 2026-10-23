# Auditoría comparativa STT / MH4UltimateDC — 2026-10-24

## Dictamen y alcance

MH4UltimateDC es una referencia útil para diseñar verificación, contratos de CPU y separación entre código recompilado y plataforma. No demuestra que STT pueda ejecutar MH4U en PS Vita. La recompilación estática sustituye la ejecución de instrucciones, pero no elimina kernel, servicios, memoria virtual, GPU PICA200, DSP, temporización ni red de 3DS.

Se recomienda continuar el laboratorio PC de STT con pruebas sintéticas y contratos explícitos. No integrar todavía código de MH4UltimateDC. Una evaluación posterior de reutilización directa necesita decidir licencia de STT, inventariar dependencias y demostrar requisitos técnicos por separado. No se propone fusionar ramas experimentales ni migrar el proyecto a otro runtime.

Esta auditoría inspeccionó fuentes públicas mediante el conector GitHub. El intento de clonación por Git falló por resolución de red; se usaron árboles y archivos fijados por SHA. La recuperación del chat anterior solo devolvió referencias opacas para varias respuestas: no se atribuyen detalles inexistentes a aquella aprobación. La solicitud actual define el alcance.

## Cómo leer la evidencia

- **E**: código, configuración o metadato público inspeccionado en el SHA indicado.
- **R**: resultado reportado por el mantenedor o sus documentos; no reproducido en esta sesión.
- **L**: prueba ejecutada localmente en esta sesión.
- **H**: hipótesis o trabajo propuesto, todavía sin demostración.

Un workflow correcto es evidencia de sus pasos y entorno, no de ejecución física en Vita ni de juego completo. Las cifras de cobertura del autor no se convierten en cobertura de STT.

## Instantánea verificable

| Repositorio / rama | Commit inspeccionado | Situación |
|---|---|---|
| [STT main](https://github.com/EMCY3233/STT-Monster-Hunter-Project/tree/f199bd07b4e05ee4f7e56ed616840518374f3300) | `f199bd07b4e05ee4f7e56ed616840518374f3300` | Base del monitor; README declara ausencia de juego nativo demostrado |
| [STT PR #45](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/45), feat/arm-cpp-leaf-proof | `d91eb729647cea45dbd099a3fd03e4bded75796d` | Abierta, sin fusionar; experimento A32 → C++17 |
| [STT PR #48](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/48), test/a32-decoder-contract-20261023 | `0c65b13b98bd3bb52c454fa3df0587cb0d0e44db` | Abierta, basada en #45; contrato del decoder |
| [MH4UltimateDC main](https://github.com/CompaLarios18/MH4UltimateDC/tree/e06b0ca30b9b2d66ec7785f277ead4bb35374b28) | `e06b0ca30b9b2d66ec7785f277ead4bb35374b28` | Port que usa Azahar como plataforma |
| [MH4UltimateDC native](https://github.com/CompaLarios18/MH4UltimateDC/tree/a6b71de1221e895312273d0378b7a2e8513955fa) | `a6b71de1221e895312273d0378b7a2e8513955fa` | Runtime propio en desarrollo; no equivale a main ni a paridad completa |

E: se enumeraron 62 ramas STT y 12 MH4UltimateDC, y 48/34 PR respectivamente en las colecciones devueltas. La colección de PR STT incluye #37 cerrada sin fusión y muchas cadenas abiertas; el número máximo de PR no es un conteo de PR. El inventario completo es un entregable local del autor; no está incluido en esta PR y no se considera evidencia reproducida por el revisor.

E: [AGENTS.md STT](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/f199bd07b4e05ee4f7e56ed616840518374f3300/AGENTS.md) exige distinguir automatización, receptor PC y confirmación física. También limita limpieza y transferencias: esta tarea documental no justifica reinstalar ni acceder a Vita. Se comprobó el AGENTS de #45; no apareció otro AGENTS anidado en los árboles STT inspeccionados.

E: [README principal](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/f199bd07b4e05ee4f7e56ed616840518374f3300/README.md), [área 01](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/f199bd07b4e05ee4f7e56ed616840518374f3300/docs/areas/01.md) y changelog maestro describen monitor y planificación; no certifican juego ejecutándose. La dirección más reciente del laboratorio está en [README #45](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/d91eb729647cea45dbd099a3fd03e4bded75796d/arm-leaf-lab/README.md): ejecutar programa original en PC, con la arena original de #44 conservada como experimento independiente. Es una diferencia de alcance entre ramas, no un cambio ya integrado en main.

E: #36 estudia núcleo PC; #39–43 son lectores/inspectores; #44 es arena original. #45 no se confunde con esas vías. #47 modifica simulador/tests del agente y #48 el decoder. La auditoría usa una rama documental nueva desde main y un archivo nuevo; no toca esas ramas ni sus archivos. No se accedió a sesiones privadas de Claude Code/OpenCode ni se enviaron mensajes a otros chats.

## CI comprobada en los commits

E remota: consultas del autor al servicio GitHub el 24/10/2026 (Europe/Madrid). Claude no reprodujo las consultas de runs/jobs ni sus logs; su revisión no constituye una segunda comprobación de CI.

| SHA / pista | Resultado remoto inspeccionado |
|---|---|
| STT main | [Monitor tests 40026934817](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/40026934817) y [Vita agent build 40026934745](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/40026934745): success |
| STT #45 | [A32 39888706214](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39888706214): success; workflow Windows/Linux, Debug/Release, Python 3.12, Unicorn 2.1.4 |
| STT #48 | [A32 40027763196](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/40027763196): success; monitor y Vita también success en las ejecuciones consultadas |
| MH main | [CI 39727281434](https://github.com/CompaLarios18/MH4UltimateDC/actions/runs/39727281434), guard y builds Linux/Windows/macOS: success |
| MH native | [Native CI 39957947779](https://github.com/CompaLarios18/MH4UltimateDC/actions/runs/39957947779) y [guard 39957947632](https://github.com/CompaLarios18/MH4UltimateDC/actions/runs/39957947632): success |
| MH native app | [Native app CI 39957947693](https://github.com/CompaLarios18/MH4UltimateDC/actions/runs/39957947693): failure; Linux success, Windows/macOS fallan en Test |

E: logs Windows, job 120431755239: app_report_test falla (3 casos); procesos hijos muestran error de sintaxis de nombre/ruta, faltan archivos de crash y el cierre esperado devuelve 1. Logs macOS, job 120431755419: app_audio_test falla, requisito steered.size() > 1000 recibe 986. Ambos registran 56/57 tests CTest correctos. Esto localiza los fallos, pero no demuestra su causa definitiva ni que sean inocuos. No se reejecutó ni corrigió CI ajena.

E: Monitor tests STT cubre Windows/Ubuntu y Python 3.11/3.13, unittest y tres smoke tests. La CI Vita compila; no valida hardware por sí misma. Esta PR documental no añade workflow ni recompila para transferir.

## Matriz técnica de reutilización

Las referencias MH siguientes están fijadas a main salvo que se indique native.

| Componente y evidencia | STT actual | Reutilización evaluada | Incompatibilidad / prueba exigida |
|---|---|---|---|
| [Decoder ARM](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/tools/recomp/arm.py), [Thumb](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/tools/recomp/thumb.py), [pipeline](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/docs/RECOMPILER.md) (E) | #45: nueve operaciones enteras no-S incondicionales, R0–R12, inmediatos rotados o registros sin shift; termina BX LR | Método de expansión gradual y rechazo explícito: útil. Copiar implementación: aplazado por licencia | No hay memoria, llamadas, ramas, instrucciones Thumb de entrada, VFP ni SVC en STT. Compartir familia ARM no resuelve esos huecos |
| [Emisor](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/tools/recomp/emit.py), análisis de CFG y llamadas indirectas (E) | Fragmentos de 1–65 instrucciones; sin descubrimiento de funciones | Separar descubrimiento, decode, análisis y emisión es aplicable como diseño | Límites de función, destinos indirectos, tablas, relocalización y ARM↔Thumb requieren pruebas originales específicas; no inferir alcance desde bytes aceptados |
| [recomp.h](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/tools/recomp/runtime/recomp.h) (E) | ArmState con registros/CPSR en C++17 | Contrato explícito de estado, callbacks y memoria: referencia de diseño | RCtx incluye VFP, TLS, monitor exclusivo y presupuesto. ABI, tamaños/alineamiento, aliasing y FPU deben verificarse en cada host |
| [ARM_Recomp](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/port/src/arm_recomp.h), [CMake](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/port/CMakeLists.txt) (E) | No plataforma 3DS ejecutable demostrada | Arquitectura CPU/plataforma separada: útil; backend no es componente autónomo para Vita | Hereda ARM_Interface, usa tablas de páginas y SVC Azahar y enlaza citra_core/citra_common/network. Sustituir CPU no sustituye plataforma |
| [Hooks](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/port/src/hooks.cpp) y RCodeInfo.set_hook (E) | Sin ABI de hooks equivalente en el laboratorio | Patrón envolver original/antes/después y validar cambios: útil | hooks.cpp incluye core/video_core/common; direcciones y comportamiento dependen de versión del juego. No portar hooks de FPS/HUD como parche universal |
| [difftest.py](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/tools/difftest.py) (E) | #45 compara C++ nativo con Unicorn sobre sintéticos | Semillas, estados idénticos y comparación de efectos: alta utilidad metodológica | difftest compila candidato a ARMv6K y ejecuta original/candidato en Unicorn; no es lo mismo que probar C nativo en host. Usa LLVM y entradas privadas |
| [Fuzz/gametest](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/docs/RECOMPILER.md) (E/R) | 21 fixtures/5376 estados documentados en #45; contrato adicional #48 | Registrar retorno, fallo, timeout e inconcluso separados; medir casos efectivos | La sección Verification, nivel 3 y Latest full run, de RECOMPILER.md reporta muchos fallos coincidentes y presupuestos agotados. Fallar igual con punteros aleatorios no prueba gameplay ni cobertura semántica |
| [Fibers](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/port/src/fiber.h) (E) | Sin scheduler de juego demostrado | Suspensión cooperativa y contrato de yield merecen estudio | Stack por fiber por defecto 8 MiB; no multiplicarlo sin medir. Backend de contexto, memoria y API de Vita no comprobados |
| [native](https://github.com/CompaLarios18/MH4UltimateDC/blob/a6b71de1221e895312273d0378b7a2e8513955fa/docs/native/README.md), [dependencias](https://github.com/CompaLarios18/MH4UltimateDC/blob/a6b71de1221e895312273d0378b7a2e8513955fa/tools/native/check_native_deps.py) (E) | Laboratorio PC independiente | Contratos de servicios y pruebas de conformidad son referencia; no integración ahora | Guard evita includes/enlaces Azahar, pero admite funciones individuales con procedencia. No significa ausencia total de código derivado de Azahar ni cambio de licencia |
| [native CMake](https://github.com/CompaLarios18/MH4UltimateDC/blob/a6b71de1221e895312273d0378b7a2e8513955fa/native/CMakeLists.txt) y estado GPU/audio (E/R) | Laboratorio C++17; prototipos Vita separados | Separar runner headless, app, GPU y audio es útil | native usa C++20/C11 y app SDL3; main app SDL2. El renderer PICA200 no se reemplaza automáticamente por renderer STT ni por compatibilidad ARM |
| [LEGAL](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/docs/LEGAL.md), [CONTRIBUTING](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/CONTRIBUTING.md) (E) | Sin LICENSE/COPYING encontrado en árbol main STT | Adoptar límites de datos y procedencia con redacción original | No asumir licencia de STT por ser público. No importar código/docs ajenos hasta decidir compatibilidad y obligaciones |

## Qué demuestra realmente native

E: native define runtime sin enlazar módulos Azahar y conserva main como port publicado hasta paridad. R: [STATUS](https://github.com/CompaLarios18/MH4UltimateDC/blob/a6b71de1221e895312273d0378b7a2e8513955fa/docs/native/STATUS.md) marca N1-21 done: G1/G2 headless en PC del mantenedor, comparadores bajo perfil native, con tolerancias documentadas y diferencias temporales; no es repetibilidad exacta por frame.

E/R: el mismo STATUS mantiene N1-26 (cacería G3 headless) todo, N2b-09 (cargar/ejecutar/presentar) todo y N2b-12 (renderer como GPU del runtime) todo. N0-30 está blocked; N0-35 review con comprobaciones privadas pendientes; N2-01 review pendiente de decisión y medición Mac. No se debe convertir una PR fusionada en prueba de que todos sus paquetes están verificados con juego.

R: main README anuncia aldea/misiones/cacerías, sonido y 60/120 FPS en Windows. No se ejecutó el juego aquí. Documentos como PORT_ARCHITECTURE conservan hitos anteriores a esos anuncios; se leen junto al código/README/STATUS y no como cronología única actualizada. Tampoco se extrapola el rendimiento anunciado a Vita.

## PS Vita: bloqueos y preguntas abiertas

**E + inferencia técnica:** main depende de Azahar y APIs de host; native exige otra plataforma de kernel/servicios/memoria/GPU/audio. Tener instrucciones ARM en ambos dispositivos no da compatibilidad binaria ni implementa servicios 3DS. El pipeline genera C y el compilador produce código para un host: tampoco eso garantiza recursos, ABI ni rendimiento suficientes.

**H, sin medición Vita:** coste de traducir cargas/almacenamientos paginados, fibers, pilas, dispatch indirecto, sincronización GPU, DSP y shaders; tamaño final de código y presión de memoria. No se dan FPS, RAM disponible ni presupuestos inventados. Se necesitan medidas de pico de memoria, tamaño, latencias p50/p95/p99 y estabilidad antes de cualquier conclusión.

**H:** un backend gráfico específico y adaptación de servicios podrían investigarse. No son tareas de recompilar sin cambios y no se afirma que sean realizables dentro de los límites de Vita. Primero deben funcionar contratos sintéticos y un runtime PC acotado. No se ha consultado, instalado ni cambiado Vita, FTP, firmware, plugins ni firewall en esta auditoría.

## Licencia y límites de publicación

E: [README MH](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/README.md) declara GPL-3.0-or-later para herramientas, port y documentación; [LICENSE](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/LICENSE) contiene GPLv3. La separación main/native no elimina esa licencia. Una eventual incorporación exige registrar procedencia, avisos/licencia, modificaciones, dependencias y obligaciones de entrega de fuente correspondiente según cómo se distribuya el conjunto. El análisis técnico no determina por sí solo compatibilidad jurídica con un STT todavía sin licencia declarada.

La referencia de diseño no autoriza trasladar implementación, estructura expresiva o nombres específicos de hooks.cpp, difftest.py o recomp.h a STT. Una eventual implementación independiente necesita requisitos y fixtures originales y procedencia registrada; esta auditoría no certifica un proceso clean-room.

No se copió implementación ni texto sustancial de MH al repositorio STT. Este informe es análisis original con enlaces. Las fuentes STT descargadas para repetir pruebas quedan en el área local de trabajo, fuera de los cambios propuestos. No se distribuye código recompilado del juego, binarios, ROMs, keys, dumps, assets, trazas privadas ni capturas comerciales.

LEGAL prohíbe incluso pequeños extractos, mientras CONTRIBUTING admite algunas instrucciones breves en notas: hay una ambigüedad documental. Para esta tarea se aplica el límite más estricto solicitado por el usuario: ningún byte comercial. La GPL del tooling no concede derechos sobre el juego. No se abrieron issues ni se contactó con el proyecto externo.

## Plan de pruebas por puertas

| Puerta | Prueba sintética / criterio de aceptación | Evidencia que todavía no aporta |
|---|---|---|
| P0: procedencia y alcance | Fijar SHA/versión, licencia de cada dependencia y fixtures originales; ninguna entrada comercial en Git | No certifica titularidad de un dump |
| P1: decoder #48 | Repetir cinco tests, incluyendo 4096 inmediatos rotados, condición/opcode, registros, rechazo de los 255 campos de shift no nulos y límites; cero fallos | No ejecuta C++ ni certifica toda A32 |
| P2: semántica #45 | CMake/CTest Windows/Linux Debug/Release, Unicorn fijado, 21 fixtures/5376 estados por configuración; comparar registros/CPSR/PC; rechazos sin mutación | No demuestra identidad de función ni juego |
| P3: memoria/ABI | Añadir casos originales con bordes de página, alineación, acceso inválido, endian, ABI/stack y wrap; fallo explícito y reproducible; sanitizadores del host | No habilitar automáticamente nuevas instrucciones |
| P4: control/FP | Ramas, llamadas, retorno ARM↔Thumb, flags, exclusivas, TLS y VFP por familias; NaN/denormal/redondeo; discrepancias del oráculo documentadas | Una familia correcta no valida scheduler/servicios |
| P5: plataforma PC | Programa 3DS sintético propio con hilos, SVC, IPC, FS temporal aislado, HID y presupuesto; trazas esperadas, cero servicios ocultamente omitidos | No equivale a boot de MH4U |
| P6: GPU/DSP | Buffers originales, transferencias, formatos, comandos y audio generado; comparar bytes y muestras, latencia y carreras; corrupción inyectada debe fallar | Un build verde no prueba sonido/imagen reales |
| P7: integración privada autorizada | Solo en una tarea posterior: usuario aporta su propio juego; resultados agregados sin datos derivados, escenarios/criterios fijados antes; faltantes nunca cuentan como pass | No se ejecutó en esta auditoría |
| P8: estudio Vita | Solo tras autorización futura específica y puertas previas: primero cross-build y pruebas de portabilidad; hardware y presupuestos medidos en tarea separada | Ninguna promesa actual de port viable |

Los comparadores deben fallar o marcar inconcluso cuando no comparan nada; conservar perfiles estrictos y documentar cada tolerancia. Una máscara de bytes variables no se añade para ocultar una discrepancia. Mantener baseline y candidato, semilla, entorno, casos comparados/rechazados/agotados y motivo.

## Pruebas realizadas aquí

L: Python 3.12.14 en Windows. Se recuperaron translate.py del SHA #45 y test_decoder.py del SHA #48, sin modificarlos. Comando:

```text
python -m unittest discover -s work/stt-source/arm-leaf-lab -p test_decoder.py -v
```

Resultado: cinco tests correctos, 0.013 s; salida de proceso 0. Se comprobó el contrato de decodificación, sin entradas comerciales.

No se ejecutaron C++/Unicorn, suites completas MH, juego, benchmarks ni pruebas de hardware. CMake y compilador C++ no se encontraron en PATH. Las pruebas de ejecución nativa citadas son CI remota, no locales. No se agregan tests duplicados: #48 ya cubre el contrato sintético relevante. La propuesta cambia únicamente esta documentación.

## Revisión independiente de Claude

R: Claude comunicó por el buzón compartido (evento 7, tarea 2) una revisión de solo lectura del commit b3fdcb499e447faad332c67594d74ec776c4347d: aprobable como documentación, sin errores de fondo y con matices menores. Confirmó límites del decoder, composición #45/#48, cifras de fixtures, licencia declarada, separación main/native y algunos estados de STATUS. No comprobó AGENTS, N2b-09, N2b-12, N2-01 ni los runs/logs de CI; no se atribuye revisión total a su dictamen.

R de ejecución independiente: el evento 8 complementa y sustituye la limitación inicial del evento 7 sobre tests. Claude informa que ejecutó test_decoder.py de #48 (0c65b13), extraído mediante git archive fuera de un checkout, con Python 3.13.17 en Linux: cinco tests OK en 0.030 s. Comando: `python3 -m unittest discover -s . -p test_decoder.py -v`. Coincide con la ejecución local Windows descrita arriba. Codex leyó el mensaje, pero no ejecutó ni observó el proceso Linux; es evidencia atribuida a Claude. No se ejecutaron C++, CMake ni Unicorn ni se modificó el repositorio durante su revisión.

Los matices sobre inventario local, atribución de CI, rechazo de shifts y referencia a Verification se incorporan en esta revisión documental. Se mantienen las restricciones de licencia y ausencia de prueba de viabilidad Vita.

## Próximo paso recomendado

Revisar este dictamen y las PR #45/#48 por separado, sin fusionarlas automáticamente. Elegir licencia de STT antes de importar código. Después ampliar una sola familia semántica con fixtures originales y puerta P2/P3, manteniendo renderer, lectores y monitor en sus ramas independientes. La existencia de MH4UltimateDC reduce incertidumbre de diseño; no elimina la incertidumbre de implementación ni de hardware.

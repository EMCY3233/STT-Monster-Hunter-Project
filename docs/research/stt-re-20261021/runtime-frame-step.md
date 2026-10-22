# Contadores contrastados con avance individual — 22-10-2026

> Seguimiento: [accesos estáticos candidatos y contraste de código](runtime-static-accesses.md).

## Resultado comprobado

En la escena local de MH4U en Val Habar, los campos u32 little endian `0x0110D004` y `0x0110D008` aumentaron **exactamente una unidad por cada una de tres solicitudes individuales de Avanzar Fotograma de Citra**. Permanecieron estables durante veinte lecturas posteriores a cada solicitud. Esto refuerza y concreta la interpretación anterior de contador periódico: **contadores que siguen el avance de fotogramas del emulador en el ensayo realizado**.

No se identificó la instrucción que escribe estos campos, no se estableció qué función cumple cada uno y no se certificó equivalencia universal con frames de lógica, render del juego, animación o VBlank en otras escenas. Un contador de otro subsistema con igual cadencia también podría producir el resultado. La identidad concreta continúa como hipótesis.

| Transición | Acción observada | Delta +4 | Delta +8 |
| --- | --- | ---: | ---: |
| Baseline → 1 | Intento UIA con menú cerrado: timeout | 0 | 0 |
| 1 → 2 | Selección visible Avanzar Fotograma | 1 | 1 |
| 2 → 3 | Segunda selección visible | 1 | 1 |
| 3 → 4 | Tercera selección visible | 1 | 1 |

Las cinco capturas de dos segundos reunieron 100 lecturas válidas de 32 bytes, diez controles de código coincidentes y cero errores RPC: 3200 bytes de muestras, privados. Todos los bloques de 32 bytes fueron estables dentro de cada captura. No se atribuye avance al intento de accesibilidad fallido. Las acciones visibles se registraron con hora UTC; las capturas se tomaron después de cada acción, no se presentan como una traza atómica del instante de escritura.

## Procedimiento reproducible

1. Con MH4U abierto, Herramientas → Avanzar Fotograma → Activar Avance de Fotogramas. Comprobar la marca en el menú y estabilidad de las lecturas. El atajo para avanzar no está asignado en este perfil; no se cambió el mapeo.
2. Registrar veinte muestras del rango verificado `0x0110D000` con `record_citra_target.py --seconds 2 --interval 0.1` y los mismos parámetros de mapa/imagen/BSS ya documentados.
3. Abrir el submenú y seleccionar Avanzar Fotograma una sola vez. Registrar otra captura. Repetir, observando de nuevo el menú antes de cada acción.
4. Ejecutar `compare_citra_frame_steps.py --captures <baseline> <intento fallido> <paso1> <paso2> <paso3> --expected 0 1 1 1`. La herramienta valida cada captura mediante el lector de hashes existente, exige muestras estables y compara diferencias modulares u32. La secuencia esperada proviene de las acciones documentadas, no de una deducción automática.
5. Desmarcar Activar Avance de Fotogramas y verificar ejecución continua. Se restauraron 100 % y 60 FPS al terminar; sin teclas retenidas, cambios de controles ni lectores activos.

Cuatro pruebas nuevas cubren transición sin entrada, incremento con desbordamiento u32, desacuerdo con la secuencia esperada, rechazo de bloques inestables y número de acciones inválido. No se repiten pruebas históricas como nuevas aceptaciones.

## Código exacto del emulador revisado

Revisión `0ff3440232d6bc9226e37c41c05c5aead03f37fd`. [main.cpp](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/citra_qt/main.cpp), líneas 945–955, conecta las opciones del menú con SetFrameAdvancing y AdvanceFrame. [main.ui](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/citra_qt/main.ui) sitúa ambas en Herramientas. [perf_stats.cpp](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/perf_stats.cpp), líneas 128–141 y 174–188, espera/restablece un evento y lo señala al avanzar. [renderer_base.cpp](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/video_core/renderer_base.cpp), líneas 43–51, aplica el limitador en EndFrame. [gpu.cpp](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/video_core/gpu.cpp), líneas 409–418, presenta el frame desde VBlankCallback. Estos hechos explican la herramienta de control; no identifican por sí mismos variables internas de MH4U.

## Siguiente límite a resolver

La prueba permite contar incrementos relativos sin depender de demoras del host. Para relacionarlos con acciones, animaciones y posición falta localizar las escrituras o estructuras correspondientes. El bloque BSS vecino no dio candidatos específicos de posición en el ensayo anterior. No se seguirá un valor como puntero sólo por parecer una dirección; se necesita demostrar rango asignado y tamaño. No se leyó VRAM, no se modificó memoria del juego y no se publicaron bytes comerciales.

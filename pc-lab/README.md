# STT PC Lab — núcleo C++ original

Objetivo actualizado por el usuario: PC, Windows y Linux; siguiente fase con
escena 3D original. Este primer módulo es una simulación de consola, sin gráficos,
sin emulación y sin ejecución de Monster Hunter 4 Ultimate.

## Compilar y comprobar

Requiere CMake >=3.16 y compilador C++17 (MSVC, GCC o Clang). No descarga
dependencias. Desde la raíz del repositorio:

```text
cmake -S pc-lab -B build/pc-lab -DCMAKE_BUILD_TYPE=Release
cmake --build build/pc-lab --config Release
ctest --test-dir build/pc-lab -C Release --output-on-failure
```

Ejecutable: `build/pc-lab/stt_pc_demo` con generadores de una configuración;
`build/pc-lab/Release/stt_pc_demo.exe` con Visual Studio.

El ensayo finito de 600 pasos debe terminar con:

```text
tick=600 x_mm=500 z_mm=0 hp=0 hits=4
```

## Contrato experimental

- Un `step` aceptado avanza exactamente 1/60 s de tiempo simulado. El llamante
  futuro gestionará reloj, acumulador, pausa y presupuesto de recuperación;
  el módulo no mide FPS ni garantiza ejecución en tiempo real.
- Coordenadas enteras en milímetros, X/Z, límites inclusivos de +/-5000 mm.
  Entrada por eje en {-1,0,1}; cualquier valor inválido rechaza el paso entero.
  Avance axial 50 mm, diagonal 35 mm por eje para no aumentar la velocidad.
- Objetivo fijo en (1000,0), 100 HP; rango circular inclusivo de 750 mm,
  daño 25 y enfriamiento de 30 pasos. Movimiento antes del ataque; enfriamiento
  decrece al empezar el paso. Solo flanco de pulsación, sin cola de ataques.
- Una entrada rechazada tampoco altera el estado del botón. Reset limpia todo.
  Se rechaza el avance al agotar el contador de 64 bits; no se permite cargar
  estado externo. No hay asignaciones dinámicas ni E/S en el núcleo.
- No hay invulnerabilidad, combos, cámara, mallas, archivos comerciales,
  persistencia, red, recompensas ni fidelidad a reglas o parámetros de MH4U.

Los tests permanecen activos en Release: no dependen de `assert`. Comprueban
límites, entradas extremas, radio inclusivo, pulsación sostenida, enfriamiento,
objetivo agotado, reset y reproducción de 100.000 pasos. La demostración prueba
además cuatro impactos separados exactamente por 30 pasos.

## Procedencia y licencia

Código escrito originalmente para este estudio, sin código ni activos de las
referencias. No se ha encontrado LICENSE en la raíz de STT en la base auditada;
el titular debe elegir la licencia de distribución antes de declarar este
proyecto open source. No se añade una licencia global por inferencia.

Evaluación, decisiones pendientes y límites: [informe](../docs/research/pc-cpp-feasibility-20261022.md).

# STT Combat Lab 0.1 — núcleo original

Rama independiente desde `410b1dd70a3713b500a829aed55cb99cb74ad1d0`. Responsabilidad: `combat-lab/`, este documento y su workflow PC. No incorpora las investigaciones PR #3/#7, formatos ni recursos comerciales. El movimiento de espada es una mecánica experimental propia, sin atribuir fidelidad a Monster Hunter.

## Ejecutar

Sin dependencias externas, C99 y biblioteca estándar:

```sh
cc -std=c99 -Wall -Wextra -Werror -pedantic -Icombat-lab/include combat-lab/src/stt_combat.c combat-lab/src/demo.c -o /tmp/stt-combat-demo
/tmp/stt-combat-demo
cc -std=c99 -Wall -Wextra -Werror -pedantic -Icombat-lab/include combat-lab/src/stt_combat.c combat-lab/tests/test_combat.c -o /tmp/stt-combat-test
/tmp/stt-combat-test
```

También: `cmake -S combat-lab -B build/combat`, `cmake --build build/combat`, `ctest --test-dir build/combat --output-on-failure`. En Visual Studio añadir `--config Release` y `-C Release`. El demo ejecuta una cadena sintética y muestra impactos en ticks 10/40/76, daños 10/14/22 y vida final 54. No es una aplicación gráfica. A enlaza exactamente la misma fuente C, sin red ni adaptador que reimplemente el combate.

## Contrato C v0.1

`include/stt_combat.h` es la interfaz sin ABI binaria prometida. `init` reinicia sesión/objetivo; `step` avanza exactamente un tick de 1/60 s. El anfitrión controla acumulador y suspensión: no debe recuperar tiempo suspendido con miles de ticks. La función no asigna memoria, usa E/S, reloj ni floats; una entrada idéntica produce estado idéntico en las plataformas C99 soportadas. Reproducción significa misma versión del núcleo y mismos comandos por tick. No serializar la memoria cruda ni sus rellenos; usar los contratos versionados de telemetría para observación.

Unidades de posición y entrada: milímetros enteros. Ejes +X derecha, +Y arriba, +Z delante, suelo Y=0. Yaw `uint16_t`: 65536 unidades/vuelta, cero +Z, positivo hacia +X. El hitbox cuantiza el rumbo a 64 sectores, sin trigonometría de plataforma. Para telemetría en miligrados: `yaw * 360000 / 65536` con aritmética de al menos 64 bits, truncado. Vida y daño son puntos enteros, no valores de ningún juego.

`move_x_mm/move_z_mm` son desplazamientos mundiales por tick, cada componente limitado a ±100 mm y arena ±100000 mm; el anfitrión normaliza el stick y aplica movimiento relativo a cámara antes de llamar. El núcleo limita componentes, no normaliza diagonales: cota de velocidad diagonal 141.5 mm/tick, axial 100. El prototipo puede elegir una velocidad inferior. La posición y yaw se actualizan solo en idle: el ataque fija ubicación y orientación al comienzo. `attack_pressed` debe ser un flanco de pulsación, no el botón mantenido. Los punteros nulos se ignoran. Estados/combo internos inválidos recuperan idle; no se admite importar arbitrariamente el estado interno.

| Golpe original | Preparación | Activo | Recuperación | Daño |
|---|---:|---:|---:|---:|
| 1 | 8 ticks | 4 ticks | 16 ticks | 10 |
| 2 | 10 ticks | 4 ticks | 18 ticks | 14 |
| 3 | 14 ticks | 6 ticks | 24 ticks | 22 |

La pulsación en idle inicia preparación con fase cero y aumenta `attack_id`; ese tick de entrada no cuenta como tick de preparación. En cada `step` posterior se procesa el estado actual y se incrementa fase. El primer test de impacto ocurre en el primer tick que empieza en activo, después de completar preparación. Se acepta una pulsación en las últimas ocho fases de recuperación: [8,16) para golpe 1 y [10,18) para golpe 2. Queda un único buffer; al terminar recuperación empieza siguiente golpe. No hay encadenamiento después del tercero. Las pulsaciones fuera de esas ventanas se descartan. Sin esquiva, guardia, daño al cazador ni sistema de heridas todavía.

## Hitbox y objetivo

La espada usa en el suelo un círculo de radio 700 mm centrado 900 mm delante del cazador; el objetivo es un círculo de radio 300 mm. Se impacta cuando distancia al centro ≤1000 mm, solo durante activo. No se afirma barrido continuo, cápsula exacta de hoja ni colisión vertical. Un límite previo evita desbordamientos al evaluar posiciones externas extremas. Objetivo inicial `(0,0,1800)`, id 1, vida 100; reacción de 12 ticks al impacto, decrementada al principio de los siguientes ticks. No hay movimiento de reacción todavía; el renderer puede expresar ese estado con color. Vida nunca baja de cero.

`hit_latched` garantiza un solo impacto por ejecución/objetivo durante todos los ticks activos. Este primer corte admite un único objetivo estable por sesión: no cambiar identidad a mitad de ataque. La salida `impacts[1]` y `impact_count` se limpian lógicamente cada tick; solo leer elementos bajo el contador. El impacto contiene ataque, objetivo, tick y daño. Ataque usa contador uint32 que vuelve de UINT32_MAX a 1, reservando cero; sesión + tick + ataque permiten distinguir ejecución en telemetría. Objetivos muertos no reciben impactos. Reiniciar con `init` crea otra sesión en el anfitrión.

## Validación y límites de evidencia

21-10-2026: GCC 13.3.0 Linux compiló con C99, warnings tratados como errores y ASan/UBSan. Suite: controles acotados, rumbos, fases exactas, límites exactos de buffer 7/8/15, buffer temprano rechazado, combo de tres, deduplicación, fallo por orientación, borde inclusivo 1900 mm / exclusión 1901 mm, objetivo muerto, saturación de vida, expiración de reacción, estado inválido, rollover de ID sin cero, entradas extremas y reproducción idéntica de 10000 ticks. Resultado correcto; demo mostró ticks 10/40/76 y vida 54.

LeakSanitizer no pudo inspeccionar `/proc` bajo el entorno instrumentado; se repitió con `ASAN_OPTIONS=detect_leaks=0`, con ASan y UBSan activos. Núcleo sin asignaciones dinámicas. CMake no estaba instalado localmente; se proporciona CI Windows/Linux separada de la compilación Vita y su resultado debe verificarse por SHA, sin atribuirle éxito anticipado.

SHA-256 de ejecutables locales de esa compilación (no portables entre compiladores/rutas y no son VPK): demo `80a2a49e50931852aa19d7a9f369eee0f1568cfd5e599dff75d1842ed447531a`; test ASan/UBSan `0c70e0202a8d01e4817392c2fe8ac97b1e1a2630acffaca4e7cde9cfaa1519dd`.

No se ha probado recepción PC de telemetría desde Vita, instalación, interacción física ni rendimiento en PS Vita. Dependencias de integración: PR A (renderer, controles y VPK), PR contratos (telemetría/HUD y reserva acuática); B Asset Lab permanece desacoplado. Enlaces concretos se añadirán al publicar las PR. Pendiente: más objetivos, colisión 3D, golpes recibidos, propiedades de progresión y revisión de equilibrio con hardware.


Revisión de portabilidad posterior: el primer build Vita GCC15 falló con `-Werror=type-limits` porque el enum de estados tiene representación sin signo; comparar con `< STT_IDLE` era siempre falso. Se sustituyó por comparación tras convertir a unsigned, conservando rechazo de estados negativos y superiores al máximo. Se añadieron caso -1 y compilación/prueba local `-fshort-enums` para reproducir enum sin signo; ambas variantes GCC13 pasan sin desactivar advertencias. CI añade esa variante. Build Vita debe repetirse sobre la corrección: este resultado PC no acredita aún el VPK. SHA-256 de `combat-lab/src/stt_combat.c` corregido: `dd50b4cf64ee0737c1f1cb9eebfc2d1ff9f47b5aedf1ec8b8ac0eb5fa726fbda`.

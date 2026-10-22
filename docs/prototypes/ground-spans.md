# STT 0.17 — suelo por tramos

La captura física de0.16 identifica el suelo como principal coste. Esta versión conserva los modos anteriores y añade G2: el plano se recorre por tramos de píxeles pertenecientes a una misma celda. No se afirma ganancia física antes de medirla.

## Comparación

Predeterminado G2/T1. L recorre G2→G0→G1→G2. G0 conserva triángulos, G1 el suelo por píxel de0.15/0.16 y G2 el nuevo suelo por tramos. R sigue alternando T0/T1 para personaje, arma y objetivo. Para aislar el cambio de suelo mantener T1 y comparar30sG2 con30sG1 usando la misma vista y acciones. Select inicia la captura de180segundos.

## Implementación

Para cada fila se conserva la misma intersección con el plano y su profundidad inversa. Se recorta el intervalo de píxeles al mismo rectángulo de16×16celdas mediante búsqueda monótona. Para cada tramo se calcula el próximo cruce de una celda en X o Z, se verifica contra la fórmula de coordenadas del modoG1 y, si el redondeo en frontera lo exige, se resuelve mediante búsqueda binaria. Dentro de un tramo solo se escriben color y profundidad constantes.

Se mantienen las celdas negativas, los límites exclusivos, el manejo de ejes constantes y el cálculo de color/profundidad del modo anterior. La profundidad no se elimina: debe seguir ocultando correctamente el personaje, el arma y el objetivo.

## Contrato y verificación

STT/6 conserva los campos de fases deSTT/5 y amplía `ground_mode` con2. El receptor mantieneSTT/1–5; STT/5 continúa rechazandoG2 para no reinterpretar silenciosamente su contrato anterior. Análisis separado por sesión/G/T y descarte de ventanas incompletas al alternar.

La prueba C compara las imágenes completas, incluido padding, y profundidad inversa bit a bit contraG1 en120cámaras/posiciones:15.667.200píxeles, ejes próximos a cero, giro, diferentes alturas de cámara y coordenadas negativas y próximas a los límites de la arena. Se mantienen todas las pruebas de raster, canarios, fases, corrupción y combate. Python comprueba el nuevo enum y lectura de versiones anteriores.

No modifica frecuencias, firmware, plugins ni recursos comerciales. IdentidadSTTP00001/00.17. Ganancia de FPS y validación visual en pantalla pendientes de captura física.

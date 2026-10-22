# Techo de prueba — 00.20

Arriba en la cruceta alterna **C0 apagado → C1 referencia por píxel → C2 optimizado por franjas → C0**. El techo empieza apagado para conservar la comparación anterior. Color violeta, altura 8 m; área 32 × 32 m centrada en el cazador, igual al suelo. Mira hacia arriba para verlo. El máximo de altura de cámara queda por debajo del techo; este plano no incorpora paredes ni colisiones de un escenario completo.

Círculo alterna CAP30/CAP45. L cambia el suelo y R el raster. Select activa la telemetría durante tres minutos; una vez agotada, Select permite iniciar otra captura. Para comparar: deja G2/T1 y CAP45, mantén cazador y cámara quietos mirando arriba y registra 20 segundos en C0, 20 en C1, 20 en C2, 20 otra vez en C1 y 20 en C0. No alteres cámara/posición entre esos tramos. Después compara el suelo mirando abajo con techo apagado; las proyecciones no cubren necesariamente el mismo número de píxeles, así que sus milisegundos no tienen por qué coincidir.

El cálculo por píxel y por franjas debe producir exactamente la misma imagen y profundidad para el techo. Ambos usan el plano horizontal con profundidad constante por fila, colocan los actores posteriormente y conservan la oclusión. La versión por franjas evita recalcular coordenadas y celdas por cada píxel; queda por medir su beneficio en Vita. La referencia sirve para diagnosticar, no como modo recomendado de juego.

STT/7 conserva todos los campos de STT/6 y añade en `perf`:

- `ceiling_mode`: entero 0..2.
- `ceiling_us`: promedio de microsegundos por imagen, entero sin signo de 32 bits; separado de `ground_us` e incluido en `render_us`.
- `target_fps`: exactamente 30 o 45.

Cambiar techo u objetivo crea sesión nueva y descarta la ventana parcial; cambiar suelo/raster también descarta esa ventana. Se mantiene el corte de envío de tres minutos desde la activación original. El lector admite STT/4–7 y no inventa techo/objetivo para datos históricos. Sesión `vita-0020-f45-c2-<reloj>` identifica el binario 00.20; los tres campos adicionales son obligatorios en STT/7. El analizador separa techo, objetivo, suelo y raster. No se mide utilización GPU ni intervalos individuales de presentación.

Pruebas automatizadas: coincidencia exacta de color y profundidad en 120 vistas/posiciones; reconstrucción independiente de altura y reproyección; cámara siempre dentro de la separación vertical; triángulo cercano tapa el techo; escena integrada con cazador/arma propios o CC0; contrato C→Python y compatibilidad con versiones anteriores. Las imágenes PC son sintéticas y sus FPS de HUD no miden la consola.

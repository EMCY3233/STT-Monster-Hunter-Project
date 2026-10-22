# STT 0.16 — rasterización incremental y fases de render

La captura física de0.15 confirmó recepción de datos y sugirió un cuello de botella en dibujado. Esta entrega prepara otra comparación; no afirma una mejora física antes de probarla. Mantiene identidad STTP00001.

## Uso de la comparación

- G1 sigue siendo el suelo calculado por filas; L alterna G0/G1.
- T1 es el nuevo rasterizador incremental y T0 el rasterizador de triángulos de0.15; R alterna T0/T1. Predeterminado G1/T1.
- Select activa captura de180segundos; conserva la configuración privada de destino. Comparar primero30sG1/T1 y30sG1/T0, repitiendo vista, movimiento y ataques. Cambiar un solo parámetro cada vez.

Ambos modos incorporan transformación del cuerpo por vértice único y comparten el buffer cacheado de0.15. T0 conserva el cálculo anterior de cobertura/profundidad de triángulos, no es una reproducción binaria completa de0.15.

## Cambios

El rasterizador anterior dividía por área para cada coordenada baricéntrica y por profundidad para cada esquina dentro del bucle de píxeles. T1 prepara los coeficientes por triángulo y avanza cobertura y profundidad mediante incrementos. La cobertura usa enteros de64bits a1/16de píxel y orientación canónica. No añade descarte por orientación ni modifica el rechazo completo de triángulos que cruzan el plano cercano. La cuantización puede cambiar la cobertura en bordes dentro de un píxel; comprobar visualmente siluetas y uniones.

La transformación del cuerpo calcula seno/coseno una vez y transforma cada vértice una vez antes de emitir triángulos. Se conservan cotas, validación de índices y propiedad inmutable del archivo de pose.

## Medición

STT/5 añade `raster_mode` y seis medias por ventana: `clear_us`, `ground_us`, `body_us`, `weapon_us`, `target_us`, `hud_us`. Personaje y arma incluyen preparación, transformación y rasterización de su grupo. Un reloj de proceso inyectado permite verificar los límites de fase en PC y usar el reloj Vita en producción. Son tiempos transcurridos, no porcentajes de utilización.

El receptor conserva STT/1–4 y añade validación estricta deSTT/5. El analizador separa fuente/sesión/G/T; las capturas antiguasSTT/4 se interpretan comoT0, sin inventar tiempos de fases ausentes. Al cambiar G o T se descarta la ventana incompleta. CDLG, FG APP, VNZ y cargas siguen no disponibles. La lecturaGPU0 de0.15 sigue sin interpretación validada; no es evidencia de0% de uso.

## Verificación

Pruebas independientes comparan T1 con T0 en24triángulos en perspectiva: cobertura vecina dentro de un píxel y error de profundidad compartida menor que0.002en unidades de profundidad inversa. Se mantienen pruebas de orientación doble, degenerados, rechazo del plano cercano,12cámaras del suelo, canarios de framebuffer/profundidad, corrupción de recursos y combate. Un reloj sintético verifica los seis intervalos sin atribuir esos tiempos a hardware. C→Python y validación/análisis comprueban la nueva versión y preservación deSTT/4.

Ganancia de FPS, errores visuales en consola y distribución real por fase quedan pendientes de nueva captura física.

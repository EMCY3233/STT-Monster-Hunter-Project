# STT — Métrica de silueta alfa para comparativas visuales (propuesta)

**Áreas:** 07 (modelos/gráficos) y 10 (validación). **Estado:** procedimiento experimental, sin demostración de fidelidad a MH4U. **Fecha:** 2026-10-23.

## Método reproducible

1. Utilizar dos PNG del **mismo recurso** con dimensiones, cámara, pose, escala, orientación y encuadre registrados. No alinear, recortar ni remuestrear silenciosamente.
2. Convertir los canales alfa a máscaras binarias: píxel visible cuando `alfa > 127` (umbral por defecto, configurable de 0 a 254). Registrar el umbral usado.
3. Contar píxeles de referencia, candidato, intersección, unión, exclusivos de referencia y exclusivos de candidato.
4. Calcular `IoU = intersección / unión` si la unión no está vacía. Cuando ambas máscaras están vacías, registrar **INCONCLUSO / IoU no definido**, nunca 1.
5. Conservar hashes SHA-256 de las capturas y la versión del comparador. Guardar entradas y salidas comerciales solo en un directorio privado fuera de Git.

## Límites de interpretación

- Dos capturas totalmente opacas producen una silueta de cuadro completo: **IoU=1 no implica igualdad de modelos**.
- IoU ignora RGB, materiales, UV, iluminación, transparencia parcial, profundidad y animación. Los píxeles RGB invisibles bajo alfa=0 pueden diferir aunque la silueta coincida.
- Un IoU bajo puede deberse a cámara/pose distintas y no a geometría errónea. La coincidencia requiere primero demostrar la identidad del recurso y las condiciones de captura.
- El resultado de un lector de tablas, un renderizador experimental o CI sintética no acredita fidelidad visual al juego original.

## Criterios mínimos

La evidencia privada debe indicar: identidad opaca del recurso, origen legítimo, hashes de entradas, herramienta/commit, dimensiones, umbral, condiciones de cámara y resultado PASS/FAIL/INCONCLUSO. No publicar capturas, texturas, modelos, claves o recursos comerciales.

**Siguiente ensayo:** un par de capturas transparentes sintéticas con intersección 1, unión 3 e IoU 1/3; después, solo con una referencia legítima y emparejada de MH4U, repetir en privado. Esta nota no certifica haber realizado esa comparación real.

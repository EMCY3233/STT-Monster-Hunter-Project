# STT 0.18 — mirada hacia arriba y separación del cazador

La palanca derecha permite cruzar el horizonte y mirar hacia arriba. El límite de pitch pasa de+0.12a−0.45radianes (unos25.8°hacia arriba); se conserva el extremo superior+1.05. No se invierten los controles existentes.

Una única función portable calcula la vista usada por el renderer. Conserva la órbita nominal de6m, limita el ojo a una altura mínima de0.35m y mantiene al menos2.75m de separación horizontal del centro del cazador. Al alcanzar el suelo, la altura deja de bajar mientras continúa la inclinación de la mirada; el personaje puede desplazarse hacia la parte inferior de la pantalla. No se mueve la cámara a través del cuerpo para mantenerlo centrado.

## Alcance de la protección

Se comprueban los vértices reales del cuerpo propio y de la espada CC0 de todas sus poses, junto con la espada portada y la vaina de estudio. Todos deben quedar dentro de un cilindro de2.5m, dejando0.25m como mínimo respecto al límite horizontal de la cámara. Un disco es convexo: los triángulos cuyos vértices permanecen dentro también quedan dentro; la exclusión del ojo no depende solo de comprobar puntos aislados. Además se verifica profundidad positiva mayor que el plano cercano para40vistas por pose.

Esta protección corresponde al cazador y equipo actuales y al suelo plano. No es un sistema general de colisiones con paredes, monstruos ni recursos nuevos de mayor tamaño; esos casos necesitan sus propias cotas y pruebas.

## Verificación

- Controles: nuevo rango vertical, mirada ascendente, altura mínima, órbita y base ortonormal en32orientaciones×41entradas de pitch, incluyendo entradas fuera del rango.
- Geometría: todas las poses del cuerpo/equipo frente a40vistas, sin invadir el cilindro de exclusión ni el plano cercano.
- Suelo: G2 conserva imagen y profundidad exactas deG1 en120cámaras, ahora incluyendo mirada ascendente y altura limitada.
- Capturas PC: arriba, horizonte y abajo, realmente revisadas antes de aceptar el paquete.

G2/T1, controles de combate y productor STT/6 se conservan. STTP00001/00.18; compilación no equivale a validación física del nuevo movimiento ni de sus FPS.

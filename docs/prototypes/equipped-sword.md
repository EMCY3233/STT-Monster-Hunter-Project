# Espada de estudio equipada — 22-10-2026

Extensión de PR21 (41bd4479), con el derivado CC0 de PR22 (49278e33).
Sin fusión de esas ramas. No se copia código del monitor ni cambia STT/3.
El personaje sigue siendo la muestra original STT; no es Kenney adaptado.

## Geometría, montaje y tiempo

Espada Quaternius derivada:199v/394tri, 7474bytes Pose/1, SHA256
da8c1a437b2d090acda2f3f3b7fbe61bd548c665537b72a9134c994da6c09dd8.
Autor y CC0 declarada por su página constan en QUATERNIUS-NOTICE.txt, incluido
en VPK. No se atribuye como recurso propio ni como arma de Monster Hunter.
La simplificación con pérdidas y procedencia se documentan en PR22.

El muñeco propio tiene cuatro articulaciones:root/torso/arm/blade. Para este
perfil, joint2 es codo y joint3 la mano/socket. Se conserva exactamente toda
la secuencia de joints; se eliminan solo los8v/12tri de la antigua hoja propia.
El cuerpo resultante tiene40v/60tri y el mismo rig/clips a60Hz (120/72frames).
prepare_body.py fija el hash de origen y regenera el derivado reproducible.
Cuerpo126315bytes, SHA256
9881699bf7f3de544038755f9b8251877593ecde60c4927d00406f9be170c861.

La dirección codo→mano define el eje longitudinal y la normal fija+Z conserva
el plano del rig original. Base transversal=(dy,-dx,0), longitudinal=(dx,dy,0),
normal=(0,0,1), determinante+1. No refleja ni cambia winding. Grip provisional
del modelo:Y180mm desde el pomo; se mapea exactamente a la mano antes de
aplicar posición/yaw del cazador. Es un ajuste experimental, no un socket
universal de rigs glTF/FBX ni una empuñadura certificada para otros personajes.
El montaje rechaza segmentos<100mm/>2000mm y desviación Z>1mm del plano.

La espada usa pose estática de un frame; se transforma con el brazo cada
frame. Idle/ataque siguen la política visual y tick global de PR21. La animación
no sincroniza ni define ventanas de daño, combos o hitboxes. Render no muta
SttCombat. La vieja hoja y el box de arma independiente no se dibujan a la vez
que el montaje nuevo. Si cuerpo no es compatible, se conserva fallback anterior.

## Carga, errores y memoria

Carga única desde app0:/assets/hunter-body.pose.json y
app0:/assets/quaternius-sword.pose.json. No se lee ningún juego ni carpeta FTP.
Cuerpo conserva límite160KiB+byte de detección; espada usa8KiB+byte de detección,
índice y una pose fija precargada. No se duplica otro buffer corporal160KiB.
Se exige espada Pose/1 de1raíz/1clip/1frame, además de límites del lector C.
Sin malloc de malla ni por frame; buffers son estáticos, no se copian/mueven ni
mutan después de carga. La API memory requiere entrada que no solape al objeto.
Libc stdio puede reservar memoria interna transitoria; no se inventa su pico.

El emisor prepara base y trigonometría una vez por dibujo; transforma vértices
por índice sin calcular trigonometría para cada triángulo. Máximo512triángulos,
misma cota del formato. No acredita30FPS físicos.

Archivo de espada ausente, inválido o demasiado grande: estado no READY y
hoja simple propia de12tri en el mismo montaje. Sin reparación, escritura,
red ni parada del combate. Si la geometría/socket es incompatible se vuelve
al box anterior. Sink puede emitir un prefijo antes de cancelar; se presupone
buffer/index inmutable validado en el camino normal de la aplicación.

## Validación y paquete

Pruebas nuevas previstas:anclas de grip/tip/yaw, 384comprobaciones de anclaje
en todos los frames a yaw0/90°, cotas/socket inválido, ausencia/corrupción/exceso,
índice fuera de rango,12tri de fallback frente394 reales, canarios,16cámaras y
combate con1impacto/HP90 sin mutación desde render. Tres capturas PC (idle,
swing y fallback) se generan para revisión real posterior.

APP STTP00001/00.12. Inspección verifica SELF/SFO, hashes de ambos assets y
créditos de tercero. Monitor STTM00001 independiente. Al abrir rama, pruebas
C/PC, compilación/VPK, capturas y memoria sizeof están pendientes de nueva CI.
No FTP, instalación, ejecución consola ni fusión.

Personaje Kenney: sigue inspeccionado, no importado. Necesita evaluación de
skinning/quaterniones, simplificación y presupuesto temporal/memoria propio.
No se convierte un rig 3D general al perfil planar por cambiar sus nombres.

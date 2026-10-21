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

## Resultado verificado

Código `017d81e94da0c419ce0373b4ac5d644a85488be8`,
[CI39687110125](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39687110125)
aprobada: controls-and-adapter-pc, build e inspect-package. Con ASan/UBSan:
384anclas sobre192poses/yaw0/90°, grip/tip, errores/cotas/índices,12tri fallback
y394reales, canarios/16cámaras y combate1impacto/HP90 sin mutación desde render.
prepare_body.py regeneró exactamente el archivo versionado (git diff vacío).

PC x64:SttAsset172904bytes y SttWeapon17256bytes, suma190160bytes de objetos
estáticos de datos. Payload JSON cuerpo126315 + arma7474 =133789bytes; los
objetos incluyen capacidad no usada, índices/scratch y padding. No es memoria
pico ni medida Vita; quedan fuera framebuffers, depth, pila, libc y otros datos.
No hay una reserva nueva de malla por frame ni una medición de rendimiento.

Se descargaron y abrieron realmente las tres capturas del
[artefacto12386787095](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39687110125/artifacts/12386787095),
PC480×272. Idle muestra espada gris en la mano al final del brazo; swing tick18
la eleva con el mismo apoyo; archivo corrupto muestra hoja simple propia y
SWORD FALLBACK. No se observa la vieja hoja duplicada ni un arma independiente
flotando junto al muñeco en estas vistas. La animación/daño siguen desacoplados.
Frame_us33333 del HUD es entrada sintética, no FPS/tiempo real medido.

Hashes SHA256 PPM:
- idle:7ea04dc06663b5f934cb09e67fe6f1d018323c748c51e2a0aac7ed48ea5bf60e
- swing:c4f0ea9bf1c1c10e02156db4ab751ac10297d2cef1a2f5f840ec8728ac35d813
- fallback:68459985311f8fe798c0ad0db3af79f9d344082aee6d743e0eda1cb13abb020c

VPK STTP00001/00.12, inspeccionado en CI con SELF/SFO, créditos y hashes:
[artefacto12386553261](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39687110125/artifacts/12386553261),
SHA256 `597a05de9553a62e21d0ce5ad6971f2be577908361ce3b539a7668c3ad44a2b2`.
No se instala ni transfiere. Commits de cierre solo documentales.

Pendientes:posición/visibilidad/controles/suspensión y recursos reales en Vita;
el clipping parcial sigue fuera como en PR21. El cuerpo Kenney requiere su
adaptación propia:esta entrega no lo importa. No hay validación GPU/hardware.

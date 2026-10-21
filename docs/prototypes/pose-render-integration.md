# STT Pose/1 en el renderer del prototipo

21-10-2026. Rama propia sobre PR11 `0403d646`. Dependencias explícitas:
PR15 define STT Pose/1 y el exportador PC; PR17 aporta el lector/adaptador C
(fuentes stt_pose.c/h idénticas al código probado `0c9fd354`). Se incluyen esas
dos fuentes para compilar sin fusionar otras PR. No se copian cambios del monitor
ni se amplía STT/3; la telemetría de PR11 queda como estaba, sin emisor UDP.

## Muestra y comportamiento

Se empaqueta solo la muestra original exportada desde Asset Lab: 4 huesos,
48 vértices, 72 triángulos, Idle120ticks y Practice swing72ticks, JSON149293bytes.
SHA256 `a6648b5901bf6282457062911946399aa3019cc7fb23a661bfc5aa81550dfcdc`.
Es exactamente el archivo de prueba de PR15/17; no es un modelo comercial.
Para regenerar desde PR17, dentro de asset-lab:

```text
python -m stt_asset_lab.bridge --runtime samples/practice-dummy.stt.json practice.pose.json
```

La aplicación carga una vez `app0:/assets/practice.pose.json`, nunca rutas de
juegos ni de transferencia. El lector conserva el buffer inmutable. El render
selecciona clip0 en idle y clip1 en otros estados (si existe). Usa tick global
60Hz módulo duración: la animación es una visualización independiente, no queda
sincronizada a ventanas de ataque ni define hitboxes. Reiniciar combate reinicia
el tick; suspensión pausa el avance de simulación según la lógica previa.

Los triángulos conservan índices/winding, pasan mm→metros y reciben posición/yaw
del cazador, con yaw0=+Z y yaw16384=+X. La espada y combate experimental previos
permanecen independientes del rig. No hay skinning ponderado ni importación en
runtime de formatos comerciales. Near-plane y raster CPU siguen las limitaciones
del renderer anterior. No se afirma rendimiento físico ni fidelidad histórica.

Archivo ausente o inválido: estado MISSING/INVALID visible y cazador simple
anterior. No aborta el bucle ni el combate; no intenta descargar, reparar ni
escribir el archivo. Error de emisión desactiva la malla para siguientes frames
y muestra fallback. Las funciones no comparten datos con procesos externos.

## Presupuestos y vida de buffers

SttAsset es estático y propietario de un buffer160KiB+1byte (extra para detectar
exceso), índice y scratch de una pose. No hay malloc de malla ni asignaciones
en el render del asset. Límite de app160KiB, más estricto que Pose/1 general2MiB:
se rechaza exceso, nunca se trunca para aceptar. El JSON se valida completo.
El índice solo referencia bytes propiedad de ese mismo SttAsset durante toda
la aplicación. No copiar/mover SttAsset una vez cargado; no recargar durante
un frame ni mutar buffer/índice. Se puede recargar entre frames con revalidación.
`fopen/fread/fclose` pueden usar buffers internos de libc; no se inventa su pico.

El almacenamiento del asset es `sizeof(SttAsset)` incluyendo padding. La prueba
PC lo imprime; no equivale a RAM medida en Vita. Conserva las reservas anteriores:
dos bloques CDRAM0xC0000 y depth480×272×sizeof(float), más otros estados. Se
documentará la cifra PC tras CI; total pico Vita sigue pendiente de medición.
El test usa buffers/canarios propios y emite una imagen PC PPM como artefacto.
Una imagen generada no equivale a revisión visual ni captura de consola.

## Identidad y verificación

VPK STTP00001 / STT Vita Prototype /00.11, independiente de STTM00001.
Inspección comprueba hash VPK, SELF, SFO, contenido exacto y hash de muestra.
No se instala ni transfiere. El cambio de versión requiere nueva revisión del
paquete; documentación sola no justifica volver a transferir.

CI PC con ASan/UBSan verifica ancla asimétrica y yaw90°, índices/tiempo, bucles,
archivo ausente/inválido/sobredimensionado, fallback igual en región de escena,
aparición y cambio temporal de malla, 16 cámaras/yaws y canarios de framebuffer,
depth y estado. Compilación/enlace Vita y paquete se verifican por jobs separados.
Al abrir esta rama esos resultados están pendientes; no hay prueba física.

## Resultados verificados al cierre

Código `a8284a5bbae7b24fd93b8c256fe1307f56a9fb50`,
[CI 39680285352](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39680285352)
aprobada: controls-and-adapter-pc, build e inspect-package.
La prueba PC con ASan/UBSan pasó las anclas, bucles, errores/fallback, escena
variable con tiempo y16cámaras con canarios. La prueba previa de combate/control
y snapshot también pasó en esta rama. No son pruebas de usuario en hardware.

El ejecutable PC x64 midió `sizeof(SttAsset)=172904` bytes, incluido el buffer
fijo163841bytes, índice5600bytes y scratch3456bytes más enum/padding.
Es almacenamiento estático de ese objeto, no pico de memoria del proceso;
no equivale al ABI ni al uso de RAM en Vita. No hubo malloc nuevo por frame.

VPK de esta CI:
[artefacto12383447931](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39680285352/artifacts/12383447931),
STTP00001/00.11, SHA256
`e0077e77b36afd24987443e820a26416499285c76be27d81a24dfb900c87853a`.
La inspección descargó el paquete dentro de CI y comprobó checksum, cabeceras,
SFO y hash de la muestra empaquetada. El tamaño del ZIP contenedor de Actions
no se presenta como tamaño del VPK. No se descargó ni instaló en la consola.

El [artefacto PC12383477797](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39680285352/artifacts/12383477797)
contiene PPM rasterizado y recibo numérico. No se ha hecho revisión visual;
producir la imagen no demuestra calidad gráfica. El siguiente bloqueo es
revisar esa imagen y, cuando proceda bajo autorización separada, comprobar en
hardware carga/controles/animación, errores y recursos. Este encargo no realiza
FTP, instalación ni ejecución física. No se fusiona ninguna PR.

[Recibo estructurado](pose-render-evidence.json). Los commits documentales
posteriores no alteran el código probado ni justifican recompilar/reinstalar.

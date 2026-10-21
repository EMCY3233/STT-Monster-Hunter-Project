# Lector C portable STT Pose/1

Extensión del puente PR15; no modifica el VPK STTP00001 ni el monitor STTM00001.
Entrada: JSON STT Pose/1 en perfil canónico C producido explícitamente por
`python -m stt_asset_lab.bridge --runtime source.stt.json destination.pose.json`.
No es un nuevo formato binario. El perfil ordena campos como el exportador y
restringe nombres de clip a ASCII imprimible sin escapes; otros JSON válidos de
Pose/1 se rechazan deliberadamente. `runtime_dumps` normaliza el orden y rechaza
nombres incompatibles. Pose/1 general conserva nombres Unicode y orden libre.

## Acceso y seguridad

`stt_pose_open` recibe buffer inmutable y longitud explícita ≤2 MiB. Recorre todo
el documento una vez, valida versión, Hz, base, jerarquía, índices, cantidades y
rangos; guarda hasta 600 offsets uint32 a frames. No confía en offsets recibidos
del archivo (JSON no contiene offsets). Cada offset se deriva de una posición
comprobada en el buffer y se vuelve a acotar al solicitar una pose.

El parser no recurre ni reserva heap; comprueba el extremo antes de leer cada
byte, limita cada array antes de escribir y corta acumulación decimal antes de
overflow. Rechaza decimales/exponentes, booleanos, campos repetidos/desconocidos,
ceros iniciales, escapes, truncamientos y basura posterior. Un error borra el
índice/salida. El llamador debe mantener el buffer y el índice sin mutaciones y
no solapar buffers/estructuras de entrada y salida. No es una API de streaming
de archivos: el buffer completo debe estar residente y la lectura acotada la
gestiona el llamador. No lee sockets ni archivos por sí misma.

`stt_pose_frame` valida clip y offset, aplica módulo al tick uint64 y decodifica
solo esa pose a arrays fijos. No reevalúa huesos ni acumula errores de rotación.
El render puede reutilizar una única salida. `stt_pose_transform` coloca un
vértice en metros con la misma rotación yaw de PR11; valida rangos antes de
convertir. No vincula animación con ventanas de ataque/hitboxes.

## Memoria y reproducción

Índice: buffer prestado + tamaño, 600 offsets de 4 bytes, 32 padres int16,
512 triángulos de 3 uint16, dos tablas de 8 uint16 y cinco conteos uint16.
En ABI de puntero/size_t de 8 bytes la suma es 5594 bytes antes de padding;
`sizeof` se obtiene de la prueba ejecutada. Frame: (32+256)×3×4 = 3456 bytes.
Pico residente del llamador: bytes del JSON + sizeof(SttPose) + 3456, más pila,
buffers de render y runtime externos. No son medidas de memoria Vita.
Parseo usa además 8 nombres de 65 bytes y temporales pequeños en pila;
no se acredita un máximo de pila sin mapa/análisis de compilación.

```text
python -m unittest discover -s asset-lab/tests -v
python pose-runtime/tests/check_cross.py
```

La segunda orden requiere compilador C99 (CC por defecto cc), construye un
ejecutable de prueba y compara todas las coordenadas con Python. POSE_CFLAGS
permite sanitizadores. CI separa pruebas PC y compilación de objeto con VitaSDK
fijado por digest; no instala ni ejecuta en consola. El ejecutable de prueba
reporta sizeof y evidencia de muestra. Estado inicial local: 30 pruebas Python
aprobadas en Python 3.12.14; C local no disponible. La evidencia C remota se
registra abajo, separada de esas pruebas locales.

Pruebas ejecutadas en CI: cada truncamiento del documento de ancla,
versión/hz/base, límites enteros, conteos, duplicados, índice/jerarquía, tiempos
y módulo (incluido UINT64_MAX), offsets dañados del índice y muestra original.
No hay mediciones de FPS, GUI ni ejecución física. Integración con el renderer
se prepara tras validar el lector; las fuentes del renderer siguen en PR11.

## Preparación mínima del render

Tras aprobar la primera prueba C/Python del lector (job cross-pc de
run39677218607, commit ff7171ce), se añadió `stt_pose_emit`: toma una pose,
conserva winding e índices, aplica mm→metros/posición/yaw y llama a un callback
por triángulo. Usa el scratch del llamador; no reserva otra malla ni mantiene
punteros al triángulo después del callback. Callback cancelable y validación
de índices de nuevo antes de acceder al vértice. Una cancelación puede haber
emitido un prefijo: el consumidor debe descartar su frame incompleto.

La prueba PC compara el número de triángulos y sumas de coordenadas emitidas
con un cálculo independiente Python a yaw90°, posición (4,0,5)m, por cada clip.
La transformación del ancla tiene además assertions C de orientación y rango.
Esto prepara la conexión al tri() de render.c de PR11; no se copió ni modificó
ese renderer, no se rasterizó una escena ni se presenta una imagen como revisada.
Se mantienen pendientes la conexión del callback en PR11, errores de carga en
aplicación, selección de clip y verificación de render/tiempos en hardware.

## Resultado verificado de esta revisión

Commit de código `0c9fd354b7d9e0ea6cfda723dd7665b3618b988f`,
[CI 39677522635](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39677522635):
cross-pc y compile-vita aprobados. PC: 288 casos ejecutados con
AddressSanitizer y UndefinedBehaviorSanitizer, incluidos los truncamientos del
ancla, comparación de todas las poses y callback de triángulos por clip.
Vita: objeto C99 compilado con advertencias como errores en SDK fijado;
no es enlace de VPK ni ejecución en consola. La prueba inicial de solo lector
ff7171ce también pasó ambos jobs (39677218607).

`sizeof(SttPose)=5600`, `sizeof(SttPoseFrame)=3456` medidos por el ejecutable
PC x64. Para la muestra propia, buffer+índice+salida suman 158349 bytes;
al máximo de archivo, 2106208 bytes. Son tamaños de almacenamiento calculados
con sizeof real, NO memoria pico del proceso ni memoria medida Vita; omiten
pila, asignador, librerías y render. El parser/lector no usa malloc; el probe
reserva solo el buffer de entrada y lo libera al terminar.

Muestra exportada: 149293 bytes, SHA256
`a6648b5901bf6282457062911946399aa3019cc7fb23a661bfc5aa81550dfcdc`.
No se modificó el asset original. Los cambios posteriores de documentación
no cambian el código cubierto por esta evidencia.

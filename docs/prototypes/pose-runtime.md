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
aprobadas; C local bloqueado por falta de compilador, pendiente CI de esta PR.

Pruebas previstas del ejecutable: cada truncamiento del documento de ancla,
versión/hz/base, límites enteros, conteos, duplicados, índice/jerarquía, tiempos
y módulo (incluido UINT64_MAX), offsets dañados del índice y muestra original.
No hay mediciones de FPS, GUI ni ejecución física. Integración con el renderer
se prepara tras validar el lector; las fuentes del renderer siguen en PR11.

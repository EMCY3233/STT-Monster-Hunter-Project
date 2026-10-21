# STT Pose/1: puente offline Asset Lab → coordenadas Vita

21-10-2026. Extensión independiente sobre PR10 f06e289f. No modifica STT/3,
PR8/9/11, monitor, banco ni consola. Exportador e importador de referencia PC;
el VPK STTP00001 todavía NO carga este formato.

## Contrato cerrado para esta versión

STT Asset/1 sigue siendo la fuente editable en metros. STT Pose/1 contiene poses
mundiales de modelo precalculadas: no offsets locales ni ángulos para evaluar en
destino. Conserva padres para inspección; cada frame incluye joints y vertices.
Triángulos conservan sus índices y orden. No hay texturas, pesos, eventos,
hitboxes, root motion aplicado al cazador ni interpretación de nombres de clips.

La base es identidad de determinante +1: +X derecha, +Y arriba, +Z delante del
personaje hacia el observador frontal del Asset Lab. Ese frente se coloca en +Z
de escena Vita a rumbo cero, consistente con stt_camera_move de PR11. No hay
espejo ni inversión de índices. El winding conserva el producto vectorial del
origen; cualquier culling futuro debe usar esta misma convención. La cámara
elige la proyección, no altera el contrato geométrico. El modelo se coloca luego
mediante transformación de escena; este puente no hace esa integración.

Cada coordenada se multiplica por 1000 y redondea a mitad alejándose de cero;
se rechazan resultados fuera de ±1.000.000 mm. El error por coordenada muestreada
es ≤0,5 mm (tolerancia numérica de prueba 1e-8 mm). La jerarquía se evalúa con
el evaluador Asset/1 antes de redondear, evitando acumular redondeos por hueso.

60 Hz. La duración debe caer en ticks enteros con tolerancia 1e-7 tick; no se
trunca. Las claves fuera de cuadrícula se interpolan en su tiempo original y
se muestrean a tick/60. Se exporta [0,duración), sin duplicar el extremo; el
lector usa tick módulo número de frames. A 30 Hz un render puede elegir ticks
alternos; no se demuestra reproducción gráfica con este lector.

Presupuestos antes de evaluar: 32 huesos, 256 vértices, 512 triángulos, 8 clips,
600 frames totales. JSON UTF-8 ≤2 MiB; claves exactas y sin duplicados; padres
preceden hijos, raíz única, índices enteros sin booleanos, cantidades y rangos
validados. No se acepta una nueva versión de manera implícita. El límite de
bytes NO es un presupuesto de memoria residente en Python o Vita. No hay
garantía de equivalencia continua entre ticks ni de rendimiento físico.

## Reproducir

Desde asset-lab con Python 3.11+:

```text
python -m unittest discover -s tests -v
python -m stt_asset_lab.bridge samples/practice-dummy.stt.json practice.pose.json
```

El destino debe ser nuevo. Para importar: `bridge.loads(raw_bytes)` valida una
vez; `bridge.frame(data, clip_index, tick)` selecciona una pose. Conservar el
objeto validado sin mutaciones. El formato es JSON, no una estructura binaria C
ni un parser runtime Vita. El lector rechaza entradas mayores del límite; quien
lea archivos debe leer como máximo MAX_BYTES+1 antes de pasarlas al lector.

## Evidencia local verificada

29 pruebas PC aprobadas (23 anteriores +6 nuevas) el 21-10-2026 con Python 3.11+
del runtime local. Primer intento: 2 pruebas antiguas fallaron por permisos del
directorio temporal del sandbox; repetición con TEMP/TMP dentro del workspace:
29/29. No se cambiaron las pruebas para ocultar ese fallo.

Pruebas nuevas: roundtrip de las 192 poses con comparación de cada coordenada
contra origen, bucle, ancla asimétrica de dos huesos rotada 90°, winding positivo,
redondeo ±0,5 mm, coordenadas no finitas, rango, jerarquía, índices, booleanos,
cuentas inconsistentes, duración fuera de cuadrícula, claves entre ticks,
duplicados JSON y límites de bytes/frames.

Exportación CLI real de la muestra propia practice-dummy: 149293 bytes, SHA256
`a6648b5901bf6282457062911946399aa3019cc7fb23a661bfc5aa81550dfcdc`.
La muestra de origen no se modifica. El archivo generado no se versiona.

## Siguiente integración

Revisar este contrato con PR11 antes de añadir parser/buffers C acotados y carga
en el render. Medir memoria/reserva y verificar las mismas anclas en C. La
compilación Vita, GUI, poses en hardware, FPS y carga del formato quedan
pendientes. STTP00001 y STTM00001 siguen separados. No hubo FTP ni instalación.
El transporte UDP STT/3 continúa como tarea distinta de este puente geométrico.

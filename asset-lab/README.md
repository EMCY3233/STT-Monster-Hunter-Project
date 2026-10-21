# STT Asset Lab 0.1

Inspector PC independiente para **STT Asset/1**, con una muestra original reproducible.
No abre formatos de Monster Hunter ni contiene datos derivados de juegos.

Requiere Python 3.11 o posterior y Tk/Tcl (normalmente incluidos en Python para Windows;
en Linux puede ser necesario el paquete python3-tk del sistema). Sin paquetes pip ni red.
Desde esta carpeta:

```sh
python -m stt_asset_lab samples/practice-dummy.stt.json
python -m stt_asset_lab samples/practice-dummy.stt.json --validate
python -m unittest discover -s tests -v
python package.py
```

La primera orden abre la ventana: Play/pause, selección de clip, Bones, árbol de huesos,
Open/Export STT JSON y reinicio temporal. Arrastrar con botón izquierdo orbita; rueda amplía.
Cerrar la ventana sale. `--validate` sirve sin pantalla. Código 2: archivo rechazado;
código 3: pantalla Tk no disponible. El ZIP de `dist/` se descomprime y se ejecutan estas
mismas órdenes desde `stt-asset-lab/`; es una aplicación Python, no un EXE ni un instalador.

## Contrato STT Asset/1

JSON UTF-8, máximo 1 MiB; lector rechaza campos desconocidos/duplicados, índices inválidos,
NaN/Infinity, ciclos, estructuras y tiempos inválidos. No hay rutas de recursos, scripts,
plugins, referencias externas ni accesos de red. Formato de la muestra:

- `format: "STT Asset"`, `version: 1`, `name` (1–64 caracteres imprimibles).
- `bones` (1–128): `name`, `parent` (-1 solo raíz; padre debe preceder al hijo), `offset: [x,y,z]`.
- `vertices` (1–8192): `position: [x,y,z]` local al hueso, `bone` (índice).
- `triangles` (1–16384): tres índices de vértice distintos.
- `clips` (1–32): `name`, `duration` (0 < segundos <= 600), `tracks`.
- Cada track: `bone` único en clip, `keys` (2–1024): `[segundos, rotación Z en radianes]`.
  Tiempos estrictamente crecientes, primero 0 y último igual a duración.

Ejes de mano derecha: +X derecha, +Y arriba, +Z hacia el observador en vista frontal.
Unidad geométrica: metro. Offsets expresados en espacio del padre; vértices en espacio
local del hueso. Rotación local Z, propagada a los descendientes; interpolación lineal de
ángulos (sin camino corto automático). Reproducción cíclica módulo duración. Pose base sin
track: ángulo cero. Un único hueso rígido por vértice, sin pesos mezclados, traslación
animada, escala animada, cuaterniones, materiales, texturas, UV, normales, audio o colisiones.
La perspectiva es ortográfica con ordenación aproximada por profundidad: no es un renderer
Vita ni un editor de producción. El árbol muestra la jerarquía; no selecciona ni edita huesos.

El exportador revalida y escribe este mismo contrato, sin conversión a formatos de motor.
Un adaptador futuro hacia el contrato Vita deberá convertir metros a milímetros (×1000),
declarar el sentido de avance y convertir Z si la cámara o convención destino lo requiere;
**no hay un importador Vita ni binding de combate implementado**. Sin dependencia de STT/1,
STT/2 ni de investigación PR3/PR7.

## Muestra y evidencias

`generate_sample.py` crea desde geometría numérica propia el muñeco de cuatro huesos,
48 vértices, 72 triángulos y clips Idle / Practice swing. La muestra no intenta reproducir
un cazador, arma, rig o animación comercial. Es código/dato original del proyecto.

23 pruebas PC locales aprobadas el 21-10-2026: regeneración exacta, lectura/exportación,
interpolación/jerarquía, bucle, CLI y entradas malformadas. La ventana requiere pantalla;
el entorno Work no tiene DISPLAY ni Xvfb, por lo que **no se acredita revisión visual GUI**.
No hay pruebas físicas Vita ni transferencias. CI separada Windows/Linux valida el contrato
y empaqueta ZIP determinista; comprobar el run del commit antes de afirmar éxito remoto.

Detalle y SHA del paquete inicial: `docs/prototypes/asset-lab.md` en el repositorio.

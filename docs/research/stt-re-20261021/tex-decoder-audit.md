# Una textura legible: el lector mhff descarta alfa

2026-10-21. Aceptación nueva de PC tras la comparativa de emuladores; una única carga ya existente, sin extracción adicional, Blender, emulador, instalación o visualización.

Fuente primaria: [mhff, io_import_scene_mod.py](https://github.com/svanheulen/mhff/blob/6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf/n3ds/io_import_scene_mod.py), commit `6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf`, blob `0da950c275caf78bfcfa310f6a45c488e890d94b`, GPL-3.0-or-later. La fuente revisada lee las dos palabras de alfa por bloque ETC1A4, pero solo escribe RGB; deja alfa inicializado a 1.0.

La auditoría ejecutó únicamente una constante literal y `decode_etc1`, seleccionadas por AST, con array estándar y una imagen simulada 8×8/depth32. No importó el módulo completo ni Blender. Se verificó el blob exacto de la fuente, conservando su cabecera de licencia privada. Python3.12.14, little-endian y array unsigned-int de cuatro bytes; otras plataformas no probadas.

**Control sintético:** dos entradas de cuatro bloques con RGB idéntico, alfa todo cero frente a todo FF. Ambas producen los mismos 256 bytes RGBA8 y alfa255 en todos los píxeles. Hash de ambas salidas: `ca60aebe5aac8a1345863ba9915c7da833bcdc32e37125c73dba508cdad7ae4b`. Confirma pérdida de información sin depender de la interpretación de un recurso comercial.

**Carga local única:** la [TEX estructural previamente aceptada](tex-smallest.md), 84 bytes, SHA256 `0e5ae51392aa2a13b0800e41f2969b15a2b1b609ca9e0e1181bc3a07af110f52`, conserva hash antes/después. Payload [20,84), cuatro bloques/64bytes; sus64 nibbles alfa contienen dos valores distintos, mientras los64 alfa de salida son255. Derivado privado RGBA8 de256bytes, SHA256 `80b3f0167f546fa97f5546cd3c00e9f61f002224993b5efaf6b269bffc56741e`. No se publican valores RGB, píxeles o imagen.

**Aceptación cumplida:** esta función no sirve como validación fiel del alfa ETC1A4. No se validaron RGB, orientación, orden completo de tiles ni aspecto en juego; tampoco se comparó otro decoder independiente. La contabilidad de cabecera/rangos TEX anterior sigue siendo un resultado separado.

[Recibo público sin píxeles](tex-decoder-audit-evidence.json). Conjunto privado `analysis-local/tex-decoder-audit-20261021/`: fuente revisada, `run_audit.py`, receipt.json y decoded-private.rgba8. Wrapper verifica blob y hash, ejecuta ambos controles y una carga; rechaza sobrescribir el derivado. Para reproducir, utilizar un directorio de salida nuevo y una copia de las fuentes existentes, manteniendo los recibos originales. No se modifica el banco compartido ni se recataloga el objeto.

Próxima aceptación de este frente: implementar o verificar un decoder que aplique alfa con controles sintéticos de nibbles y orden antes de comparar otra salida comercial. El resultado presente cierra una limitación concreta de herramienta; no justifica convertir masivamente las otras TEX.

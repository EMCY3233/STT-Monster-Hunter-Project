# Aceptación visual independiente del render PC

21-10-2026. Solo muestra propia; sin consola, FTP ni instalación.
Fuentes: PR21 sobre PR11, contrato/exportador PR15 y lector PR17.

## Capturas realmente observadas

Se descargó el artefacto11731bytes
[12383454645](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39682179024/artifacts/12383454645),
se validaron sus tres entradas/tamaño descomprimido y se abrieron las dos PPM
480×272 como PNG sin cambiar píxeles. No son capturas de pantalla de PS Vita.

| Vista con la misma cámara | Estado | SHA256 PPM |
|---|---|---|
|Referencia de la muestra |Idle, tick0 |7e927df082106ad0cc1f9fdf06590c344f8e37877f6e6d4e4e286af5b9bd66ee |
|Animación muestreada |Practice swing, tick18 |a7d657236f00d9b9da141d5ed47fe1c29b2c7cfea32216d46ee1f9224d016023 |

Observación visual: malla cian completa, apoyo y posición estables, brazo/espada
horizontal en referencia y elevado en la pose animada; objetivo rojo y suelo
visibles, HUD legible y ASSET READY en ambas. No se observó inversión aparente,
recorte de la figura por los bordes o desaparición de caras en estas dos vistas.
Esta observación no demuestra todas las poses ni cámaras ni equivalencia GPU.
La espada experimental separada sigue siendo geometría del prototipo; ninguna
de estas poses define ventanas de combate, daño o parámetros comerciales.

## Anclas CPU y regresión encontrada

El test de integración conserva ancla asimétrica jerárquica y giro yaw90°;
los triángulos emitidos corresponden a (7,2.25,4), (7,3.25,4), (7,2.25,5)m.
Prueba del renderer, cámara identidad: (0,0,2)→(240,142), (.8,.4,2)→(340,92).
Comprueba bitmap exactamente idéntico al invertir el orden del triángulo
de prueba, triángulos degenerados y rechazo de geometría tras/cerca de cámara.

La primera prueba nueva, eb537242, falló en igualdad de bitmaps con winding
invertido (CI39681998020). El renderer calculaba la tercera coordenada como
1-u-v, con redondeo distinto en píxeles de borde. Se corrigió evaluando las tres
funciones de borde. No se relajó la comparación ni se desactivó el sanitizador.
No se afirma que este único triángulo demuestre invariancia exhaustiva de toda
entrada flotante; sí conserva una regresión exacta del caso encontrado.

El renderer es doble cara; no hay culling. Rechaza el triángulo completo si un
vértice tiene z<0.15m: NO implementa clipping parcial. Puede haber desapariciones
al atravesar ese plano. Es un límite explícito conservado, no una función nueva
ni una garantía de calidad en todos los ángulos. No se midieron FPS ni GPU.

## Evidencia final

Código `d5df0516e44280035f4dcb4a2eb834183468b0ae`,
[CI39682179024](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39682179024):
PC ASan/UBSan, build Vita y inspect-package aprobados. Pruebas de fallback,
tiempo/bucles, 16cámaras y canarios siguen aprobadas; sizeofAssetPC172904bytes.
La captura tiene frame_us33333 como entrada sintética del HUD, NO medición.

VPK vigente revisable en
[artefacto12384288044](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39682179024/artifacts/12384288044),
STTP00001/00.11, SHA256
`bc95fdf5f5c1dbb5ea00e563eb26ff81ca4e5bbd6d580129a46be1e2bdb943a6`.
Sustituye como candidato al paquete de a8284a5b; no se transfiere ninguno.
Monitor STTM00001 intacto. No se fusionan ramas.

Siguiente aceptación que requiere hardware: carga desde app0, controles reales,
presentación en pantalla Vita1000, suspensión/reanudación y memoria/FPS reales.
No existe un bloqueo de backend PC: el renderer CPU produjo las vistas y se
inspeccionaron. Fuera de esta aceptación quedan ejecución GPU, rendimiento y
pruebas de archivos alterados en consola. No se crean más features por este cierre.

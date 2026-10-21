# MHXX update: ExHeader y .code BLZ

2026-10-21. Aceptación cerrada sobre **una sola entrada existente** del update MHXX. Sin arranque, desensamblado, claves, base cifrada, extracción de otras entradas o cambios al banco.

## Identidad y precondiciones

NCCH existente `analysis-local/containers/MHXX-patch-content.0000.00000000`, 36.868.096bytes, SHA256 `1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473`, `no_crypto=true`, unidades512bytes. La [identidad ExeFS anterior](plain-executables.json) se mantiene: `.code` de **7.419.468bytes**, SHA256 **`251399daef52a2a23bf77375a94ac4e6746bacb9b6d67e1b0654c82f57964f93`**, ahora leído dentro del mismo NCCH en offset11264. No procede de una conversión nueva de CIA.

Antes de descomprimir se comprobó: ExHeader de1024bytes, hash coincidente con NCCH, flag en offset0x0D **0x03**, bit0 de compresión activado; rangos de segmentos, ExeFS y .code dentro del archivo; hash de .code coincidente con tabla. Otros bits de flag no se interpretan aquí. Si el bit0 hubiera estado desactivado, la herramienta no habría aplicado BLZ.

Referencias primarias **Azahar2126.2, commit `219d743a1e698101fe1ab8bef43e6563126c3c27`**:

- [ncch_container.h](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/file_sys/ncch_container.h), blob `1559ee5dcf83aee8b197fb7510b433871c0e6b55`: estructuras y campos.
- [ncch_container.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/file_sys/ncch_container.cpp), blob `666d6037f1667ceea641cc46c7ee94cac5bee56c`: flag, tamaño y LZSS inverso. Se adapta el algoritmo con atribución GPL-2.0-or-later y comprobaciones más estrictas, sin afirmar equivalencia general con todas las entradas que acepta el emulador.
- [loader/ncch.cpp](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/loader/ncch.cpp), blob `842453fcbdace1f42a6ac17e9d6b15595fa8064d`: páginas4096, offsets consecutivos y BSS añadido separadamente en carga. Consulta documental, no ejecución de Azahar.

[Licencia GPLv2 incluida](azahar-gpl2-license.md); los archivos citados permiten versiones posteriores. Herramienta nueva `tools/stt_re/inspect_ncch_code.py`. No se copia ni publica el ejecutable comercial.

## Segmentos e invariantes

| Segmento | Dirección virtual | Páginas | Bytes declarados de código/datos | Capacidad por páginas | Offset en salida |
|---|---:|---:|---:|---:|---:|
| text | 1.048.576 | 2.803 | 11.478.072 | 11.481.088 | 0 |
| ro | 12.529.664 | 319 | 1.306.468 | 1.306.624 | 11.481.088 |
| data | 13.836.288 | 63 | 257.192 | 258.048 | 12.787.712 |

Direcciones alineadas, segmentos virtuales contiguos sin solapamiento y tamaños declarados menores o iguales a capacidad. Suma de capacidad **13.045.760bytes**. Las diferencias hasta capacidad son3016,156y856bytes; no se asume que su contenido sea todo cero. Stack65.536bytes. BSS468.516bytes, redondeado a471.040 por el loader de referencia, **fuera del .code descomprimido**. No se incorporó BSS ni se simuló memoria de proceso.

Pie BLZ: top11, bottom7.419.384, incremento5.626.292. Tamaño calculado `7.419.468 + 5.626.292 = 13.045.760`, exactamente la suma de páginas **antes** de reservar salida. Prefijo preservado84bytes; flujo comprimido7.419.373bytes; top incluye el pie y bytes que no se interpretan individualmente.

## Resultado de una descompresión

- Flujo completo consumido y cobertura de salida completa hasta el prefijo.
- 3.452.829literales +9.592.847bytes por1.663.501referencias +84bytes de prefijo =13.045.760bytes.
- Contabilidad de entrada:639.542controles +3.452.829literales +2×1.663.501tokens =7.419.373bytes.
- Salida privada `analysis-local/mhxx-code-blz-20261021/code.bin`, **13.045.760bytes**, SHA256 **`6f66928e0deecdcd20c3b0e67c614e6313dfe92c8dc0b9ba2d7a906d1efe4fe8`**.
- Fuente NCCH sin cambios por SHA256 antes/después; hash .code comprimido y ExHeader verificados. Ninguna clave o descifrado adicional.

La salida no tiene un hash esperado independiente en el contenedor: el hash ExeFS verifica la entrada comprimida. La aceptación combina referencia fijada, controles sintéticos e invariantes exactas; **no es validación independiente de cada byte del ejecutable**, ni identificación de funciones.

## Pruebas y reproducción

Diez pruebas nuevas: referencia solapada con salida esperada explícita, prefijo, pie truncado, top inválido, presupuesto, referencia fuera de salida, cobertura incompleta, entrada no comprimida sin forzar BLZ, alteración ExHeader, rechazo de NCCH cifrado y solapamiento de segmentos (algunas condiciones comparten prueba). Suite completa **116/116**, código de salida0; ayuda CLI nueva código0. Las106pruebas anteriores siguen siendo la campaña histórica, no un recuento adicional a sumar116.

Reproducción: `inspect_ncch_code.py --ncch <NCCH existente> --expected-sha256 1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473 --out-dir <directorio nuevo>`. Presupuestos128MiB de contenedor y64MiB de salida; directorio existente rechazado. Entrada actual y prueba no requieren claves ni instalación de emulador. Los tests usan datos sintéticos, no este recurso comercial.

[Recibo público de estructura y aceptación](mhxx-code-blz-evidence.json). El conjunto privado conserva el receipt.json original y code.bin; no mover/borrar los derivados referenciados ni registrarlos unilateralmente en el banco.

## Próximo bloqueo

La compresión ya está explicada para este update. La base MHXX permanece cifrada y no se equipara el ejecutable del update a un juego arrancable. Próxima aceptación útil de análisis estático: contrastar el mapa de segmentos con una segunda herramienta/implementación independiente sobre esta misma salida, antes de asignar funciones. Si se propone desensamblado después, fijar primero estado ARM/Thumb y evidencias de puntos de entrada; no derivar IA o ataques por nombres de secciones. La visualización MH4U sigue pendiente de herramienta de control visual fiable; no se repite un arranque equivalente.

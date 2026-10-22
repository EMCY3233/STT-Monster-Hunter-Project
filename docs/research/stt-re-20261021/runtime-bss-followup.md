# Seguimiento de candidatos y primer rango BSS variable — 22-10-2026

## Hallazgo confirmado

Un rango de 32 bytes en **`0x0110D000`**, dentro de la BSS derivada para MH4U, varió repetidamente: 118 respuestas RPC válidas en 12 segundos, 117 hashes distintos y 116 diferencias entre muestras consecutivas. No hubo errores. Es un objetivo variable verificado, **sin identidad semántica**: no se han identificado movimiento, animaciones, hitboxes, IA ni campos concretos. Un reloj o contador global sería una hipótesis posible, no un resultado.

## Experimentos acotados

| Ensayo | Lecturas correctas | Resultado y alcance |
| --- | --- | --- |
| Doce candidatos del segmento de datos | 520/520; 40 ciclos en 26,169 s | 40 muestras por candidato, todas estables; control de código en cada ciclo. 15.520 bytes extraídos en privado. |
| BSS dispersa: dos pasadas de 156 ventanas | 314/314 en 15,985 s | Una ventana cambió en cinco posiciones de byte. 9.992 bytes extraídos con controles. |
| Seguimiento de la ventana BSS 139 | 118/118 en 12 s | 117 hashes distintos; 116 cambios entre pares consecutivos. Solo digests y registro privado en este seguimiento, sin extracción de nuevos bytes brutos. |

La BSS se delimitó con el mapa ExHeader ya verificado y el [loader del commit exacto Citra 0ff3440232d6bc9226e37c41c05c5aead03f37fd](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/loader/ncch.cpp): el emulador añade BSS redondeada a páginas detrás del segmento de datos redondeado. El plan usa como comienzo `15466496 + 1843200 = 17309696`, y como extensión declarada 636.332 bytes. El muestreo toma 32 bytes cada 4 KiB: 4.992 bytes únicos de BSS, no un volcado completo. Excluye heap, VRAM y padding posterior a la extensión declarada.

La ventana 139 empieza en `17309696 + 139×4096 = 17879040`, equivalente a `0x0110D000`. Entre las dos pasadas cambiaron los índices 0, 4, 5, 8 y 9 dentro de sus 32 bytes. El seguimiento posterior demuestra variación del rango mediante hashes, sin localizar cuáles de sus bytes cambiaron en cada muestra posterior. No se infiere un tipo de dato por el patrón de índices.

Las pasadas y lecturas son secuenciales, no snapshots atómicos. No se cronometraron acciones del jugador ni se realizó una nueva comprobación visual de la escena en estos ensayos. La variación no establece una relación causal con acciones del juego.

## Búsqueda estática y límites

`follow_citra_candidates.py` también busca palabras u32 little endian alineadas a cuatro bytes cuyo valor cae dentro de las ventanas candidatas. Encontró 547 coincidencias: 537 en el segmento de código y diez en datos. El candidato 114 concentra 523; los candidatos 32, 110, 125, 276, 398 y 408 tienen diez, siete, una, dos, una y tres respectivamente. Los otros cinco no tienen coincidencias de esta clase.

**No son referencias de instrucciones confirmadas.** En código, una palabra puede ser una instrucción o parte de un pool de literales; en datos puede ser un puntero o una coincidencia. No se desensambló ni siguió un flujo de ejecución. Una búsqueda equivalente del rango BSS variable no encontró coincidencias, lo cual tampoco demuestra ausencia de referencias: pueden calcularse direcciones base/desplazamiento o existir referencias indirectas.

## Cambios de herramientas y verificación

- Nuevo `follow_citra_candidates.py`: valida hashes de imagen, mapa, protocolo, índice y binario de la etapa previa; comprueba que los candidatos pertenecen al segmento de datos con backing correcto. Presupuesto máximo de extracción 128 KiB, límite 20 solicitudes/s, hasta 60 segundos y parada por cuatro errores consecutivos o control distinto. Guarda índice, bytes privados, hashes y diferencias respecto a la muestra válida previa. No incluye escrituras RPC.
- `sample_citra_data_windows.py` admite ahora `--region bss` además de su modo de datos. Verifica tamaño y final del backing antes de derivar BSS. Sus ventanas BSS tienen `file_offset: null` y `matches_static: null`; no se presenta la ausencia de backing como un archivo de ceros con el que deban coincidir.
- Cinco pruebas nuevas del seguimiento pasaron. La suite del muestreador modificado pasó nueve pruebas, incluidas sus siete anteriores y dos nuevas sobre derivación BSS y ausencia de comparación estática. No se presenta esto como catorce pruebas nuevas ni como una repetición de toda la batería histórica.
- Se releyeron y verificaron los hashes, offsets y tamaños de los 520 y 314 fragmentos privados. La diferencia de cinco posiciones de BSS y los conteos temporales del seguimiento se recalcularon desde los archivos guardados. Esta es una comprobación de integridad/consistencia, no un segundo método independiente de interpretación.

Original `.3ds`, banco de recursos, consola, firmware, plugins y montajes no se modificaron. No se usó FTP, no se instaló otro emulador y no se publican bytes de memoria, capturas o logs brutos. Citra permanece abierto; los lectores terminaron.

## Reproducción

```text
python tools/stt_re/follow_citra_candidates.py --prior <carpeta-sondeo-datos-450-ventanas> --image <code.bin-verificado> --mapping <recibo-MH4U-code-BLZ.json> --out <carpeta-privada-nueva> --cycles 40 --rate 20 --seconds 40

python tools/stt_re/sample_citra_data_windows.py --mapping <recibo-MH4U-code-BLZ.json> --image <code.bin-verificado> --out <otra-carpeta-privada-nueva> --region bss --rate 20 --seconds 30

python tools/stt_re/observe_citra_session.py --log <perfil>/log/citra_log.txt --out <tercera-carpeta-privada-nueva> --seconds 12 --interval 0.1 --address 17879040 --size 32
```

Estas direcciones solo corresponden a la base MH4U y al mapa documentados. No aplicarlas al update MHXX ni a otra compilación sin rehacer su mapeo. En este entorno se utilizó el anfitrión autorizado para el RPC local, por el aislamiento de red observado previamente.

## Próxima prioridad

Comparar el rango BSS variable en reposo y durante una sola acción reconocida, con marcadores temporales y varias repeticiones. Primero comprobar si varía también sin entrada; eso evita confundir un temporizador con un estado de combate. Solo después ampliar el entorno del rango o interpretar campos mediante referencias y trazas. La lista de candidatos del segmento de datos permanece documentada, pero repetirla sin cambiar las condiciones no ha aportado variación.

# Primera interpretación de campos en ejecución — 22-10-2026

## Resultado

Los campos de 32 bits little endian en `0x0110D004` y `0x0110D008` avanzan a unas 60 unidades por segundo de tiempo del host mientras la emulación funciona, permanecen fijos en pausa y vuelven a avanzar al continuar. Traducción provisional: **dos candidatos a contador periódico ligados al avance de la emulación**. La hipótesis de contador de frames es compatible, pero no se ha probado equivalencia de un incremento con un frame ni se conoce la función de cada campo. Son iguales en las 160 muestras con emulación funcionando; durante las 80 muestras pausadas, el campo +8 permanece una unidad por debajo del campo +4. No se llaman copias idénticas ni se atribuye ese desfase a una instrucción concreta.

| Condición comprobada | Muestras correctas | Cambios por campo | Unidades/s del host |
| --- | ---: | ---: | ---: |
| Primer intento de pausa, no pausó | 80 | 79/79 | 59.7878 |
| Pausa confirmada, Citra a 0 FPS | 80 | 0/79 | 0.0000 |
| Continuación, Citra volvió a 60 FPS | 80 | 79/79 | 59.7952 |

Todos los controles de código antes/después coincidieron; cero errores RPC. La primera llamada F4 con el menú abierto no pausó y se conserva como intento fallido, aunque el nombre privado de la carpeta diga paused. Se pausó después seleccionando Pausar desde el menú, se confirmó 0 FPS, y se reanudó con Continuar. La captura inmediata tras Continuar mostró estado visual transitorio; las lecturas volvieron a avanzar y la comprobación posterior confirmó 100 % y 60 FPS.

## Comparación de movimiento

Se creó `capture_citra_bss_block.py`: lee exclusivamente un bloque de 32–8192 bytes íntegramente dentro de la BSS derivada del mapa y de la imagen estática verificada por hash. Solicitudes ReadMemory de 32 bytes, máximo 20 por segundo, controles de código antes/después, directorio exclusivo, índices y hashes. No sigue punteros ni toca VRAM.

Se tomaron cuatro bloques de 4096 bytes desde `0x0110CC00`: reposo A, reposo B, después de derecha un segundo y después de izquierda un segundo. Los desplazamientos se confirmaron por imágenes antes/después; no se certificó regreso a las mismas coordenadas. Total: 512 lecturas del bloque, 16384 bytes privados y ocho controles de código; sin errores. Los bloques no son instantáneas atómicas y cada uno tarda unos 6,5 segundos.

Ocho palabras alineadas variaron entre fases: `0x0110CEC0`, `0x0110CF4C`, `0x0110CF50`, `0x0110CFFC`, `0x0110D000`, `0x0110D004`, `0x0110D008` y `0x0110D018`. Ninguna permaneció estable entre las dos lecturas de reposo y cambió sólo después del movimiento. **No se identificaron posición, dirección, hitbox o animación** en este bloque. La ausencia de candidatos aquí no prueba que no existan en otras regiones.

## Herramienta de interpretación reproducible

`translate_citra_counter.py <carpeta de record_citra_target>` valida los hashes del binario, índice, protocolo y cada muestra, exige controles correctos, y calcula diferencias modulares u32, tasa observada e igualdad de ambos campos. No convierte automáticamente unidades a segundos del juego ni decide la identidad del campo. Se añadieron tres pruebas de límites BSS y cuatro de resumen: frecuencia con desbordamiento u32, congelación, rechazo de tiempos inválidos y campos congelados desiguales. Siete pruebas correctas, sin contarlas de nuevo por repetir su ejecución.

## Prioridad siguiente y bloqueos

1. Verificar la hipótesis de frames con avance individual de frames documentado o una traza de las instrucciones que escriben ambos campos. Cambiar la velocidad por sí solo no identifica la función de cada copia.
2. Buscar coordenadas en regiones con propietario/asignación demostrados: este vecindario BSS no aportó candidatos. Antes de seguir un valor como puntero se necesita una asignación válida y límites, no sólo que parezca una dirección.
3. Repetir secuencias cortas reposo/movimiento opuesto, manteniendo la misma zona y separando NPC, cámara y animación ambiental mediante controles negativos.

El resultado es una interpretación conductual parcial, no descifrado completo ni traducción lingüística de textos. No se escribieron valores de memoria; sólo se controló el juego con las flechas autorizadas y se pausó/reanudó Citra. Datos comerciales brutos siguen privados. Citra quedó ejecutando la partida, lectores terminados y teclas liberadas.

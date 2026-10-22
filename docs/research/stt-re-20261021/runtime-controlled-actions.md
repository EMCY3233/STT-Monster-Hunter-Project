# Reposo, caminar y acciones controladas por el asistente — 22-10-2026

## Resultado actual

Se confirmó control táctil de la partida local de MH4U en Val Habar: abrir Menu, seleccionar Combine, cerrar Menu y ejecutar el gesto **Wave**. Wave se resaltó y el personaje cambió de pose. El ensayo ampliado de 60 segundos obtuvo **598 lecturas correctas** del rango de 32 bytes `0x0110D000`; la pulsación Wave y la observación visual posterior ocurrieron dentro de esa captura. Los intentos con Right, Left y M no produjeron movimiento o apertura de menú confirmados; no se contabilizan como desplazamientos realizados.

Los datos **no identifican un campo de movimiento o animación**. En particular, el campo a +24 bytes (`0x0110D018`, leído como patrón u32 little endian) varió también antes de entradas del asistente. La coincidencia inicial con caminar no basta para usarlo como detector de movimiento. No se interpretaron instrucciones ni se desreferenciaron supuestos punteros.

## Comparación manual declarada por el usuario

El usuario confirmó reposo inicial, eligió caminar a la derecha y confirmó después que el personaje había caminado y vuelto a quedar quieto. Cada fase duró doce segundos. La coordinación se hizo por mensajes y no por fotogramas; no hubo comprobación visual independiente de toda la acción manual.

| Fase | Muestras válidas | Errores | Cambios del patrón u32 a +24 |
| --- | --- | --- | --- |
| Reposo anterior | 120 | 0 | 0 de 119 pares |
| Caminar a la derecha, declarado y confirmado por el usuario | 120 | 0 | 11 de 119 pares |
| Reposo posterior | 120 | 0 | 0 de 119 pares |

El patrón constante del reposo posterior **no fue igual** al del reposo anterior y no apareció en las muestras de caminar. No se afirmó una vuelta al valor original. Los patrones de +4 y +8 fueron iguales entre sí en todas las muestras de estas tres fases y avanzaron aproximadamente 59,9 unidades por segundo del anfitrión, también sin entrada. Esto respalda la hipótesis de contadores periódicos; no confirma qué cuentan ni que equivalgan exactamente a frames del juego.

La vista u32 es una manera de comparar bits, no un tipo de campo deducido. Las estadísticas usan diferencias módulo 2³² para no confundir un desbordamiento con una discontinuidad arbitraria. Los valores absolutos y bytes de memoria permanecen privados.

## Entradas automáticas y cobertura temporal real

Se registraron intervalos UTC para el inicio de cada llamada, su retorno y el retorno de la captura visual. Se contrastaron con las horas de cada lectura. La observación de pantalla permite comprobar aceptación de una entrada, pero no da el instante exacto del frame que la procesó.

| Campaña | Lecturas válidas | Cambios a +24 | Cobertura comprobada |
| --- | --- | --- | --- |
| Intento de teclado, 30 s | 300 | 29 | Foco y pulsación Right dentro de la captura; observación posterior a Right, Left y M fuera de ella. No se confirmó movimiento. |
| Menú táctil, 20 s | 200 | 23 | Apertura de Menu y su observación dentro. Selección Combine y cierre observados después de terminar la lectura. |
| Primer Wave, 30 s | 299 | 4 | Apertura de Gestures dentro; Wave ocurrió después del cierre de esta captura. No se atribuyen estas muestras al gesto. |
| Repetición Wave, 60 s | 598 | 29 | Gestures a ~17,05 s; Wave entre ~28,06 y ~28,47 s; observación de pose a ~28,98 s. Todas dentro. Cierre posterior de Gestures fuera de la captura. |

La primera campaña de Wave fue temporalmente insuficiente. Se conservó y se repitió con una ventana mayor; no se corrigieron sus marcas ni se reasignaron muestras a una acción que ocurrió fuera. En la repetición ampliada hubo **13 cambios a +24 entre 170 muestras anteriores a la primera entrada del asistente**. En la campaña de Menu también hubo 18 cambios entre 155 muestras previas a esa entrada. Son intervalos anteriores a mis acciones, no una prueba de ausencia de toda actividad del juego. No se atribuyen los cambios a Wave, al menú o a caminar por la mera cercanía temporal.

Las capturas se inspeccionaron en el entorno privado y no se publican. La anotación textual del resultado visual se escribió después de observar; su hora de escritura no sustituye la hora de retorno de la observación guardada con la acción.

## Herramienta y evidencia

`record_citra_target.py` registra una única ventana de 32 bytes elegida del plan BSS previamente verificado. Revalida hashes de mapa, imagen y protocolo; deriva de nuevo el plan BSS para comprobar la dirección. Comprueba cuatro bytes de código antes y después. Solo admite RPC ReadMemory, intervalos de 0,1–1 s y duración de hasta 60 s, con parada por cuatro errores consecutivos. Etiqueta condiciones declaradas por el usuario, entradas del asistente o condición no controlada sin convertir la etiqueta en una verificación independiente.

Guarda bytes privados, índice de lectura, hashes, UTC de inicio y tiempos relativos de inicio/fin. Las estadísticas incluyen posiciones de byte cambiantes y conteos de patrones/diferencias u32; no nombres de estructuras. No son snapshots atómicos. Cada una de las siete capturas de esta etapa tuvo controles coincidentes antes y después; esos dos controles por captura son adicionales a las muestras de la tabla.

Cuatro pruebas sintéticas pasaron: desbordamiento modular, campos constantes, tamaños incorrectos y rechazo de parámetros fuera del límite antes de leer archivos. Se reejecutaron al ampliar el límite de treinta a sesenta segundos; no son ocho pruebas diferentes. Se verificaron los hashes e índices de cada muestra guardada y se recalcularon sus estadísticas sin repetir capturas.

La evidencia JSON separa la comparación manual de las cuatro campañas del asistente, e incluye cobertura de cada acción dentro/fuera de su captura. Los recibos individuales del lector conservan `action_effect_verified: false`: el lector por sí solo no observa la pantalla. El agregado documenta por separado las acciones visuales confirmadas y mantiene `causal_effect_verified: false`.

Reproducción del registro ampliado, con los mismos archivos MH4U verificados y una carpeta privada nueva:

```text
python tools/stt_re/record_citra_target.py --prior <carpeta-sondeo-BSS> --image <code.bin-MH4U> --mapping <recibo-code-BLZ-MH4U.json> --out <carpeta-nueva> --condition assistant-issued-action --window 139 --seconds 60 --interval 0.1
```

Observar la pantalla actual antes de cada entrada; abrir Gestures, pulsar Wave y verificar la pose. Guardar un intervalo UTC por llamada y comprobar después que la entrada y su observación quedaron dentro de las lecturas. No reutilizar coordenadas de una pantalla diferente ni prolongar una lectura terminada mediante una etiqueta retrospectiva.

## Límites y siguiente experimento

El control táctil ya permite provocar una acción visible mientras se lee memoria. El control por teclado de este frente sigue sin aceptación visual: hay que resolver duración/foco antes de afirmar desplazamientos automáticos. No se usó inyección de memoria para suplirlo.

Los campos periódicos +4/+8 pueden servir como referencias de progresión **solo como hipótesis pendiente de comprobar**, no como reloj de frames certificado. +24 no es específico de caminar en estos ensayos. Antes de ampliar su entorno conviene repetir Wave y una acción de control con ventanas iguales, registrar reposo en la misma escena y buscar diferencias reproducibles que no aparezcan antes de la entrada. Después será necesario encontrar referencias o trazas que justifiquen una interpretación.

La partida quedó abierta con los paneles cerrados. Los lectores terminaron. No se modificaron originales, banco de recursos, firmware, plugins, montajes ni consola; no hubo FTP, nuevas instalaciones ni publicación de capturas, logs o bytes comerciales.

## Revisión posterior: duración de teclas y teclado digital

El usuario autorizó probar el teclado en pantalla de Windows y después pidió probar primero teclas normales sostenidas. Se abrió el teclado digital preexistente y se inspeccionó, pero **no se pulsó ninguna de sus teclas**. El intento de volver a enfocar Citra devolvió `user input was detected in this window; call get_window_state before continuing`; no se actuó desde un estado anterior ni se continuó con las flechas digitales.

La API documentada del control nativo disponible (`PressKeyInput`) expone `key` y `window`, sin parámetro de duración ni operaciones separadas de key-down/key-up. Por tanto, la prueba automática de tecla normal sostenida quedó **sin ejecutar**. No se simula una retención mediante una espera después de una pulsación breve ni se declara resuelta la hipótesis de duración. El usuario había confirmado que el teclado normal sí permitió caminar en la prueba manual.

La lectura de 60 segundos que ya había arrancado para el ensayo digital terminó con 598 respuestas correctas y controles coincidentes. No hubo teclas digitales enviadas ni acción de juego del asistente durante esa lectura; se conserva la etiqueta planificada del protocolo, pero el agregado la marca como ensayo sin actuación. El campo +24 cambió 41 veces. Esto refuerza la necesidad de no interpretar ese campo como exclusivo de caminar. No se atribuye esa variación al teclado en pantalla ni se afirma ausencia de toda entrada externa.

En un intento posterior, tras la indicación del usuario de usar las flechas del stick de movimiento, se envió una llamada de clic hacia la zona observada de **Right en el teclado digital**. Se reobservó el estado después de detectar intervención del usuario y se puso el foco en Citra antes del intento. **No se confirmó visualmente la activación de la tecla ni el desplazamiento**; el usuario indicó que no vio utilizar las flechas. El retorno de la llamada no demuestra una pulsación recibida por el teclado o por Citra. Esa segunda lectura obtuvo otras 598 respuestas correctas; el intento de clic quedó entre aproximadamente 47,66 y 48,11 segundos, dentro de la captura de 60 segundos. No se confunde esta prueba con la anterior sin actuación ni con el stick C: el perfil asigna el stick de movimiento a las flechas y el stick C a I/J/K/L.

Se devolvió el foco a Citra al terminar; el teclado digital permaneció abierto y no quedó una tecla retenida. La prueba automática de tecla normal sostenida y el desplazamiento por teclado de este frente siguen pendientes; no se modificó el mapeo ni se afirmó que el teclado digital resolviera el problema.

Finalmente se probó mantener Citra en primer plano y enviarle directamente dos pulsaciones Right y una Down, sin activar el teclado digital. Tampoco se confirmó desplazamiento en las observaciones. La lectura asociada obtuvo 599 respuestas correctas en sesenta segundos, sin errores y con controles coincidentes. Estas son pulsaciones breves, no una prueba de retención de tecla. El foco por sí solo no resolvió el control automático en el ensayo; no se concluye que el juego o el teclado físico del usuario estén averiados.

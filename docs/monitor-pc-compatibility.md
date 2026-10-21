# Monitor PC — compatibilidad y ensayo conjunto

## Dependencias

PR #13 añade la vista `--live`; PR #14 añade el resumen temporal. PR #16 añade duración máxima y ensayo conjunto. Los límites de recursos se basan en #16, sin fusionar ninguna de ellas. Compatible con el agente Vita 0.5 instalado: no cambia STT/1, STT/2, puertos ni JSONL. Amplía las opciones CLI del receptor y los campos del resumen del analizador.

## Matriz de comportamiento

| Caso | Vista en directo | Analizador / evidencia |
|---|---|---|
| STT/1 simulado | Muestra, sesión y batería; sin diagnóstico | Conserva secuencia y tiempos disponibles; sin diagnóstico inventado |
| STT/2 / agente 0.5 | Contadores previos y último error conservado | Diagnóstico de mayor secuencia recibida |
| Nueva sesión con error conservado | Contadores pueden ser cero con código anterior | Sesiones separadas por IP, origen y sesión; no se atribuye nuevo fallo |
| Duplicado o llegada fuera de orden | Muestra cada recepción | Cuenta duplicados/desorden; conserva el registro recibido |
| Salto hacia delante del reloj PC | Hora de recepción observada | Mayor intervalo con secuencias y delta de uptime; sin atribuir suspensión/latencia |
| Retroceso del reloj PC | Hora de recepción observada | Cuenta retrocesos; excluye intervalos negativos del máximo |
| Hora ausente/inválida/sin zona en JSONL | No altera la captura original | Paquete válido se conserva; interrumpe comparación temporal de esa sesión |
| Datagrama truncado o inválido | No aparece como muestra aceptada | Receptor lo rechaza; línea JSONL inválida cuenta en invalid_lines |
| Parada Vita o silencio | No se deduce estado de parada | STT/2 no transmite parada ni presupuesto RTC |
| Límite PC | Duración, inactividad o máximo de muestras | Cierre del receptor y archivo; no demuestra parada del emisor |

## Reproducción sin consola

Desde la raíz del repositorio, con Python 3.11 o posterior:

```powershell
python -m unittest discover -s tests -v
python tests/smoke_cli.py
python tests/smoke_diagnostics.py
python tests/smoke_limits.py
```

`smoke_diagnostics.py` crea receptor y emisor en dos procesos independientes, solo en loopback puerto 32110, con archivo temporal. Todos sus paquetes son sintéticos, incluso `source=vita`, utilizado para probar el contrato. Espera cinco muestras aceptadas y dos datagramas inválidos rechazados; secuencias 0,2,2,1 y una nueva sesión con 0. Confirma cierre correcto, conservación JSONL y diagnóstico histórico con contadores reiniciados. Los saltos de reloj se inyectan después en copias en memoria para el analizador, sin cambiar el reloj del equipo ni registros de hardware. Añade dos líneas truncadas/inválidas al análisis; no se escriben al archivo de captura.

`smoke_limits.py` usa loopback puerto 32112 para comprobar cuota, contenido previo intacto, informe parcial y rechazo de anexado sin LF. `smoke_cli.py` cubre STT/1 con diez muestras. Los retrocesos del reloj en el análisis y los límites temporales del receptor también se prueban de forma determinista: no dependen de dormir largos periodos ni de tocar el Wi-Fi.

## Memoria, duración y disco

El receptor procesa un datagrama cada vez, de máximo 1024 bytes, y no acumula historial en memoria. `--live` no añade una colección de sesiones ni muestras. El consumidor de stdout puede acumular sus propias copias, fuera del receptor.

`--duration N` acepta un plazo positivo de hasta 3600 s, medido con reloj monotónico del PC. Se usa el menor plazo entre duración total e inactividad para esperar en el socket, y se comprueba la duración antes de procesar una nueva muestra. Tráfico válido o inválido no amplía ese plazo total. Es una parada cooperativa del proceso, no una garantía de planificación en tiempo real; una escritura o salida bloqueada puede retrasar el retorno. La opción se omite por defecto para mantener compatibilidad.

El CLI comprueba antes de abrir el socket que un archivo existente vacío o no vacío termine en LF si contiene datos (también admite CRLF). Si falta LF, devuelve error 2 y pide elegir otro `--output`, sin cambiar ni reparar el archivo. Esto evita pegar una nueva muestra a una línea incompleta o a un objeto JSON completo sin separador. Solo comprueba la frontera final, no valida el historial; la API `receive` requiere que su stream de salida esté ya en una frontera de registro. Sigue requiriendo uso exclusivo del archivo, sin protección frente a cambios de otros procesos entre comprobación y apertura.

El archivo sigue siendo append-only, sin rotación. La cuota por defecto `--max-bytes 10485760` (10 MiB) incluye el tamaño existente al abrir. Cada nuevo registro se mide en UTF-8 con LF; se escribe entero o se detiene antes de él. Al alcanzar la cuota, el resumen incluye `stop_reason=max_bytes`, `bytes_written` de esta ejecución y `not_recorded`: 1 si un datagrama válido recibido no cabía, 0 si se paró antes de leer o justo al llenar el límite. `accepted` cuenta solo registros guardados, `rejected` solo datagramas inválidos. No se trunca un archivo preexistente que ya supere la cuota ni se añade nada a él. Requiere uso exclusivo del archivo; no coordina escritores externos. El límite no es una cuota del sistema de archivos ni soluciona fallos de disco.

El analizador guarda por defecto hasta 1000 sesiones y 100000 secuencias únicas globales. Son límites de cardinalidad, no bytes RAM medidos. Se pueden ajustar con `--max-sessions` y `--max-unique`, enteros positivos; las duplicadas no consumen otro identificador. Al primer registro válido que excedería un límite, no se incluye ese registro ni se sigue leyendo: devuelve `partial=true`, `stop_reason=max_sessions|max_unique`, `processed_packets` y `limits`. Exactamente alcanzar el límite al EOF no marca parcial. `partial=false` significa que terminó la entrada, no que todos sus registros fueran válidos.

Conteos de muestras, duplicados, desorden, huecos internos y diagnósticos siguen siendo exactos **para el prefijo incluido**, nunca para el resto omitido ni para entregas UDP reales. `invalid_lines` cubre solo líneas examinadas hasta la parada. El mayor intervalo temporal corresponde a las recepciones incluidas, no es una estimación de la pausa máxima de toda la captura. El CLI termina correctamente con un JSON parcial; los consumidores deben comprobar `partial`.

El lector CLI usa bloques de como máximo 4097 bytes para drenar líneas de más de 4096 bytes sin acumularlas, y cuenta una línea demasiado grande o con UTF-8 inválido una sola vez como inválida. No cambia los archivos. La API `summarize` también rechaza entradas superiores a ese tamaño; no puede controlar la memoria que el llamante haya reservado antes de entregarlas. Estos límites acotan estado retenido/entrada por línea, no garantizan un máximo de RAM del intérprete ni se han medido como tal. No es una prueba de rendimiento sostenido o resistencia a tráfico hostil.

## Estado

26 pruebas locales y ensayo de cuota/anexado correctos en la corrección de frontera; ensayos conjunto y STT/1 aprobados en su base; validación remota registrada en la PR. Las pruebas físicas pendientes de límite sin red durante suspensión y fallos/retrocesos RTC permanecen pendientes. Esta entrega no requiere FTP, instalación, firmware/plugins ni acceso a banco u originales.

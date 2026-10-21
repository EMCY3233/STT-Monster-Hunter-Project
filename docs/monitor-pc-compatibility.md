# Monitor PC — compatibilidad y ensayo conjunto

## Dependencias

PR #13 añade la vista `--live`; PR #14 añade el resumen temporal. Esta mejora se basa en #14, sin fusionar ninguna de ellas. Compatible con el agente Vita 0.5 instalado: no cambia STT/1, STT/2, puertos ni JSONL. Amplía las opciones CLI del receptor y los campos del resumen del analizador.

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
```

El último ensayo crea receptor y emisor en dos procesos independientes, solo en loopback puerto 32110, con archivo temporal. Todos sus paquetes son sintéticos, incluso `source=vita`, utilizado para probar el contrato. Espera cinco muestras aceptadas y dos datagramas inválidos rechazados; secuencias 0,2,2,1 y una nueva sesión con 0. Confirma cierre correcto, conservación JSONL y diagnóstico histórico con contadores reiniciados. Los saltos de reloj se inyectan después en copias en memoria para el analizador, sin cambiar el reloj del equipo ni registros de hardware. Añade dos líneas truncadas/inválidas al análisis; no se escriben al archivo de captura.

La prueba STT/1 de dos procesos cubre diez muestras. Los retrocesos del reloj en el análisis y los límites temporales del receptor también se prueban de forma determinista: no dependen de dormir largos periodos ni de tocar el Wi-Fi.

## Memoria, duración y disco

El receptor procesa un datagrama cada vez, de máximo 1024 bytes, y no acumula historial en memoria. `--live` no añade una colección de sesiones ni muestras. El consumidor de stdout puede acumular sus propias copias, fuera del receptor.

`--duration N` acepta un plazo positivo de hasta 3600 s, medido con reloj monotónico del PC. Se usa el menor plazo entre duración total e inactividad para esperar en el socket, y se comprueba la duración antes de procesar una nueva muestra. Tráfico válido o inválido no amplía ese plazo total. Es una parada cooperativa del proceso, no una garantía de planificación en tiempo real; una escritura o salida bloqueada puede retrasar el retorno. La opción se omite por defecto para mantener compatibilidad.

El archivo sigue siendo append-only, sin rotación ni cuota de bytes. Ni duración ni muestras limitan el tamaño de un archivo ya existente. El analizador guarda las secuencias únicas de cada sesión: su memoria crece con esa cardinalidad; no existe una cuota automática. Usar capturas acotadas y no equiparar esta revisión a una prueba de rendimiento sostenido o resistencia a tráfico hostil.

## Estado

20 pruebas locales y ensayo conjunto correctos al publicar; validación remota registrada en la PR. Las pruebas físicas pendientes de límite sin red durante suspensión y fallos/retrocesos RTC permanecen pendientes. Esta entrega no requiere FTP, instalación, firmware/plugins ni acceso a banco u originales.

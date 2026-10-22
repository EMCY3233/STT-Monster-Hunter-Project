# Revisión offline de interoperabilidad STT — 21-10-2026

## Resultado
Se ejecutaron **15casos sintéticos,15correctos,0fallos**,sin sockets,UDP ni acceso a consola. Se compararon los módulos vigentes del monitor con las fuentes de la rama prototype/vita-3d-20261021,referenciadas por hash en el [recibo](protocol-interop-review.json).

| Entrada/composición | Monitor vigente STT/1–2 | Código candidato de prototipos |
|---|---|---|
|STT/1,batería50.5 |Aceptado,97bytes |Aceptado,97bytes |
|STT/2,diagnósticos |Aceptado,171bytes |Aceptado,171bytes |
|STT/3,snapshot |Rechazado:unsupported version |Aceptado,386bytes |
|STT/3,impacto |Rechazado:unsupported version |Aceptado,432bytes |
|ClavesJSONduplicadas |Rechazado |Rechazado |
|Entrada1025bytes |Rechazado |Rechazado |

Un caso válido ampliado con sesión de64caracteres,valores grandes y2impactos ocupó715bytes. Es una muestra concreta,no una prueba exhaustiva del tamaño máximo de todos los paquetes posibles.

El analizador vigente rechaza las2líneasSTT/3 con su validador actual. Al componer ese mismo código de analizador con el validador candidato,cuenta una sesión y2paquetes,sin líneas inválidas. Esto es una composición de prueba en memoria,no un cambio instalado ni una fusión. El resumen no calcula estadísticas de combate.

## Qué queda demostrado y qué falta
- La ampliación Python probada acepta los ejemplosSTT/3 y conserva los casosSTT/1–2 ensayados.
- Un receptor vigente no debe presentarse como compatibleSTT/3 antes de integrar su soporte explícito. Su rechazo actual es deliberado,no un fallo nuevo.
- El productor Vita inspeccionado ofrece muestras a un buzón local. No se observó un envíoUDP en su bucle y su documentación declara transporte pendiente.
- Este recorrido no compila el encoderC,no ejecuta VPK ni valida hardware,pérdidas reales de red,suspensión o rendimiento.
- Sesiones,secuencias,origen,unidades y eventos no adquieren autenticación por pasar el validador.
- Mantener independientes la revisión del esquema/receptor y la futura implementación/validación del emisorUDP. No fusionar ni instalar por este informe.

## Reproducción
Con copias de las fuentes propias del proyecto identificadas en el recibo:
```powershell
python tools/check_protocol_interop.py --baseline ../repository/stt_monitor --candidate ../analysis-local/protocol-review-20261021/candidate --snapshot ../analysis-local/protocol-review-20261021/snapshot.json --hit ../analysis-local/protocol-review-20261021/hit.json --report ../analysis-local/logs/protocol-interop-new.json
```
El destino debe ser nuevo. La herramienta carga y ejecuta únicamente los módulos Python de proyecto indicados,abre los archivos fuente en lectura y desactiva escritura de bytecode. No proporcionar directorios de código ajeno sin revisarlo. Los módulos fuente comparados se identifican porSHA-256; las copias candidatas incluyen también blobGit en el recibo.

[Herramienta propia](../../../tools/check_protocol_interop.py). Fuentes:[contratosPR8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/8),[prototipoPR11](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/11). La revisión se comunicó al chat coordinador de prototipos,sin modificar sus archivos,el monitor,el banco o los juegos.

# Ampliación de lectura y extracción — 22-10-2026

Estado posterior: [seguimiento de candidatos y BSS](runtime-bss-followup.md). El ensayo de datos descrito aquí se conserva; la nueva etapa añade un modo BSS delimitado por el loader y encuentra un rango variable. Sus resultados no convierten esta captura anterior en un volcado de BSS.

## Resultado implementado y ejecutado

`tools/stt_re/sample_citra_data_windows.py` amplía el lector RPC v1 existente. En vez de repetir solo el inicio del segmento de datos, construye ventanas reproducibles a partir del mapa ExHeader previamente verificado: 32 bytes al inicio de cada página de 4 KiB, sin salir de los bytes declarados del segmento. Revalida el hash de todo el `.code` estático antes de leer. Cada pasada empieza con un control de cuatro bytes de código; un control distinto detiene la captura.

| Medida del ensayo MH4U | Resultado |
| --- | --- |
| Ventanas de datos por pasada | 450 |
| Pasadas completadas | 2 |
| Lecturas correctas / errores | 902 / 0 |
| Duración medida en anfitrión | 45,797 s |
| Bytes extraídos, controles incluidos | 28.808 |
| Bytes únicos del segmento de datos muestreados | 14.400 de 1.842.044 (0,782 %) |
| Ventanas distintas del archivo estático, por pasada | 12 de 450 |
| Ventanas que cambiaron entre las dos muestras | 0 de 450 |

**Las doce diferencias respecto al archivo son una nueva lista de candidatos; no son cambios observados durante el juego.** Las doce permanecieron estables entre pasadas. Su causa puede incluir inicialización o estado de ejecución; no se ha identificado su semántica. Direcciones, offsets e índices de diferencias figuran en la evidencia JSON, sin valores comerciales. Las otras 438 ventanas coincidieron con el archivo estático. No se cronometraron acciones del jugador ni se confirmó una escena de combate en este ensayo.

No es un volcado completo: se omiten los 4.064 bytes restantes de cada página, BSS, heap, VRAM y otras regiones. Las lecturas son secuenciales; cada pasada tarda aproximadamente 23 segundos. Una variación transitoria puede quedar entre muestras. Que no se observaran cambios no implica que el estado completo fuera estático.

## Mejoras prácticas

- Extracción binaria privada más un índice de cada lectura: dirección virtual, offset dentro del binario de muestras, tamaño, hash, comparación estática y tiempos de inicio/fin. Los huecos entre ventanas no se rellenan ni se presentan como memoria leída.
- Comparación únicamente entre ventanas leídas correctamente en ambas pasadas. Las lecturas ausentes se contabilizan como no emparejadas; no equivalen a estabilidad.
- Límites: 1–20 solicitudes/s, hasta 60 segundos, dos o tres pasadas y presupuesto total de extracción de 128 KiB. Parada por cuatro errores consecutivos o discrepancia del control. El ritmo se cuenta por solicitud, no por bytes.
- Protocolo guardado antes de la primera solicitud; directorio de salida nuevo y hashes de protocolo, índice de lecturas y binario final. Solo se emite ReadMemory hacia 127.0.0.1; no se escanean procesos del anfitrión.
- Siete pruebas sintéticas nuevas pasaron: límites de rango, final parcial de página, exclusión de huecos, diferencias con lecturas ausentes, offsets de extracción, rechazo de hash incorrecto, parada por control y por errores (algunas propiedades comparten prueba). No se repitió la batería histórica completa.

Los archivos brutos están en `analysis-local/citra-sparse-data-20261022-001`, fuera de publicación. El banco de recursos y los originales no se modificaron. La captura terminó; no se dejó un monitor permanente.

## Investigación de protocolos y alternativas

| Opción | Hecho verificado en fuente primaria | Aplicación y límites |
| --- | --- | --- |
| Citra Nightly 2104, commit `0ff3440232d6bc9226e37c41c05c5aead03f37fd` | [packet.h](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/rpc/packet.h): protocolo 1, carga máxima de 32 bytes. [rpc_server.cpp](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/rpc/rpc_server.cpp): lectura asíncrona respecto al emulador. | Es el protocolo ensayado. Aumentar el tamaño del paquete del cliente no crea soporte para lecturas mayores. No proporciona una instantánea atómica ni un marcador de frame. |
| Azahar 2126.2, commit `219d743a1e698101fe1ab8bef43e6563126c3c27` | [packet.h](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/rpc/packet.h): protocolo 2, hasta 32 KiB, selección de proceso, capturas y estadísticas. [Release](https://github.com/azahar-emu/azahar/releases/tag/2126.2) anuncia ruptura de compatibilidad del cliente RPC. | Candidato para otra instalación aislada y otro cliente, no mejora automáticamente Citra. No instalado ni ejecutado en esta etapa. La [fuente del servidor](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/core/rpc/rpc_server.cpp) condiciona sincronización a `ENABLE_SCRIPTING_SYNC`; no se comprobó cómo está compilado el binario de distribución. |
| Sincronización / GDB | [Issue primario #2619](https://github.com/azahar-emu/azahar/issues/2619) describe fallos al leer memoria atendida por el rasterizador y propone atender peticiones en el hilo de emulación, como GDB. El issue está cerrado; ese estado no demuestra que el Citra local tenga una corrección. | Mantener la lectura fuera de VRAM. Para un volcado coherente, evaluar pausa y depuración sincronizada con un ensayo separado; no afirmar atomicidad por usar hashes. GDB local sigue sin probarse y no se habilitó ni se reinició el juego. |
| PPSSPP 1.20.4, commit `fa50bb1976065c4f8b1b47af227d367fe9771555` | [MemorySubscriber.cpp](https://github.com/hrydgard/ppsspp/blob/fa50bb1976065c4f8b1b47af227d367fe9771555/Core/Debugger/WebSocket/MemorySubscriber.cpp): `memory.read` acepta dirección/tamaño, valida el rango y responde Base64; parámetro `replacements` controla las sustituciones. [InputSubscriber.cpp](https://github.com/hrydgard/ppsspp/blob/fa50bb1976065c4f8b1b47af227d367fe9771555/Core/Debugger/WebSocket/InputSubscriber.cpp): pulsaciones con duración y seguimiento por vblanks. | Para MHFU, permite diseñar extracción por bloques y entrada delimitada sin depender del foco de Windows. Capacidades documentales: no se abrió el debugger ni se envió entrada en esta etapa. Vblank no equivale necesariamente a un frame de juego. [Documentación oficial del API](https://www.ppsspp.org/docs/reference/websocket-api/). |

El informe de fallos de GPU se refiere a builds y condiciones concretas de Azahar; no se reprodujo aquí ni se afirma que toda lectura RPC de Citra falle. El propio servidor Citra sí confirma asincronía. Por eso esta ampliación conserva rangos de imagen de proceso conocidos, sin asumir que sean snapshots coherentes del estado completo.

## Prioridades siguientes

1. **Acción y tiempo:** confirmar una entrada reconocida por el juego y tomar marcadores antes/después. Comparar reposo, una sola acción y vuelta a reposo, con el mismo rango y varias repeticiones. Los timestamps del anfitrión acotan una llamada, no prueban el frame emulado.
2. **Doce candidatos concretos:** seguir las ventanas que difieren del archivo, con mayor frecuencia dentro del mismo presupuesto de solicitudes. Añadir referencias estáticas a esas direcciones; una diferencia, un float finito o un puntero aparente no bastan para nombrar una estructura.
3. **BSS documentada:** el [loader exacto de Citra](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/loader/ncch.cpp) redondea BSS a páginas y la añade al segmento de datos. Para este mapa, el comienzo derivado sería dirección de datos + 450×4096 y la extensión redondeada 638.976 bytes. Es una base para un próximo plan de lectura, todavía sin verificar el rango en ejecución ni leerlo en este ensayo. Heap y estructuras creadas dinámicamente siguen sin mapearse.
4. **Extracción de recursos:** preferir contenedor/tabla de archivos para modelos, texturas y animaciones: conservar hash de origen, offset, tamaño empaquetado/desempaquetado, versión de herramienta y hash de salida. El muestreo RAM no recupera automáticamente límites de recursos ni referencias de esqueleto/material. Reutilizar ARC y los parsers existentes; mantener bloqueos MOD230/LMT/TEX y JKR donde su semántica no esté validada.
5. **Cambio de backend:** evaluar Azahar v2 en un perfil separado si se necesitan bloques grandes, selección de proceso y capturas asociadas. No sustituir Citra durante una sesión ni atribuir resultados de un emulador a otro. No hacen falta nuevas instalaciones para los resultados obtenidos aquí.

## Reproducción de esta aceptación

```text
python tools/stt_re/sample_citra_data_windows.py --mapping <recibo-MH4U-code-BLZ.json> --image <code.bin-verificado> --out <carpeta-privada-nueva> --sweeps 2 --stride 4096 --rate 20 --seconds 60
```

Usar el mapa y el `.code` de la misma base MH4U que la sesión, no el update MHXX. El control compara solo cuatro bytes y no autentica por sí solo toda una compilación. El hash completo del derivado estático sí se revalida; no se volvió a hashear la imagen original de 4 GiB. En este equipo, las lecturas válidas requirieron ejecución del cliente en el anfitrión autorizado debido al aislamiento de red observado anteriormente.

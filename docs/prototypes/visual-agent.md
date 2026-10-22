# Agente visual GPU 0.24 — imágenes y estado de escena

Base explícita: GPU0.22, PR #33, commit6befe1fe033821079a1006217c3244e8e6ca0548. Conserva mapa/texturas/controles y recursos locales existentes. No incorpora la cámara experimental0.23 ni vuelve al renderer CPU0.15. STTP00001/00.24; no sustituye STTM00001. La primera prueba de transporte0.16 funciona, pero su base era antigua: [resultado y corrección de alcance](visual-016-result.md).

## Captura

Select inicia/detiene métricas y visuales hacia la IP privada existente en ux0:/data/STTP00001/monitor-ip.txt. Métricas mantienen su contrato actual y puerto32100. Imágenes van por UDP32101 en canal STV/1 separado; no se cambia STT/3 ni STT/4–7. START sale y una notificación de suspensión/reanudación detiene captura, que requiere otro Select. No recibe órdenes del PC ni cambia frecuencias, firmware/plugins, Wi-Fi o datos de escena.

Se lee el buffer propio de vita2d después de swap_buffers y wait_rendering_done, antes del siguiente dibujo. La implementación pública [vita2d.c](https://github.com/xerpi/libvita2d/blob/master/libvita2d/source/vita2d.c) actualiza frontBufferIndex al intercambiar y get_current_fb devuelve ese buffer. Su modo estándar es960×544 con stride960. Este comportamiento se revisó en fuente; compilación y prueba física deben verificar el uso en el SDK fijado. No se lee la pantalla global ni procesos ajenos.

Muestreo4:1 a240×136 RGB565. Máximo una captura nueva cada2s; imagen y escena se congelan en el mismo punto del bucle. Se envían como máximo4fragmentos no bloqueantes por fotograma. Se conserva un solo snapshot en el emisor, sin cola histórica. La frecuencia puede ser menor a0,5Hz con pérdida/red lenta/FPS bajos; no es vídeo continuo ni entrega confirmada.

El snapshot GPU incluye posiciónXYZ en mm, yaw, fotograma de animación, filtro, objetivo30/45FPS, tick, ojo de cámara en mm y vectores derecha/arriba/frente en millonésimas. Son los valores que alimentaron el render de esa imagen, cuantizados; no transformaciones reconstruidas del PNG. No se inventan HP, objetivos de combate, ataques o equipamiento ausentes en este laboratorio. perf_session permite correlacionar con la ventana de métricas, sin afirmar simultaneidad exacta.

VISUAL ATT es número de capturas intentadas, ERR fallos locales; no cuentan imágenes entregadas. Tras5fallos visuales el canal para hasta nuevo Select. Se conserva el plazo global de180s de proceso activo y el límite de fallos de métricas de la base. No se afirma un plazo de pared mientras la aplicación esté suspendida.

## Receptor PC

Desde la raíz, con Python3.11 o posterior:

```powershell
python -m stt_monitor.visual_receiver --bind 127.0.0.1 --output visual-new --duration 180 --idle-timeout 10 --max-frames 90 --max-bytes 16777216
```

Loopback para pruebas sintéticas; la prueba física requiere IP privada del PC y la excepción UDP32101 autorizada con alcance y retirada temporal. Sin cambios del router ni desactivar el firewall. El directorio debe ser nuevo.

Guarda frame-NNNN.png + frame-NNNN.json y una vista index.html que refresca la última pareja completa. La fecha de recepción sigue visible; el refresco del navegador no acredita imágenes nuevas. summary.json indica imágenes, fragmentos, rechazos, caducadas/desalojadas, duplicados, incompletas y causa de cierre. Ctrl+C conserva archivos y escribe interrupted.txt; puede no haber resumen final. No se garantiza recuperación transaccional frente a fallos de disco.

Default180s,90imágenes,10s sin completar una y16MiB para PNG+JSON. index.html/resumen son auxiliares pequeños fuera de esa cuota. El plazo es cooperativo: disco/stdout pueden retrasar el cierre. Memoria de ensamblaje limitada a dos imágenes de como máximo66815bytes cada una, más estructuras, PNG y buffers del intérprete/socket; no es una medición de RAM máxima.

## Transporte y metadatos

Cabecera STV/1 big-endian `!4sQIIIHH` (28bytes): magicSTV1,stream_idu64,frameu32,totalu32,offsetu32,countu16,meta_lengthu16. Después0–1000bytes de fragmento (count debe ser el tamaño exacto esperado, nunca0). Máximo1028bytes por datagrama. Offset múltiplo de1000; total=meta_length+65280. Metadatos UTF-8 de1–1535bytes; después RGB565 little-endian. No se fragmentan los contratos JSON STT existentes.

Metadatos version2 para GPU: campos exactos version,width=240,height=136,format=rgb565le,frame,perf_session,scene. Scene contiene source,tick,pos_mm,yaw_mdeg,animation_frame,filter_linear,target_fps,camera. Camera contiene eye_mm,right_ppm,up_ppm,forward_ppm,yaw_mdeg,pitch_mdeg. El receptor también conserva soporte para la versión1 preliminar CPU, con escena STT/3. No se reinterpretan silenciosamente las dos estructuras.

Validación estricta de tamaño/rangos/claves/duplicados, frame coincide con cabecera, sesiones y versiones explícitas. UDP/source no autentican ni cifran. Imágenes incompletas nunca se publican: caducidad5s, dos en curso como máximo y desalojo de la más antigua ante una tercera. Deduplicación acotada a128identidades; fuera de esa ventana no se garantiza. La pérdida de fragmentos no se resuelve con retransmisión.

## Validación y pendientes

Pruebas Python de imagen PNG/canales/CRC, fragmentos desordenados/duplicados, identidades, cuota y expiración. Fixture C→Python con ASan/UBSan cubre fuentes480×272 CPU y960×544 GPU, reducción2:1/4:1 y metadatos diferenciados. Las bandas de color de CI son sintéticas, no capturas Vita.

La prueba física 00.24 del 22 de octubre recibió 24 parejas completas PNG/JSON de la Vita, frames 0–23, entre 21:14:19.706552 y 21:15:05.788482 UTC. Se observaron 23 posiciones y 23 estados de cámara distintos. Dos imágenes inspeccionadas muestran mapa, personaje y texturas desde vistas diferentes. El usuario confirmó apertura de 00.24 GPU conservando mapa/texturas y, después de caminar y mover la cámara, NET OFF, contador VISUAL ATT detenido y ERR 0 al pulsar Select.

El número de parejas permaneció en 24 durante más de diez segundos con receptor y excepción todavía activos. Se cerró ese receptor y se comprobó retirada de la excepción temporal a las 23:15:48 del 22 de octubre (España). Evidencias y hashes de cada pareja se conservan localmente en physical-result.json; no se publican imágenes ni recursos privados. No hay resumen agregado de fragmentos/rechazos porque el receptor terminó externamente; no se afirma ausencia de pérdidas UDP.

Automatización del commit f54bc1c: CI de monitor, agente, prototipo y laboratorio GPU superada; incluye compilación VitaSDK, inspección de paquete 00.24 y fixtures C→Python con ASan/UBSan. Ejecución Python local: 34 pruebas superadas y una omitida por falta de compilador C local. El VPK probado tiene SHA256 f05a1554b39bae0f7d8f6af07b5dca1af635409bdba98b12e4341bcda352d5f5.

Pendientes: medir coste de captura/FPS y probar suspensión en esta versión; no se registró el ATT final exacto. Se retiraron del PC el VPK y ZIP preliminares 0.16 tras verificar sus hashes, conservando evidencias e historial. Tras reactivar FTP, se verificó el hash completo del paquete vigente 00.24 y se conservaron sus archivos. Se retiraron únicamente los instaladores remotos 00.16 y 00.22, comprobando hash, identidad STTP00001 y versión SFO; después se retiraron sus carpetas vacías. No se tocaron datos de aplicación ni recursos de escena. Ningún recurso comercial se añade al VPK o al repositorio y no se modifican los archivos locales de escena.

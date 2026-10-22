# Agente visual integrado — prototipo 0.16

Implementación derivada de PR #25 (9139a415), sin fusionar. STTP00001/00.16 incorpora imágenes del buffer propio y datos de escena del mismo fotograma. No actualiza ni reemplaza el monitor independiente STTM00001. No lee la pantalla de otras aplicaciones, no necesita plugins y no recibe comandos del PC.

## Funciones y uso previsto

Select inicia/detiene la captura integrada. Conserva STT/4 de rendimiento a UDP32100 y añade STV/1 visual a UDP32101, ambos hacia la IPv4 privada de `ux0:/data/STTP00001/monitor-ip.txt`, que no se publica ni empaqueta. Sin configuración válida no transmite. START sale. Una notificación de suspensión/reanudación o retroceso de reloj detiene la captura: requiere otro Select. No se cambia el reloj ni la configuración Wi-Fi.

Cada imagen procede del buffer 480×272 del prototipo, reducida por muestreo 2:1 a 240×136 y cuantizada RGB565. Máximo una imagen nueva cada dos segundos, sin cola histórica. Se congela la imagen y escena antes de fragmentarla: el siguiente render no modifica esa captura. Como máximo cuatro datagramas no bloqueantes por fotograma del juego. Una imagen necesita unos 67 fragmentos; su frecuencia real puede ser menor si el juego va lento. No es vídeo de 30 FPS ni garantiza entrega.

La escena contiene cámara (ángulos y distancia), posición/orientación/estado del cazador, ataque/fase/impactos, tick, equipamiento, modo de suelo y posición/HP/reacción del objetivo. Se reutiliza el snapshot STT/3 sin cambiar su contrato; algunos campos heredados son constantes del prototipo (por ejemplo HP del cazador), no sensores nuevos. Las frecuencias y demás métricas siguen en STT/4; pueden correlacionarse por sesión y tick, sin promesa de simultaneidad exacta con su ventana de 1 Hz.

VISUAL ATT cuenta capturas intentadas, ERR errores locales; no son imágenes entregadas. Cinco fallos visuales deshabilitan ese canal hasta reiniciar Select; rendimiento puede seguir activo. El monitor completo conserva el límite de 180 s de proceso activo y sus cinco fallos de rendimiento. Ese plazo no es tiempo de pared durante suspensión; la notificación de suspensión ahora cierra la captura.

## Receptor PC

En un terminal desde la raíz, con Python 3.11 o posterior:

```powershell
python -m stt_monitor.visual_receiver --bind 127.0.0.1 --output visual-synthetic --duration 180 --idle-timeout 10 --max-frames 90 --max-bytes 16777216
```

El ejemplo escucha loopback; para Vita debe usarse explícitamente la IP privada del PC y una excepción de firewall específica para UDP32101 si es necesaria. Esa configuración y la instalación física no se ejecutan por compilar esta entrega. No abrir el router ni desactivar firewall.

La carpeta debe ser nueva: el receptor rechaza una existente. Guarda parejas `frame-NNNN.png`/`frame-NNNN.json`, `index.html` con vista de la última imagen completa y `summary.json`. Abrir index.html en el navegador permite refresco cada dos segundos sin servidor web ni control remoto. La imagen y la escena comparten índice local, identificador de sesión y fotograma. La pantalla podría mostrar una imagen antigua si deja de recibirse: consultar su hora y el resumen, no interpretar el refresco HTML como recepción nueva.

Default: 180 s, 10 s sin imagen completa, 90 imágenes y 16 MiB para PNG+JSON. index.html y summary.json son archivos auxiliares pequeños adicionales a esa cuota. El plazo se aplica al bucle, sin garantía de tiempo real si disco o salida bloquean. Ctrl+C conserva resultados y escribe interrupted.txt; en ese caso puede no existir resumen final. Fallos de disco terminan con error, sin promesa de recuperación transaccional de una pareja parcialmente escrita.

## Canal STV/1

Separado de los datagramas JSON STT/1–4. No cambia sus versiones, el tamaño máximo de 1024 bytes ni los contratos de prototipos.

Cada datagrama: cabecera de 28 bytes big-endian `!4sQIIIHH`: magic STV1, stream_id u64, frame u32, total u32, offset u32, count u16 y meta_length u16; después count bytes (máximo 1000). Datagrama máximo 1028 bytes. Offset múltiplo de 1000; tamaño exacto del último fragmento. Total exacto = meta_length + 65280. Metadata UTF-8 estricta de 1–1535 bytes, seguida de píxeles RGB565 little-endian.

Metadata exacta: version=1, width=240, height=136, format=rgb565le, frame, equipment, ground_mode, target y scene (snapshot STT/3). El session de scene debe corresponder a `vita-perf-<stream_id hexadecimal>` y seq debe coincidir con frame. El receptor rechaza claves duplicadas, rangos/modos incorrectos o identidades incompatibles. UDP y source no autentican al emisor; esto no aporta cifrado ni prueba de origen físico.

Se admiten fragmentos desordenados y duplicados idénticos. Un duplicado contradictorio descarta la imagen. Separación por IP/sesión/fotograma; no se mezclan emisores. Máximo dos imágenes incompletas; caducan a los cinco segundos y se descarta la más antigua si llega una tercera. Se recuerdan 128 identidades terminadas/descartadas; fuera de esa ventana no se garantiza deduplicación. El resumen cuenta duplicados, caducadas, desalojadas, incompletas, rechazos y una imagen completa no guardada si excede la cuota. No escribe imágenes parciales ni las presenta como capturas válidas. El límite de estado no es una medición de RAM máxima.

## Validación y pendientes

Pruebas PC de fragmentación inversa/duplicados, expiración, cuotas, mezcla de peers, metadatos y PNG (canales, datos descomprimidos y CRC). Ensayo UDP real en loopback con escena marcada simulator. Fixture C con sanitizadores cruza imagen RGB565 y STT/3 hacia el receptor Python; build Vita e inspección SFO00.16 en CI. La imagen de bandas roja/verde generada en CI es sintética, nunca una captura de Vita.

Al publicar: pruebas Python locales aprobadas con omisión explícita del compilador C no disponible; contrato C y VPK dependen de CI. Pendientes físicos: instalación/arranque, recepción de imágenes y escena en la LAN, carga real sobre FPS, pérdida/reconexión, suspensión y parada. No se afirma ganancia de rendimiento ni recepción física desde pruebas PC. Sin cambios de firmware/plugins, juegos, banco u originales; no se transfiere ni instala esta versión automáticamente.

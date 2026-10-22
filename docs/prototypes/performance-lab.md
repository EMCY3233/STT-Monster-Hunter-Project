# STT 0.15 — medición del prototipo y comparación del suelo

El usuario confirmó movimiento, cámara, extracción y golpe en 0.14 y observó 10–12 FPS. Es un resultado comunicado por el usuario, no una captura sincronizada ni un perfil del dispositivo. Esta versión añade el productor de lectura al mismo proceso del prototipo; abrir el monitor independiente en primer plano no mide de forma equivalente el juego suspendido.

## Uso

Instalar el VPK STTP00001/00.15. La configuración local `ux0:data/STTP00001/monitor-ip.txt` contiene solo la IPv4 privada del receptor. No se empaqueta la dirección del usuario en GitHub. Select activa/desactiva la captura UDP hacia puerto32100; termina automáticamente a los180segundos de reloj de proceso activo o tras5errores acumulados. No hay recepción de comandos, confirmación de entrega ni control remoto. NET ON/contador solo acredita intentos de envío aceptados localmente: el recibo PC es la evidencia de recepción.

El receptor STT Vita Monitor actualizado acepta STT/1, /2, /3 y /4; captura con límite de duración, tamaño, cuota e inactividad. `python -m stt_monitor.receiver --bind <IP_PC> --output <archivo_nuevo> --duration 600 --idle-timeout 600 --max-bytes 10485760 --live`. Después: `python -m stt_monitor.perf_analyze <archivo>`. No instalar otro monitor para esta prueba ni cambiar plugins, firmware o frecuencias.

Prueba:30squieto,30smovimiento/cámara y30sataques en G1. Pulsar L cambia a G0 y repetir con la misma vista y acciones. G1 calcula el plano del suelo por filas; G0 conserva los512triángulos del suelo como referencia. Se descarta la ventana incompleta al cambiar de modo. Ambos modos usan el nuevo buffer de dibujo en RAM cacheada y copia secuencial a CDRAM: G0 no equivale exactamente al binario0.14.

## Qué se mide

| Solicitud | Campo/unidad | Alcance |
|---|---|---|
| CPU | cpu_mhz | Frecuencia consultada, no porcentaje de carga. |
| GPU | gpu_mhz | Frecuencia consultada; escena rasterizada en CPU. |
| XBAR | xbar_mhz | Frecuencia consultada. |
| FPS | frames/window_us | Fotogramas completos contados por ventana de reloj de proceso; no FPS externo de compositor. HUD muestra el inverso del último periodo completo, incluido limitador. |
| RAM | ram_free, bytes | Memoria USER_RW disponible según API; no memoria usada del juego ni RAM física total. |
| CDRAM | cdram_free, bytes | Disponible según API; no utilización de GPU. |
| PHY | phy_free, bytes | Memoria físicamente contigua disponible según API. |
| CDLG | cdlg_free, bytes | Subpresupuesto de diálogos libre si la consulta funciona. |
| FG APP | null | No se dispone de contador validado equivalente al del overlay. |
| VNZ | null | No hay acceso validado al contador de Venezia desde este productor. |
| BAT | battery_pct, % | Lectura de batería; null si falla. |
| Carga CPU/GPU | null | Frecuencias y duración del render no se presentan como utilización. |

Lecturas API negativas se envían null. Referencias primarias: [VitaSDK power](https://docs.vitasdk.org/group__ScePowerUser.html), [VitaSDK sysmem](https://docs.vitasdk.org/kernel_2sysmem_8h_source.html). No se llama a funciones para cambiar frecuencias o presupuestos de memoria.

STT/4, datagrama máximo1024bytes, incluye sesión de captura nueva en cada activación, secuencia, tick del juego, estado de equipamiento al muestrear y modo de suelo. Las fases `update_us`, `render_us`, `present_us` son medias por fotograma de la ventana; presentación incluye copia a CDRAM y espera de vblank. `telemetry_us` agrega el tiempo de la llamada de instrumentación del fotograma anterior: queda desplazado un fotograma y es diagnóstico del coste amortizado. El trabajo de limitación a30FPS no se atribuye a CPU/render. El receptor deriva FPS como total de frames/tiempo, evita duplicados y separa sesiones, fuentes y modos.

## Optimización y límites

Se evita dibujar repetidamente512triángulos para un plano y se rasteriza en un buffer cacheado antes de copiar la imagen a CDRAM. Se añade aproximadamente557056bytes de buffer principal y1MiBpara red mientras captura. El primer cambio necesita comparación física; no se afirma una ganancia de FPS a partir de compilación o pruebas PC. La CPU sigue rasterizando personajes y objetivo; no es todavía un motor GXM/GPU.

Pruebas: contrato C→Python, rangos/null/duplicados, captura y análisis ponderado, proyección y límites del nuevo suelo en12cámaras, controles/cámara/combate/render y compilación/inspección del VPK. Las pruebas sintéticas no se publican como métricas del dispositivo.

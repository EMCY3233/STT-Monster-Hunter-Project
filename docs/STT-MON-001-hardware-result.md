# STT-MON-001 — primer resultado en hardware

21 de octubre de 2026, 06:37:29–06:38:32 (Europe/Madrid).

## Alcance

Aplicación experimental 0.1, compilada desde main b02c7cc. Hardware/configuración declarados por el usuario: PS Vita 1000, firmware 3.65 HENkaku/ensō, VitaShell, SD2Vita 64 GB. La configuración no se inspeccionó de forma independiente. El usuario autorizó transferencia FTP, instalación y ejecución solo de STT Vita Monitor.

El VPK se copió a una carpeta nueva de ux0:data, sin sobrescribir archivos; su lectura de vuelta coincidió con SHA-256 `f8691ad873695c5af3b8ec4d271571b5e21d5370dfb0c5326b8caef1ba92696b`. Antes de copiar, STTM00001 no estaba presente en ux0:app.

## Observación en el PC

| Métrica | Resultado |
|---|---|
| Muestras válidas | 60 |
| Rechazos del receptor | 0 |
| Secuencias | 0–59, completas |
| Duplicados / fuera de orden | 0 / 0 |
| Huecos entre secuencias observadas | 0 |
| Duración entre primera y última recepción | 62,524186 s |
| uptime_ms final declarado | 62514 |
| Batería declarada, inicial/final | 91 % / 91 % |
| Origen declarado por el emisor | vita |

El receptor terminó al alcanzar su límite de 60 mensajes. No se deduce consumo energético ni latencia de red de estos datos. El ritmo observado es aproximadamente 1 Hz, no una garantía de temporización exacta. STT/1 no autentica la identidad del emisor.

## Confirmación del usuario

- Instaló y ejecutó la aplicación en la consola; el flujo produjo las muestras anteriores.
- Tras pulsar START, confirmó que salió correctamente.
- Informó texto pequeño y parpadeo constante. El código 0.1 borraba/redibujaba la pantalla cada 50 ms, coherente con esa observación. No se midieron FPS de pantalla.

## Cierre y evidencia

La excepción de firewall fue autorizada expresamente, limitada al proceso receptor, UDP 32100 y las dos IP privadas del ensayo. Retirada a las 06:38:48; se verificó que la regla ya no existía. No se desactivó el firewall. No se cambiaron firmware/plugins ni se borraron juegos.

El registro íntegro se conserva localmente, sin publicar IP ni identificador de sesión. SHA-256 del JSONL: `eb33809476bf6b7663718c99d7a8309b43dc207f8bca4e3fada9fb33ed3bf1c0`.

## Pendientes

Prueba física de Círculo para detener, desconexión/reconexión Wi-Fi, suspensión y rendimiento sostenido. La corrección de tamaño/parpadeo 0.2 debe compilarse y validarse visualmente en consola antes de considerarla confirmada.

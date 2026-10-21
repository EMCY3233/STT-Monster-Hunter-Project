# STT-MON-003 — recepción y parada de 0.2

21 de octubre de 2026. Paquete 00.20, código del commit 901fe16, integrado por PR #2.

## Resultado

En el último ensayo se recibieron diez mensajes de la sesión, secuencias 0–9, sin huecos internos, duplicados ni desorden. El usuario confirmó que Círculo mostró «Parado» y detuvo el contador. La observación adicional de diez segundos en el PC no añadió mensajes a esa sesión. Batería declarada: 90 %.

Primera/última recepción del último ensayo: 07:03:41.909785 y 07:03:49.903653 (Europe/Madrid). Estos tiempos de llegada no miden latencia ni garantizan un intervalo de envío exacto.

## Captura completa y limitaciones

El JSONL reúne tres sesiones: 4 mensajes (secuencias 2–5), 6 (0–5) y 10 (0–9), veinte en total. La primera sesión no incluye 0–1: no se puede afirmar ausencia de pérdida para toda la captura ni atribuir la ausencia a la red. Las sesiones reflejan reinicios de ensayo; no prueban reconexión Wi-Fi.

El primer receptor terminó por inactividad antes del inicio efectivo; se reabrió con mayor margen. La excepción temporal de firewall expiró y se comprobó su retirada; el receptor de prueba se cerró al terminar. No se desactivó el firewall ni se modificaron juegos, firmware o plugins. No se transfirió un nuevo binario para registrar este resultado.

SHA-256 del registro local: `bac9ee0cddae93b945e5ae29d5525097e84349dc4997deb8eb1c8d0f08cf17cc`. IP e identificadores de sesión se mantienen en el registro local, no en este documento.

## Pendientes

- Nuevo ensayo completo de 60 muestras con 0.2; el ensayo completo anterior fue con 0.1.
- Desconexión/reconexión Wi-Fi y suspensión.
- Informes de error transmitidos al PC: no implementados en STT/1. Los errores de envío actuales solo aparecen en pantalla; el usuario esperaba un informe automático y esta diferencia se explicó durante la prueba.

La validación visual de texto mayor y ausencia de parpadeo fue confirmada por el usuario en un paso anterior.

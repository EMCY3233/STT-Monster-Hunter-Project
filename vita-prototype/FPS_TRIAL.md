# Ensayo 00.19

Instalar STTP00001 y abrir STT Vita Prototype. Objetivo inicial CAP45; Círculo alterna CAP30/CAP45. FPS es la duración del último ciclo, no un promedio estable. Conservar G2/T1 para comparar. Select activa el envío de rendimiento durante un máximo de tres minutos. Repetir 30 segundos quieto, caminando y atacando con la misma cámara en cada objetivo.

El formato STT/6 se conserva: la sesión contiene versión y objetivo (`vita-0019-f45-<reloj>` / `vita-0019-f30-<reloj>`). Cada cambio descarta la ventana incompleta y crea una sesión distinta sin ampliar el límite temporal de captura. El analizador agrupa por sesión, G y T, evitando mezclar objetivos. Capturas anteriores sin este prefijo no identifican objetivo/versión inequívocamente.

La temporización usa plazos absolutos; no suma el error de fase de vblank a cada intervalo. La simulación mantiene sus pasos de 60 Hz. El ensayo conserva el reloj actual de la consola. No mide tiempos de presentación individuales ni demuestra uniformidad de movimiento: la pantalla de 60 Hz requiere alternar intervalos al intentar 45 FPS. Comparar FPS de aplicación y costes por etapa; validar visualmente la fluidez en consola.

# Flechas normales sostenidas — 22-10-2026

> Seguimiento: [primera interpretación de contadores y comparación BSS](runtime-counter-translation.md).

Se creó `tools/stt_re/hold_citra_arrow.py` y se verificó desplazamiento visible en MH4U mediante flecha derecha dos segundos; izquierda dos segundos devolvió al personaje hacia el punto anterior. Una repetición de derecha se realizó íntegramente dentro de una captura de treinta segundos: 299/299 lecturas válidas, cero errores y controles de código correctos antes/después. Esto resuelve la limitación previa de pulsaciones breves sin movimiento confirmado.

## Entrada y protecciones

La herramienta usa SendInput con KEYEVENTF_SCANCODE y KEYEVENTF_EXTENDEDKEY para las flechas normales. Envía un único key-down, espera el intervalo solicitado comprobando el foco cada 10 ms, y ejecuta key-up en finally. Comprueba HWND, PID y ruta exacta del ejecutable, exige Citra ya en primer plano, rechaza modificadores/flechas previamente pulsados y limita cada acción a 0,1–3 segundos. No activa ventanas, cambia mapeos ni instala componentes. Sin `--execute` sólo valida. Los recibos se crean exclusivamente y no se sobrescriben.

Cinco pruebas cubren duración, liberación al perder foco, liberación tras fallo de key-down, rechazo por foco incorrecto y límites de duración. No garantizan liberación tras terminación forzada del proceso ni recepción del key-up si Windows rechaza la entrada.

El intento inicial en el aislamiento falló al comprobar el proceso (WinError 5) y no envió teclas. La ejecución autorizada fuera del aislamiento aceptó down/up con dos segundos de separación. El recibo mantiene movement_verified=false porque no observa imágenes; la observación visual independiente está separada en runtime-held-key-evidence.json.

## Lectura y límites

La primera captura de doce segundos terminó antes de la flecha izquierda: sus 120 muestras no se atribuyen a esa entrada. Se repitió con treinta segundos y se verificaron hashes de cada muestra, binario, índice y protocolo, así como inclusión temporal de la pulsación completa. En esa repetición el patrón u32 a +24 cambió 27 veces en 298 pares. Sigue sin identidad semántica: ya variaba en reposo y no se convierte en coordenadas, hitbox o animación por coincidir con una acción.

La sincronización usa tiempos del host y comprobación visual posterior, no frames exactos. Los registros de memoria y capturas permanecen privados. Los lectores finalizaron; las teclas se soltaron y Citra quedó abierto. Próximo experimento: ciclos cortos reposo/derecha/reposo/izquierda, con candidatos más amplios y controles negativos; no interpretar automáticamente campos como posición.

## Uso reproducible

Con la ventana actual seleccionada y Citra en primer plano, ejecutar Python con `hold_citra_arrow.py --window <HWND observado> --exe <ruta exacta a citra-qt.exe> --key right --seconds 2 --receipt <archivo nuevo> --execute`. No reutilizar un HWND de una sesión anterior. La herramienta sólo admite flechas y citra-qt.exe.

Fuentes primarias: [KEYBDINPUT](https://learn.microsoft.com/windows/win32/api/winuser/ns-winuser-keybdinput), [SendInput](https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-sendinput). La búsqueda de complementos no devolvió una solución pertinente; no se instaló ninguno.

# STT-MON-008 — suspensión y límite total en 0.5

## Paquete y comprobaciones automatizadas

Código probado: `ad119037bc1acf83307228875a3833a0e630f082`. VPK SHA-256: `67c42bfb5567628b0dc7a99146ef8e4accbd7eb3ea1e2dcf57b95fcc590ec1f6`. Usuario confirma instalación y apertura de 0.5 con «Tiempo de limite» visible.

[CI PC](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39552818196): quince pruebas y ensayo CLI correctos en la matriz Windows/Linux. [CI Vita](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39552818266): pruebas C, compilación Vita e inspección VPK correctas.

## Suspensión breve

Usuario informa 39 s de tiempo de límite, 15 intentos y 15 envíos después de suspender, despertar y parar con Círculo. PC recibió secuencias 0–14; última muestra con uptime de proceso 14147 ms, frente a 39,096378 s entre primera y última recepción. Mayor intervalo entre mensajes: 25,892994 s. Último diagnóstico transmitido: 14 envíos previos, cero errores, códigos cero. El contador de pantalla incluyó el intervalo que no avanzó en el proceso.

Registro local `hardware-test-007/vita-suspend-test.jsonl`, SHA-256 `35a85434cad355c553b77b803a55b146da3bc89c7c5e51e434a490dfcc422616`.

## Suspensión larga

Instrucción: mantener Wi-Fi habilitado, iniciar otro ensayo, suspender con pulsación breve de Encendido cerca de diez intentos, esperar 3 min 10 s y regresar sin pulsar Cruz.

PC recibió 14 muestras, secuencias 0–13, de una misma sesión. Primera: 2026-10-21T06:12:57.929126+00:00. Última: 2026-10-21T06:14:41.655738+00:00. Al comprobar a las 08:18:20 (España), no había nuevas muestras y tanto receptor como excepción de firewall seguían activos. No se observaron paquetes posteriores antes de cerrar la captura. Último diagnóstico: 13 envíos previos, cero errores y códigos cero; cada paquete informa del intento anterior.

El usuario confirmó «14 int 14 env temp 181 parado limite total». La parada por límite total después de reanudar queda validada en este ensayo. La pantalla satura en 181 s deliberadamente: el umbral de parada sigue siendo 180 s. El PC no mide por sí solo la duración exacta de suspensión ni recibe el estado de parada por STT/2; la lectura de pantalla procede del usuario.

Registro local `hardware-test-008/vita-long-suspend-test.jsonl`, SHA-256 `98a9846bc9ecd419f710e7b001e6d8987de64d97901d1e5209f22e5a77daa3d1`.

## Cierre y alcance

Ambos receptores cerrados. Retirada de ambas excepciones temporales comprobada; la última a las 08:20:35 (España). Sin cambios de firmware, plugins, juegos o perfiles de red. Instaladores 0.4 anteriores retirados tras verificar 0.5; conservados paquete vigente, recibos y evidencias. Este cierre documental no requiere transferencia ni reinstalación.

Pendientes físicos: límite de 30 s sin red durante suspensión y rutas de fallo/retroceso de reloj. Esas condiciones solo están cubiertas por pruebas automatizadas. No se afirma validación universal de RTC ni entrega garantizada de UDP.

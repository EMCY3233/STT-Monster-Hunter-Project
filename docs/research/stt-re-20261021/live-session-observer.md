# Observador de sesiones Citra — 22-10-2026

Se creó `tools/stt_re/observe_citra_session.py`: lector acotado de registros y del protocolo RPC incluido en `analysis-local/c3/scripting/citra.py` de Citra Nightly 2104. Solo emite solicitudes ReadMemory (tipo 1), hacia 127.0.0.1. No incluye operaciones WriteMemory, inyección, búsqueda de claves ni escaneo de procesos.

## Alcance verificado

Cinco pruebas sintéticas pasan: solicitudes solo de lectura; rechazo de identificadores/longitudes incorrectos; límites de dirección y tamaño; registros truncados y UTF-8 fragmentado; timeout registrado y rechazo de sobrescritura del directorio de salida. El primer intento de pruebas tuvo dos errores de permisos en la carpeta temporal del sandbox; la repetición con TEMP/TMP dentro del espacio de trabajo pasó. No se repitió toda la batería histórica.

Se preparó una copia aislada del Citra Qt ya instalado, con perfil nuevo, sin importar partidas. Ejecutable SHA-256 `8450b9bf8caec4e9ede9fd20495d0dae52c36e37c119c4be6aee706f66a62ac2`. La ventana se abrió y su árbol de accesibilidad pudo consultarse. Mostró una solicitud de consentimiento de telemetría; no se respondió automáticamente. **No se cargó un juego en este ensayo.** No se verificó una escena, una acción ni su correlación con memoria.

El usuario confirmó después que había resuelto el aviso. Se observó la ventana principal sin ese aviso y se abrió Cargar Archivo. El control por accesibilidad devolvió `point ... is over citra-qt.exe "Citra", not target window ...` y, para el nombre de archivo, `element 137 is not available in cached app state`. Una selección mediante captura abrió el diálogo, pero la captura posterior no confirmó el foco en Nombre. No se introdujo texto ante esa incertidumbre. Se solicitó al usuario cargar manualmente la base conocida. El bloqueo actual es la carga del juego, no el consentimiento de privacidad.

Una prueba negativa de tres segundos, sin juego cargado, hizo cuatro intentos de lectura de cuatro bytes desde 0x00100000: cero respuestas válidas y cuatro errores; cero líneas de registro disponibles. Esto comprueba el tratamiento del fallo, no que el servidor sea incompatible ni que la dirección contenga datos válidos. El protocolo RPC es distinto de GDB; no se comprobó GDB.

## Reproducción con una sesión local abierta

Con el consentimiento resuelto por el usuario y un juego legible ya cargado en el perfil aislado:

```text
python tools/stt_re/observe_citra_session.py --log <perfil>/log/citra_log.txt --out <carpeta-privada-nueva> --seconds 10 --address 0x100000 --size 4
```

El rango es un sondeo inicial del área de código, no una dirección de hitboxes o IA identificada. Cada lectura admite 1–32 bytes y timeout de hasta 250 ms; duración solicitada máxima 60 segundos. No se detiene ni controla el emulador desde este programa. Sin `--address`, solo observa el registro. Los eventos de memoria contienen hashes y si cambiaron respecto a la muestra anterior; no guardan bytes de memoria.

Las líneas existentes se incluyen desde el principio y reciben la hora de llegada al observador: pueden ser anteriores al ensayo. Los tiempos no equivalen a frames ni a timestamps internos del juego. El lector detecta truncación por tamaño, pero no garantiza detectar reemplazo de un registro por otro del mismo tamaño o mayor. No guardar estas salidas privadas en Git: los registros pueden contener rutas u otros datos locales.

## Próxima aceptación

1. Resolver la solicitud de privacidad manualmente y abrir la base MH4U `.3ds` previamente identificada, sin instalar CIAs ni aportar claves.
2. Registrar una lectura válida y contrastar su digest con el mismo rango del `.code` estático, verificando antes el mapeo de dirección de esta compilación. Una igualdad solo demostraría esos bytes.
3. Definir una acción reproducible y marcadores temporales antes de buscar datos variables. No identificar hitboxes, animaciones o IA por la mera existencia de cambios.

Esta etapa no sustituye ninguna de las 29 aceptaciones del índice anterior. Su resultado es una herramienta probada sintéticamente y una conexión con juego **pendiente**.

Referencia documental auxiliar: [configuración de Azahar 219d743, descendiente de Citra](https://github.com/azahar-emu/azahar/blob/219d743a1e698101fe1ab8bef43e6563126c3c27/src/citra_qt/configuration/config.cpp), grupo Debugging/enable_rpc_server. Se utilizó como hipótesis de configuración, no como prueba del comportamiento de Nightly 2104. La referencia directa del paquete local es su cliente scripting/citra.py.

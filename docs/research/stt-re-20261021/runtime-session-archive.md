# Archivo de sesiones, lecturas prioritarias y exportación verificada — 22-10-2026

> Referencia posterior: [pistas EUR de GitHub/Scribd y contraste local](mh4u-cheat-references.md).

## Qué se construyó

`citra_session_archive.py` captura BSS verificada, guarda bloques de 32 bytes por SHA-256, conserva un índice de dirección/tiempo/pasada y permite analizar o exportar cada pasada tras comprobar integridad. Las lecturas repetidas de igual contenido comparten objeto; el índice conserva cada observación y ubicación. No se modificó el banco de recursos previo.

Se amplió la zona densa de 4096 a **8192 bytes**, `0x0110BC00`–`0x0110DC00` (fin exclusivo), íntegramente dentro de la BSS derivada del mapa ya verificado. Cada sesión toma tres pasadas, máximo 20 solicitudes/s contando controles, dos controles de código por pasada y límite de 60 segundos. La captura falla cerrada ante error; no exporta una sesión incompleta. Es una lectura secuencial no atómica.

En la tercera sesión se intercalan **dos ventanas prioritarias de 32 bytes por cada 16 bloques densos**: una incluye los campos vecinos con candidatos de lectura y la otra los contadores contrastados por avance individual. Las muestras prioritarias se indexan aparte; no alteran la reconstrucción del bloque denso.

- `0x0110CF40`: 48 muestras prioritarias.
- `0x0110D000`: 48 muestras prioritarias.

## Ensayos reales

| Sesión | Lecturas de datos válidas | Bytes muestreados | Objetos únicos | Bytes almacenados como objetos | Palabras densas variables |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 768 | 24576 | 159 | 5088 | 5 |
| 2 | 768 | 24576 | 159 | 5088 | 5 |
| 3 | 864 | 27648 | 211 | 6752 | 6 |

Las tres sesiones terminaron sin errores y con los seis controles de código correctos por sesión. Los bytes almacenados de la tabla excluyen manifiestos, recibos y exportaciones; la deduplicación ahorra bytes dentro de cada sesión, no se presenta como compresión global del proyecto. Los cambios se calculan entre tres pasadas, no entre frames.

La sesión 1 confirmó visualmente desplazamientos izquierda/derecha, pero derecha se produjo después del fin de captura debido a una demora entre acciones. Se conserva como acción fuera de cobertura y no se le atribuyen muestras. Para resolverlo se creó `run_citra_archive_trial.py`: inicia el lector y programa izquierda un segundo a los seis segundos y derecha un segundo a los dieciocho, sin depender del tiempo entre mensajes del asistente. Comprueba que el lector siga activo antes de cada entrada y utiliza la herramienta existente que verifica ventana/PID/ruta/foco y libera la tecla. Ante fallo de entrada no intenta la siguiente.

En sesiones 2 y 3 ambas pulsaciones quedaron íntegramente dentro de la captura; los recibos registran down/up aceptados por Windows. La observación final muestra la partida funcionando, pero no se observaron visualmente ambos movimientos intermedios de esas sesiones automáticas; por eso sus acciones conservan visually_verified=false. No se transforma aceptación de entrada en confirmación visual.

## Exportación y nueva información

Se reconstruyeron y verificaron **nueve archivos locales de 8192 bytes**, tres por sesión, contrastando el hash de cada objeto y la continuidad de direcciones antes de escribir. Son pasadas de memoria muestreada; **no son archivos originales recuperados del juego**. Se guardan sólo en analysis-local y no se publican bytes comerciales.

El analizador genera hashes de las exportaciones, palabras de 32 bits que variaron y estadísticas de cada ventana prioritaria. Esto permite reproducir la comparación y acotar futuras búsquedas. No identificó todavía coordenadas, modelos, animaciones, nombres originales de recursos ni contenedores nuevos. La actividad de contadores y del entorno sigue siendo una explicación alternativa de los cambios.

Las horas de lectura delimitan una operación que incluye hasta una espera de planificación antes de enviar RPC; no son marcas de frame. Los recuentos de lecturas que intersectan las acciones son intervalos del host, no prueba de causalidad o de que todo el bloque se leyera mientras el personaje se movía.

## Integridad y reproducción

Nueve pruebas correctas cubren deduplicación y exportación, rechazo de sobrescritura, objeto alterado, índice alterado, sesión incompleta, huecos/direcciones duplicadas, objeto existente corrupto, identidad con recorrido de ruta, separación de lecturas prioritarias y contabilidad corrupta. Son nueve métodos, con varias propiedades por método; sus repeticiones no se cuentan como pruebas nuevas.

- Captura: `citra_session_archive.py capture --image <code.bin> --mapping <receipt.json> --address 0x0110BC00 --size 8192 --sweeps 3 --probes 0x0110CF40 0x0110D000 --out <carpeta nueva>`.
- Análisis: `citra_session_archive.py analyze <sesión>` valida manifiestos, controles, índices, objetos y contabilidad antes de informar.
- Exportación: `citra_session_archive.py export <sesión> --sweep 0 --out <archivo nuevo>`; rechaza sobrescribir.
- Prueba coordinada: `run_citra_archive_trial.py --image <code.bin> --mapping <receipt.json> --out <carpeta nueva> --window <HWND observado> --exe <ruta exacta a citra-qt.exe>`. Requiere Citra en primer plano y teclas/modificadores sueltos. No reutilizar un HWND de otra sesión. El lector es sólo lectura; el coordinador realiza las entradas de juego explícitas.

## Próximas prioridades

1. Usar las ventanas prioritarias para reducir candidatos y contrastarlos con reposo, entradas y cambios de pantalla, manteniendo el límite global de lectura.
2. Demostrar las estructuras o rangos asignados antes de seguir punteros. Las ventanas siguen limitadas a BSS; no se escanea heap/VRAM arbitrariamente.
3. Un extractor de archivos del juego necesitará límites y estructura de contenedor verificados, compresión y hashes de origen. Encontrar una firma o exportar memoria no demuestra esa reconstrucción. El archivo de sesiones aporta evidencia reutilizable para llegar a ello.

Los lectores terminaron, las teclas quedaron liberadas y Citra siguió ejecutando la partida. No se tocaron originales, firmware, plugins, montajes, FTP o archivos de Vita.

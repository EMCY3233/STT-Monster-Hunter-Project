# Changelog maestro — Start The Travesy, Monster Hunter

## 2026-10-21 — STT-MON-003 / agente Vita experimental

- CI del commit 610c076 confirmado correcto: [Actions 39542198933](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39542198933).
- Implementado agente independiente VitaSDK con IP privada editable, inicio manual, envío STT/1 no bloqueante, límite de 60 intentos, parada/salida y corte tras tres errores consecutivos. No incluye monitorización de otros juegos.
- Añadido codificador C portable, validación de destino y pruebas cruzadas C → protocolo Python en CI.
- Preparado build remoto con imagen VitaSDK fechada, dependencia de pantalla fijada por commit y artefacto VPK experimental con hash. Resultado de compilación pendiente al crear esta entrada; consultar el workflow de la rama.
- Sin ejecución en Vita, transferencias FTP, cambios de firmware/plugins, instalación de software local ni borrado de juegos. Compatibilidad física pendiente de autorización y pruebas.

## 2026-10-21 — STT-MON-002 / análisis de capturas

- Confirmada ejecución remota correcta del primer commit: [Actions 39541986872](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39541986872), conclusión success. Esto resuelve el pendiente de CI de STT-BOOTSTRAP-001.
- Añadido analizador JSONL por IP, origen declarado y sesión; cuenta muestras únicas, duplicados, llegadas fuera de orden y huecos entre secuencias observadas. No atribuye huecos a pérdidas de red ni autentica dispositivos.
- Añadidas cuatro pruebas de análisis; el ensayo de dos procesos CLI se incorpora también a CI.
- Validación local Windows/Python 3.12.14: **10/10 pruebas OK** y **ensayo CLI PASS**, diez muestras simuladas, cero rechazos. Nueva ejecución remota pendiente al publicar este commit.
- Revisión oficial de APIs y límites del entorno en vita-agent/API_REVIEW.md. No hay toolchain utilizable localizado; sin compilación Vita, VPK ni prueba física. No se instaló software del sistema.
- Limitación del analizador: mantiene las secuencias únicas en memoria; utilizar capturas acotadas. No añade métricas de juegos ni modifica los registros de entrada.
- Se mantienen las restricciones sobre consola, FTP, firmware, plugins y juegos.

## 2026-10-21 — STT-BOOTSTRAP-001 / STT Vita Monitor 0.1

Zona de referencia: Europe/Madrid. Primera base de desarrollo autorizada en EMCY3233/STT-Monster-Hunter-Project.

### Inspección y preservación

- `git ls-remote` no devolvió referencias y la clonación informó repositorio vacío. No había commits ni archivos remotos que sobrescribir.
- La carpeta de trabajo contenía ESPACIOS_DEL_PROYECTO.md fuera del clon; se leyó y se conserva intacta. Los nombres/dependencias de las áreas proceden de ese mapa.
- Confirmación del usuario: FTP WinSCP operativo, PS Vita 1000, firmware 3.65 HENkaku/ensō, VitaShell, SD2Vita 64 GB. No se verificó la consola directamente.

### Añadido

- Estructura inicial con documentación técnica de áreas 01–10, alcance, dependencias y aceptación pendiente.
- Receptor UDP Windows en Python, contrato STT/1 estricto de hasta 1024 bytes, registro JSONL por adición con hora UTC e IP de origen; escucha local por defecto.
- Generador finito con etiquetas explícitas de simulación y sesiones independientes.
- Seis pruebas automatizadas de protocolo/recepción y ensayo reproducible con dos procesos CLI.
- Workflow CI para Windows/Linux y Python 3.11/3.13; su ejecución remota no se ha verificado en esta entrega.
- Diseño mínimo de agente Vita y plan de prueba STT-MON-001, sin código nativo no compilado.

### Validación ejecutada

- Entorno local Windows, Python incluido en el entorno de trabajo: `python -m unittest discover -s tests -v`: **6/6 OK**.
- El intento inicial dentro del aislamiento no recibió UDP local (falló una prueba). Repetición autorizada fuera del aislamiento: seis pruebas correctas, sin cambiar el código.
- `python tests/smoke_cli.py`: **PASS**, dos procesos, diez muestras simuladas, cero rechazos, secuencias 0–9 y etiqueta simulator comprobadas. Archivos temporales eliminados al terminar el ensayo.
- Inactividad automatizada: OK. Duplicados y reordenación preservados: OK. No equivale a probar desconexión Wi-Fi física.

### Pendientes y bloqueos

- VitaSDK no localizado (`VITASDK` ausente); no se compila ni entrega VPK. APIs nativas y compatibilidad pendientes de investigación y validación.
- Sin mediciones de FPS, memoria, consumo, rendimiento sostenido o actividad de otros juegos.
- Sin conexión a consola, cambios de firmware/plugins, borrado de juegos ni transferencia FTP. La prueba física necesita autorización adicional.
- Sin funciones de juego implementadas ni viabilidad de port nativo demostrada. Los documentos de áreas son planes iniciales.
- STT/1 carece de autenticación/cifrado y el archivo de registro no tiene rotación automática; no exponer a Internet y limitar ensayos.

Trazabilidad: el commit Git que introduce esta entrada contiene todo el prototipo y su documentación. No se incorporan cambios de otros chats ni recursos de juegos.

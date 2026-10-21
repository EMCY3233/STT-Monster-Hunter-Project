# Changelog maestro — Start The Travesy, Monster Hunter

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

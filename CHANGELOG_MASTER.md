# Changelog maestro — Start The Travesy, Monster Hunter

## 2026-10-21 — STT-RESEARCH-002 / consolidación de investigación y áreas

- Inventariados siete archivos locales, 7.861.039.260 bytes, mediante lectura completa y SHA-256; dos pasadas con hashes idénticos. [Resultados y límites](docs/research/game-inputs-2026-10-21/README.md).
- MHFU: ISO9660, ULES01213 y DISC_VERSION 1.01 observados en SFO. MH3U: CIA/TMD con contenidos marcados como cifrados. MH4U y MHXX: cabeceras de conjuntos 7z divididos con CRC correcto; carga comprimida sin prueba completa. La carpeta MHGU no acredita una edición Switch. Sin Frontier inventariado.
- Seis pruebas sintéticas nuevas aprobadas. La ejecución amplia local tuvo 15/16 (fallo UDP previo dentro del entorno restringido); no se presenta como diagnóstico de red. CI del commit 1b68b5b correcto: [Monitor tests 39547319058](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39547319058) y [Vita agent build 39547319029](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39547319029). Estos resultados corresponden a ese commit, no a futuras revisiones.
- Incorporada la documentación de [Frontier Clásico](docs/research/frontier-classic/README.md): 13 registros de investigación, fuentes y vacíos explícitos. Selección del usuario: corte de retirada + corte evasivo + estocada perforante cargable. La fusión propuesta es diseño original; Extremo permanece independiente. Sin botones, tiempos ni parámetros internos históricos confirmados.
- Actualizados portada, estado consolidado y fichas 01–10 con dependencias y siguientes pasos. Respuestas de Diseño 02/04/07 y contratos propuestos 03/05/08 registrados; no equivalen a inspección independiente ni aprobación de implementación.
- Conservados originales y trabajo del monitor. Solo documentación, metadatos y código propio en [PR #3](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/3), independiente y sin recursos comerciales. Ninguna instalación, transferencia a Vita ni actividad FTP en este frente.
- Pendientes: prueba íntegra de 7z, identidad interna accesible, clasificación de contenedores/ejecutables, evidencia primaria Frontier y validación de interfaces. No se demuestra un juego nativo ni adaptación de assets.

## 2026-10-21 — STT-MON-004 / primer ensayo físico y pantalla 0.2

- [Ensayo físico STT-MON-001](docs/STT-MON-001-hardware-result.md): 60 muestras, secuencias 0–59, cero rechazos, huecos, duplicados o llegadas fuera de orden; batería declarada 91 %. Salida con START confirmada por el usuario.
- VPK 0.1 transferido con autorización a carpeta nueva y verificado por lectura de vuelta. Excepción temporal del firewall autorizada por separado y retirada al terminar; retirada comprobada.
- Usuario informa texto pequeño y parpadeo. Corrección 0.2: fuente duplicada, filas estables que se redibujan solo si cambia el texto, sin borrar toda la pantalla cada 50 ms. Añadidos saltos de +/-10 para editar IP con menos pulsaciones.
- Compilación 0.2, codificador C e inspección de paquete correctos ([Actions 39545465268](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39545465268)); pruebas PC correctas ([Actions 39545465267](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39545465267)). Usuario confirma en Vita texto mayor y desaparición del parpadeo. [PR #2](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/2) integrada.
- VPK 0.2 transferido con hash verificado. Instalador y carpeta de transferencia 0.1 eliminados de Vita, y VPK/ZIP anteriores eliminados del PC; conservados paquete vigente y registros. Preferencia de limpieza futura registrada en AGENTS.md.
- Pendientes: nuevo ensayo de telemetría en 0.2, desconexión, suspensión y parada con Círculo. La confirmación visual no sustituye esas pruebas.

## 2026-10-21 — STT-MON-003 / agente Vita experimental

- CI del commit 610c076 confirmado correcto: [Actions 39542198933](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39542198933).
- Implementado agente independiente VitaSDK con IP privada editable, inicio manual, envío STT/1 no bloqueante, límite de 60 intentos, parada/salida y corte tras tres errores consecutivos. No incluye monitorización de otros juegos.
- Añadido codificador C portable, validación de destino y pruebas cruzadas C → protocolo Python en CI.
- Primer build remoto **correcto**: [Actions 39542902949](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39542902949), commit c84c58e. Compiló el agente y superó la prueba del codificador C contra Python; artefacto experimental generado (46.612 bytes de ZIP de Actions, no tamaño del VPK).
- Imagen VitaSDK fijada después por el digest observado en ese build; dependencia de pantalla fijada por commit. Añadida inspección automática de hash, contenido y cabeceras del paquete; su primera ejecución queda pendiente hasta publicar este cambio.
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

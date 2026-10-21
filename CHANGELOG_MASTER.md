# Changelog maestro — Start The Travesy, Monster Hunter

## 2026-10-21 — STT-MON-009 / diagnósticos visibles en el PC

- Receptor con opción `--live`: muestra cada recepción, sesión, secuencia, batería y diagnóstico STT/2; distingue contadores previos y último error conservado, que puede ser histórico. STT/1 se identifica sin diagnóstico.
- Conserva JSONL, contrato, comportamiento por defecto y recepción sin respuestas. No infiere parada/desconexión del silencio ni modifica el agente Vita 0.5.
- Validación local: 16 pruebas correctas y ensayo CLI de diez muestras simuladas con salida en directo. Primer intento dentro del sandbox bloqueó recepción loopback/temporales; repetición fuera del sandbox correcta. CI remota pendiente al publicar. Sin prueba física nueva, FTP ni reinstalación.

## 2026-10-21 — STT-MON-008 / límite temporal durante suspensión 0.5

- Corrige el control que usaba solo reloj de proceso: [presupuesto conservador proceso+RTC](docs/suspend-deadlines.md), con parada ante lectura fallida/retroceso y protección ante saltos/desbordamientos.
- Comprueba 180 s antes de transmitir al reanudar y usa el mismo presupuesto para los 30 s sin conexión observada. Muestra «Tiempo de limite» sin cambiar uptime_ms ni STT/2.
- Pruebas C de reloj/política, compilación Vita e inspección VPK correctas ([CI Vita](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39552818266)); quince pruebas PC y ensayo CLI correctos ([CI PC](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39552818196)). VPK 0.5 transferido con hash verificado e instalación/apertura confirmadas.
- [Prueba física](docs/STT-MON-008-suspend-result.md): suspensión breve con 39 s de presupuesto y 15 envíos; suspensión larga termina con 181 s, 14 intentos/14 envíos y «Parado: limite total», confirmado por usuario. PC recibió 14 muestras y ninguna posterior mientras receptor/firewall seguían activos.
- Receptores cerrados y retirada del firewall comprobada. Instaladores 0.4 anteriores retirados, conservando paquete vigente y evidencias. Sin transferencia por este cierre documental.
- No cambia el reloj ni ajustes de la consola. Pendientes físicos: límite sin red durante suspensión y fallos/retrocesos de reloj; cubiertos automáticamente, sin validación física de todas las rutas.

## 2026-10-21 — STT-MON-007 / recuperación automática acotada 0.4

- Implementada [política de recuperación](docs/auto-recovery.md): consulta de estado con SceNetCtl, pausa sin consumir intentos durante desconexión y recreación del socket al volver la conexión o después de un fallo de envío.
- Mantiene STT/2 y la sesión durante la recuperación. Límites: 30 s desde desconexión observada, cinco fallos consecutivos de apertura/envío, 180 s totales y 60 intentos reales. Círculo/START mantienen parada/salida manual.
- Pruebas C portables de transición/socket/límites, compilación Vita e inspección VPK correctas ([Actions 39550515715](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39550515715)). Quince pruebas PC y ensayo CLI correctos ([Actions 39550515789](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39550515789)).
- [Validación física 0.4](docs/STT-MON-006-auto-result.md): primer intento detenido por cinco fallos según usuario, con falta de señal observada. Repetición con 60 muestras 0–59 de la misma sesión, pausa de 53,863822 s y regreso sin otro Cruz confirmado por el usuario. Sin errores de envío nuevos declarados; diagnóstico histórico preservado.
- La pausa del PC excedió el avance del reloj de proceso: suspensión no aislada y límites de tiempo de pared no validados durante ella. No se afirma causa raíz identificada ni todas las rutas de recuperación verificadas.
- VPK 0.4 transferido, verificado e instalado; instaladores 0.3 retirados de Vita y PC. Receptor cerrado y retirada de firewall comprobada. Sin nuevas transferencias por este cierre documental.
- No se atribuye una causa raíz nueva a 0x80412112; esta revisión intenta recuperar la comunicación y conserva diagnóstico. Sin modificaciones de firmware/plugins, perfiles Wi-Fi ni juegos.

## 2026-10-21 — STT-MON-006 / fallo Wi-Fi y diagnóstico 0.3

- [Ensayo Wi-Fi 0.2](docs/STT-MON-004-wifi-result.md): PC recibió 39 muestras 0–38; usuario informó 60 intentos, 46 envíos aceptados, 14 errores y último retorno 0x804101CD (SCE_NET_ERROR_ERETURN). No se observó recuperación de recepción; causa subyacente todavía no identificada.
- Captura cerrada y excepción temporal retirada. Sin modificar firmware/plugins ni borrar juegos.
- Revisión 0.3: captura sceNetErrnoLoc inmediatamente tras fallo, conserva último código/detalle en RAM y los añade a STT/2. Receptor/analizador compatibles con STT/1 y STT/2. Nuevo socket en cada inicio manual con Cruz; sin promesa de reconexión automática.
- Quince pruebas PC y ensayo CLI correctos en Windows/Linux Python 3.11/3.13 ([Actions 39548761830](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39548761830)). Compilación C/Vita e inspección VPK correctas ([Actions 39548761895](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39548761895)).
- [Prueba física 0.3](docs/STT-MON-005-diagnostic-result.md): tras el corte, usuario informa 60 intentos/51 envíos/9 errores, retorno 0x80412112 y errno 205. PC recibió 46 muestras; recuperación automática no observada. Al pulsar Cruz sin cerrar la aplicación llegaron las 60 muestras de la sesión nueva y el error anterior se recibió automáticamente por STT/2. Recuperación manual y transporte del último diagnóstico validados; causa raíz pendiente.
- Actualización transferida y verificada; instaladores 0.2 anteriores eliminados en Vita y PC. Receptor cerrado y retirada del firewall comprobada. Este cierre documental no requiere nuevas transferencias ni reinstalación.

## 2026-10-21 — STT-MON-005 / parada con Círculo validada en 0.2

- [Resultado físico de recepción y parada](docs/STT-MON-003-stop-result.md): último ensayo con diez mensajes, secuencias 0–9 sin huecos internos, duplicados ni desorden; usuario confirma «Parado» y contador detenido tras Círculo. Sin nuevos mensajes durante diez segundos de observación adicional.
- Captura completa: veinte mensajes en tres sesiones, con prefijo 0–1 ausente en la primera. No se declara ausencia de pérdida para toda la captura ni reconexión Wi-Fi validada.
- Receptor de prueba cerrado; retirada de excepción temporal de firewall comprobada. Sin transferencias ni reinstalación por este cambio documental.
- Pendientes: ensayo completo 0.2, desconexión y suspensión. Informe automático de errores al PC todavía no implementado; los errores actuales se muestran solo en Vita.

## 2026-10-21 — STT-MON-004 / primer ensayo físico y pantalla 0.2

- [Ensayo físico STT-MON-001](docs/STT-MON-001-hardware-result.md): 60 muestras, secuencias 0–59, cero rechazos, huecos, duplicados o llegadas fuera de orden; batería declarada 91 %. Salida con START confirmada por el usuario.
- VPK 0.1 transferido con autorización a carpeta nueva y verificado por lectura de vuelta. Excepción temporal del firewall autorizada por separado y retirada al terminar; retirada comprobada.
- Usuario informa texto pequeño y parpadeo. Corrección 0.2: fuente duplicada, filas estables que se redibujan solo si cambia el texto, sin borrar toda la pantalla cada 50 ms. Añadidos saltos de +/-10 para editar IP con menos pulsaciones.
- Compilación 0.2, codificador C e inspección de paquete correctos ([Actions 39545465268](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39545465268)); pruebas PC correctas ([Actions 39545465267](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39545465267)). Usuario confirma en Vita texto mayor y desaparición del parpadeo. [PR #2](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/2) integrada.
- VPK 0.2 transferido con hash verificado. Instalador y carpeta de transferencia 0.1 eliminados de Vita, y VPK/ZIP anteriores eliminados del PC; conservados paquete vigente y registros. Preferencia de limpieza futura registrada en AGENTS.md.
- Recepción y parada con Círculo validadas posteriormente en STT-MON-005. Siguen pendientes ensayo completo 0.2, desconexión y suspensión.

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

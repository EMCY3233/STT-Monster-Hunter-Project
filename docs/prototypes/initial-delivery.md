# STT — Prototipos iniciales Vita: entrega revisable

21 de octubre de 2026. Implementación original; ninguna PR se ha fusionado.
Base main revalidada `410b1dd70a3713b500a829aed55cb99cb74ad1d0`; AGENTS.md leído.
Las investigaciones PR3 y PR7 no se modificaron ni aportan datos al prototipo.

| Trabajo | PR | Responsabilidad |
|---|---|---|
| Contratos | [#8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/8) | contracts/, validador STT/3 y pruebas cruzadas |
| A e integración | [#11](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/11) | vita-prototype/, adaptador y CI Vita |
| B | [#10](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/10) | asset-lab/, inspector PC y formato original |
| C | [#9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/9) | combat-lab/, núcleo C99 y demo/tests PC |

A incluye una copia Git del mismo núcleo C y contratos para poder compilar por sí
sola desde main sin merges previos. No hay dependencia del inspector ni de assets
comerciales. La revisión/integración posterior deberá reconciliar las secciones
aditivas de CHANGELOG_MASTER.md; no fusionar las PR automáticamente.

## Evidencias separadas

| Gate | Resultado y evidencia |
|---|---|
| Contratos PC | 19 tests locales, C→Python y conservación /1 /2; [CI del commit b685bbec](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560447959) aprobada |
| B PC | 23 tests, Windows/Linux Python3.11/3.13; [CI f06e289f](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560156907) aprobada |
| C PC | límites/combos/hitboxes/vida/dedup/replay10.000 ticks y enums cortos; [CI dad7350b](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560710412) aprobada |
| A PC | controles/cámara/adapter/render y C→Python con sanitizadores; [CI e6416fb9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560756730) aprobada |
| Compilación Vita | GCC15.2.0 en SDK fijado; mismo run39560756730, build correcto |
| VPK | job119091458348 valida checksum/SELF/SFO STTP00001; descarga e inspección local repetida con el mismo hash |
| Recepción PC | pruebas PC sintéticas /1 /2 y adaptación STT/3; ninguna recepción desde este VPK: transporte desactivado |
| Hardware | sin acceso FTP/local desde Work, sin instalación ni confirmación física |
| GUI B | pruebas numéricas de242 poses×3 cámaras; sin revisión visual GUI en este entorno |

Primer build Vita run39560398532 falló por comparación de enum sin signo con cero.
Se corrigió sin suprimir advertencias, con regresión de estado negativo y compilación
`-fshort-enums`. La evidencia correcta es el nuevo run39560756730.
Una imagen del framebuffer renderizado en PC se revisó visualmente; no es captura de Vita.

## Paquetes y hashes

| Archivo | SHA-256 |
|---|---|
| stt_vita_prototype.vpk (51.745 bytes) | e8b0a0bded89881c9a79a035028bec04fbed2bd99e85533abc662a0af993ffa5 |
| stt-asset-lab-0.1.zip | 916638957260b3a7eea59581fcde8b83d539706faf294958d4a4360c8928fe99 |

VPK del commit de código `e6416fb952ea050f3b785c852417e5bc58cd3f88`,
[artefacto12327970553](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560756730/artifacts/12327970553),
conservado por CI hasta4 de noviembre de2026. ZIP B del commit
`f06e289f5209806b767a09814c920901bc4df606`,
[artefacto12327770274](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560156907/artifacts/12327770274),
hasta28 de octubre de2026. Los hashes de ZIPs contenedores de Actions son distintos
de los archivos internos anteriores. Ambos archivos internos se descargaron y
contrastaron localmente; el ZIP B coincide con el paquete local regenerado.
Los commits posteriores de esta entrega cambian documentación, no el código probado.
No se transfiere ni reinstala un binario por un cambio solo documental.

## Ejecutar y probar localmente

**Vita:** verificar hash con `Get-FileHash .\stt_vita_prototype.vpk -Algorithm SHA256`.
Con el checkout de la PR11, ejecutar
`python vita-prototype/tests/inspect_package.py <carpeta-con-VPK-y-SHA256SUMS>`.
La identidad debe ser **STTP00001 / STT Vita Prototype /00.10**;
el monitor existente es **STTM00001** y debe permanecer intacto.
VitaShell debe mostrar el destino real y espacio suficiente. Mediante la conexión
FTP local ya autorizada, crear únicamente la carpeta del proyecto si hace falta,
copiar a `ux0:data/STT-Prototypes/stt_vita_prototype.vpk` cuando ese sea el montaje
verificado, y comprobar por lectura de vuelta el hash antes de instalar.
No cambiar montajes, firmware, plugins, juegos o partidas. No abrir firewall desde
este encargo. Abrir la burbuja STT Vita Prototype.

Stick izquierdo desplaza; derecho orienta cámara; Cruz ataca y encadena al pulsar
otra vez dentro de los últimos8 ticks de recuperación; Triángulo reinicia;
START sale. Tras suspender/reanudar, soltar sticks y botones para continuar.
Registrar: movimiento, cámara, HP100→90 al primer impacto, un daño por ataque,
reinicio, salida y reanudación. FPS30 es objetivo, pendiente medir físicamente.
Guardar recibo de destino/hash/instalación y observaciones del usuario.

**Asset Lab:** extraer ZIP, entrar en `stt-asset-lab`, disponer de Python3.11+
y Tk y ejecutar `python -m stt_asset_lab samples/practice-dummy.stt.json`.
Sin pantalla: añadir `--validate`. El paquete contiene Python ejecutable, no EXE.
Play/Pause, Clip y Bones permiten inspeccionar la muestra original. Admite únicamente
STT Asset/1 documentado, no MOD/LMT/formatos Monster Hunter. Contrato en metros,
conversión a mm/binding al motor deliberadamente desacoplados.

**Combat Lab:** comandos de demo y pruebas en [combat.md](combat.md).
Compilar `combat-lab` con CMake/CTest o GCC C99 según ese documento; no requiere Vita.

## Límites pendientes

No telemetría UDP del VPK; buzón local de capacidad1, eventos descartables y esquema
STT/3 listo para un adaptador de envío futuro. Hunter HP100 es sintético: no recibe daño.
Solo un objetivo, hitbox experimental simple, animación de espada por estado, suelo
sin colisión de terreno. Render CPU480×272, sin garantía de30FPS físicos ni clipping
completo de near-plane. Suspensión y rutas de error probadas en lógica/compilación,
pendientes de observación física. Extensión acuática null, sin natación implementada.
No soporte de modelos comerciales, rig avanzado, skinning ponderado o importadores
Monster Hunter. No se necesita ningún decoder no validado para ejecutar esta entrega.

## Revalidación al cierre

Main continúa en410b1dd. Se observaron avances concurrentes ajenos a este encargo:
PR3 ahora7ae447d29a4d3d82978c626ff862fb32944e2122 y
PR7 ahora097f64f31b4133f6f721cdd25d69efc51700f867; también apareció PR12 documental
del monitor. No se editaron esas ramas ni se incorporaron sus investigaciones.
La base y los datos originales de los prototipos no dependen de esos avances.
ZIP B descargado de CI: validación CLI real correcta,4 huesos,48 vértices,
clips Idle y Practice swing. Se eliminaron únicamente los dos ZIP contenedores
propios de descarga después de verificar los paquetes internos; se conservan
paquetes vigentes, recibos, evidencias e historial Git.

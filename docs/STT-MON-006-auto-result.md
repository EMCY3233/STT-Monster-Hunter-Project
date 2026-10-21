# STT-MON-006 — recuperación 0.4 en hardware

21 de octubre de 2026. Paquete 00.40, fuente 0d25d27; STT/2. Instalación y arranque de 0.4 confirmados por el usuario.

## Primer intento y repetición

El primer intento produjo doce mensajes, secuencias 0–11. El último llegó 111,863039 s después del anterior; no se tomó ese paquete aislado como prueba de flujo recuperado. El usuario informó falta de señal y posteriormente parada por cinco fallos de red. Los contadores finales no se copiaron de pantalla; no se dedujo una causa raíz ni se ocultó este resultado.

Se repitió con la misma 0.4, sin reinstalar. El procedimiento solicitado fue iniciar otra sesión con Wi-Fi conectado, cortar la radio unos cinco segundos y volver al monitor sin pulsar Cruz de nuevo. El usuario confirmó después «funcionó».

## Evidencia de la repetición

| Observación del PC | Resultado |
|---|---|
| Mensajes de la nueva sesión | 60 |
| Secuencias | 0–59 completas, sin duplicados ni desorden |
| Primera / última recepción | 07:48:15.134847 / 07:50:18.756416 (Europe/Madrid) |
| Mayor pausa entre recepciones | 53,863822 s, entre seq 15 y 16 |
| Cambio de uptime en esa pausa | 8049 ms |
| Identificador de sesión antes/después de la pausa | El mismo |
| send_errors declarado en las muestras de la sesión nueva | 0 |
| Último error preservado desde el intento anterior | 0x80410140, net_errno 64 |
| Batería declarada | 89 % |

Se confirma continuación de recepción en la misma sesión después del corte y regreso a la aplicación, sin un nuevo inicio según el procedimiento y confirmación del usuario. El error histórico no indica errores nuevos: sus contadores se reiniciaron por sesión y el último diagnóstico persiste por vida del proceso.

La duración física exacta de radio apagada no se instrumentó. Entrar en Ajustes puede suspender el agente: la pausa del PC fue mayor que el avance de su reloj de proceso. Esta prueba no aísla la suspensión ni demuestra qué ruta interna recreó el socket; no mide latencia. Los límites temporales del código usan el reloj del agente y **no quedan acreditados como límites de tiempo de pared durante una suspensión**. Debe investigarse un reloj adecuado y hacer esa prueba por separado.

## Artefacto y cierre

- Build, pruebas C de recuperación y paquete: [Actions 39550515715](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39550515715), correctos.
- Quince pruebas PC y ensayo CLI, Windows/Linux Python 3.11/3.13: [Actions 39550515789](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39550515789), correctos.
- VPK verificado por lectura de vuelta: SHA-256 `11a0f6b520e2057bf50417d53acccec125f006d565f72ea755537560831bf556`.
- Instaladores 0.3 eliminados de Vita y PC; conservados paquete vigente y evidencias. No se reinstala por el cierre documental.
- Receptor cerrado; excepción temporal del firewall retirada y ausencia comprobada a las 07:50:47.
- JSONL local completo: 72 mensajes en dos sesiones; SHA-256 `41c69e1464f239c58a838302e1bb7ea866a20b5586373a328987f488c684d9a3`. No se publican IP ni identificadores de sesión.

Sin cambios de firmware/plugins ni juegos. Pendientes: suspensión y reloj aislados, cortes prolongados/repetidos, entrega sin confirmación UDP y causa raíz específica de 0x80412112.

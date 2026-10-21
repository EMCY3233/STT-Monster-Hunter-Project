# STT-MON-005 — diagnóstico y recuperación manual en 0.3

21 de octubre de 2026. Paquete 00.30, código b24ddf1, STT/2. Instalación, arranque y línea «Detalle red» confirmados por el usuario.

## Corte Wi-Fi

Tras confirmar recepción, el usuario informó apagar Wi-Fi unos diez segundos, reactivarlo y volver al monitor sin pulsar Cruz. Al finalizar: 60 intentos, 51 envíos aceptados localmente, 9 errores, último retorno `0x80412112`, detalle 205 (`0xCD`).

El PC recibió 46 mensajes de la sesión, secuencias 0–45, de 07:24:06.336171 a 07:24:51.700487 (Europe/Madrid). Los últimos mensajes recibidos aún indicaban cero errores porque precedían al fallo. Cinco envíos aceptados localmente no aparecen en la captura; no se atribuye la diferencia a una causa concreta. No se observó recuperación automática.

La cabecera oficial identifica errno 205 como [SCE_NET_ERETURN](https://github.com/vitasdk/vita-headers/blob/master/include/psp2common/net.h). El significado específico del retorno `0x80412112` no quedó establecido con fuentes primarias; no se usa para afirmar una causa raíz. La intervención en Ajustes puede implicar suspensión del proceso y no aísla ese factor.

## Recuperación manual e informe automático

Con Wi-Fi reactivado y sin cerrar la aplicación, el usuario pulsó Cruz. Ese inicio recrea el socket y genera otra sesión.

- PC: **60 mensajes, secuencias 0–59**, completos, sin duplicados ni desorden.
- Diagnóstico de todos los mensajes recuperados: send_errors=0 para los intentos previos de esa nueva sesión.
- El primer mensaje de la nueva sesión ya transportó last_result=`0x80412112` (codificado con signo) y net_errno=205. No hubo que copiar esos valores manualmente para recibirlos en el PC.
- Último error conservado y contadores de la nueva sesión tienen ámbitos distintos: un código histórico distinto de cero no significa que el ensayo nuevo esté fallando.
- Recepción de la sesión nueva: 07:28:34.736680–07:29:29.119652 (Europe/Madrid). Las horas de llegada no garantizan periodicidad exacta ni miden latencia de red.

Validado: recuperación **manual** con nuevo inicio y transmisión del último diagnóstico preservado una vez restablecida la conectividad. No hay reconexión automática ni historial completo de cada error; cerrar la aplicación borra ese estado en RAM.

## Artefacto y cierre

VPK SHA-256 `5cadd1b633c1c49362fb13d3997a8ed99bf23d5e92a4f90510910d0546c3d5ad`, compilado e inspeccionado en [Actions 39548761895](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39548761895). Quince pruebas y ensayo CLI PC correctos en [Actions 39548761830](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39548761830).

Se eliminó el instalador 0.2 de Vita y sus copias VPK/ZIP del PC, conservando versión vigente y evidencias. Receptor cerrado; excepción temporal de firewall retirada y ausencia verificada a las 07:29:55. No se modificaron firmware/plugins ni juegos.

Registro íntegro local, sin publicar IP ni identificadores de sesión: SHA-256 `c25e90edee0ada6e82b0e7c840c4dbb0be70934a3c71250bb64a4e5108363626`.

Pendientes: causa raíz del retorno, reconexión automática, pruebas de suspensión aislada y rendimiento sostenido.

# Seguimiento MOD230 — aceptación parcial

Se cotejaron objeto del banco y copia local de990bytes, SHA-256 `ec1b20b25f022db69ba759bb525e0e9a88d05c2ccaf727812d900a61efc280b0`, y los tres recibos contra [evidencia PR7/10f3f10](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/10f3f10/docs/research/stt-re-20261021/mod230-smallest-evidence.json). SQLite conserva su hash de registro. No se añade derivado: el objeto ya está catalogado y la copia de ensayo es idéntica. No se repitió el lector ni la extracción ARC desde este frente.

Investigación comprobó una muestra MOD230, entrada377 de common.arc: tablas en límites,16registros de posición/UV finitos, stride28 y28índices de malla dentro de0–15. Cabecera global declara30índices, pero solo caben29u16 desde su puntero; faltan2bytes para ese rango. Min/max declarados0/0 no coinciden con rango observado0–15. Se conservan las discrepancias sin añadir relleno ni atribuir corrupción.

Ocho pruebas sintéticas nuevas aprobadas según propietarioPR7; no reproducidas aquí. Geometría completa, área/winding, ejes, transformaciones, materiales y visualización no validados. Esta muestra declara cero huesos/skins y no permite validar skinning o asociación de animación. No se extrapola a otros modelos.

Áreas02/07: antes de importar, resolver interpretación del contador global y min/max frente a referencia específica de esta revisión. Área04: metadatos generales, sin atribuir función ni clasificar armas. Próximo ensayo: contraste documental limitado sobre la misma muestra; no ampliar modelos/JKR ni adaptar recursos comerciales.

## Contraste de convenciones: discrepancia delimitada

[Investigación PR7/4d0e9a9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/4d0e9a9/docs/research/stt-re-20261021/mod230-index-conventions.md) encontró que un lector público explícitamente MH4U/E6 lee cantidad de malla+un u16:29índices,58bytes desde932,hastaEOF990. El índice adicional añade una terna con repetición; ambas ventanas mantienen seis ternas de índices distintos. No es comprobación de área/winding.

Ese lector deja sin usar el u32 que RevilLib denomina dos campos min/max. Su semántica MHXX no está probada:0/0 frente a0–15 es diferencia de interpretación, no corrupción confirmada. El contador global30 permanece sin explicación específica MHXX. No se rellena ni corrige el archivo. Geometría completa no validada; cierre del ensayo como delimitación, sin ampliar modelos.

Aquí se cotejó SHA-256 del recibo `index-conventions.json`: `a970b3c73b866af6022e038b190efcdb840da4359c499297ac9c82d287e5a215` y copia fuente contra evidencia. Cuatro pruebas nuevas pertenecen a investigación y no se repitieron. Fuente documental fijada:mhff6ef14c8ffa341ccbe44e0e6a93eb4bfe541265cf, aplicabilidad declarada MH4U/E6; no implica compatibilidad MHXX. Banco y derivados sin cambios.

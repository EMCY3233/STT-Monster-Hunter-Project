# MH4U: análisis de Val Habar — 22 de octubre de 2026

## Mejora de movimiento: pulsaciones largas y combinadas

`hold_citra_arrow.py` admite ahora 0,1–30 segundos y de una a cuatro teclas distintas. Se repite `--key` para mantenerlas juntas, por ejemplo `--key left --key down --seconds 4`. Se añade `dash`, asignada a W/R según el perfil local. No admite direcciones opuestas ni teclas arbitrarias. Los recibos incluyen `keys` y la tecla de cada evento; las pulsaciones se envían consecutivamente y se mantienen solapadas, sin prometer simultaneidad exacta a nivel de fotograma.

Diez pruebas automatizadas superadas cubren duración, foco incorrecto, pérdida de foco, fallo parcial al pulsar y fallo de liberación. En este último caso se intenta liberar igualmente el resto de teclas. La comprobación de foco continúa cada 10 ms durante la espera. No se cambia la configuración del emulador.

Pruebas reales privadas:

- `citra-village-diagonal-20261022-001.json`: izquierda + abajo, 4,000 s; cuatro eventos aceptados y desplazamiento visible desde Guildmarm hacia la calle central.
- `citra-village-three-keys-20261022-001.json`: izquierda + arriba + dash, 0,813 s; seis eventos aceptados y desplazamiento visible hacia el lado de la forja. No se midió velocidad ni se aisló el efecto de dash frente a caminar.

El máximo de 30 segundos se verificó como límite de software; la prueba real más larga de esta serie fue de cuatro segundos. El campo `movement_verified` sigue falso en los recibos automáticos: la observación visual se registra aquí por separado.

Estado parcial: se mantiene el análisis dentro de la aldea. No se ha aceptado ni iniciado una misión en esta serie.

## NPC principales: forja y Courier

Se respeta el orden solicitado: primero NPC de puestos/servicios; los NPC que caminan por la calle se dejan para el final. No se declara completo el recorrido de principales.

### The Man — forja

La aproximación directa desde la calle encontró un aparente borde/obstáculo. Tras retroceder hacia el frente y moverse lateralmente se alcanzó el aviso «A The Man». Esto prueba una ruta de acceso observada, no la geometría de colisión interna. A abrió la conversación con cambio de cámara. Se completó la presentación y se abrió Smithy.

Servicios visibles: Forge Weapons, Forge Armor, Upgrade Equipment y Forge Palico Gear. La ayuda inicial abrió «About the Smithy»; Cancelar regresó al índice, con temas de forja, mejoras, Insect Glaive Growth, Activating Skills y equipo Palico, además de entradas aún ocultas. Otra cancelación cerró la ayuda y devolvió el menú. Se cerró el servicio sin fabricar, mejorar ni comprar.

Muestras privadas separadas `village-forge-dialogue-007` y `village-forge-menu-008`: cada una 22 lecturas/244 bytes, controles de código coincidentes y candidatos 100/600. No se identificó variable de NPC o servicio. Recibos de navegación y botones: `citra-village-forge-20261022-001` a `016`.

### Courier — servicio fijo

Se observó el aviso «A Courier» y se inició su presentación. El diálogo explicó Guild Cards y StreetPass. Ante la pregunta de activación se usó Cancelar; apareció Yes/No con No seleccionado y se continuó con Cancelar. El menú posterior confirmó visualmente StreetPass Off, Quest (None), Palico (None), con Inbox y StreetPass como opciones. La ayuda tenía About the Courier, The Inbox y StreetPass Settings. No se abrieron funciones de intercambio.

Al salir apareció «Save StreetPass settings? Game progress will be saved as well». Cancelar seleccionó No; se observó esa selección antes de A, que confirmó No y llevó a la despedida. No se aceptó guardar. Una pulsación previa para avanzar texto fue rechazada por revisión automática por posible activación de StreetPass; no se ejecutó ni se reintentó por otro medio. Se continuó con la alternativa de cancelar y con observación de cada pantalla.

La navegación de Courier está registrada en recibos `citra-village-forge-20261022-017` en adelante (el prefijo heredado no significa que esas capturas correspondan al herrero). No se interpreta la aceptación de una tecla como prueba de activación de una función; cada transición descrita fue observada en pantalla.

### Caravaneer y mercado

Se habló con Caravaneer tras observar su aviso A. El diálogo pidió Well-done Steak o Rare Steak, remitió a Guildmarm y terminó de vuelta en Val Habar. No hubo aceptación de misión ni salida. Durante esta conversación se observaron habitantes caminando por el fondo; todavía no se les abordó, respetando el orden pedido.

Se recorrió la calle hasta que apareció «To Gathering Hall». No se pulsó A allí y se retrocedió hacia el mercado exterior. El aviso «A Val Habar Market» permitió iniciar y completar la presentación de la comerciante.

El menú ofrece Buy, Sell y Buy & send to Box. Se abrió únicamente el catálogo Buy y se observaron las cuatro páginas: básicos/herramientas, barriles y otros suministros, munición y recubrimientos, y libros. Ejemplos visibles: Herb 20 z, Whetstone 80 z y Neopterons Vol 1 100 z. Los fondos permanecieron en 1500 z. La ficha de Normal S Lv2 mostró 0 en bolsa y 99 en caja; no se deduce de ello el contenido completo de la caja. No se compró, vendió ni transfirió nada.

La lectura privada `village-market-catalog-009` contiene 22 lecturas/244 bytes con controles de código coincidentes y los mismos candidatos 100/600. Los recibos de Caravaneer y mercado continúan la serie `citra-village-forge-20261022-040` a `062`; los intentos fallidos por pérdida de foco no se cuentan como acciones.

### Street Cook: regalo y primera correspondencia dinámica de inventario

Se alcanzó el aviso «A Street Cook» y se completó su presentación. Explicó sentarse a la mesa para pedir comida; hablar con él no consumió comida. Al finalizar entregó automáticamente un regalo: apareció «Voucher placed in Pouch». La bolsa se abrió después y mostró Voucher, cantidad 1, en su primer slot. No se consumió ni descartó el regalo. Por tanto, la bolsa dejó de estar vacía debido a un evento del juego, no a una escritura de memoria.

Se compararon las capturas privadas `village-item-pouch-006`, `village-market-catalog-009` y `village-voucher-after-010`, comprobando hashes de muestras, índices y cada ventana comparada. En las dos primeras, las dos lecturas del candidato de inventario v1.0 de 32 bytes estaban a cero. Tras el regalo, ambas lecturas devolvieron en los primeros cuatro bytes dos u16 little-endian: (842, 1); los otros 28 bytes permanecieron a cero. Es evidencia de correspondencia temporal con Voucher ×1 y apoya la hipótesis «identificador u16 + cantidad u16», limitada al primer slot y a esta versión/sesión. No prueba todavía los otros slots, el catálogo completo de IDs, los límites de cantidad ni la persistencia en el guardado.

La comparación queda en `analysis-local/ctrpf-mh4u-reference-20261022/voucher-comparison.json`; los datos comerciales crudos permanecen locales. La captura adicional `village-voucher-visible-011` se tomó con Voucher ×1 visible para permitir repetición del contraste. Cada captura posterior al regalo contiene 22 lecturas/244 bytes, sin escrituras de memoria. Recibos del recorrido y cocinero: `citra-village-forge-20261022-063` a `079`.

Prioridad siguiente: terminar el resto de principales accesibles, después abordar habitantes móviles. Para el inventario, comparar un segundo objeto o un cambio legítimo de cantidad antes de generalizar el layout. Mantener el Voucher mientras tanto. No salir a campo abierto aún.

La repetición con Voucher ×1 visible (`village-voucher-visible-011`) verificó nuevamente hashes y devolvió (842, 1) en ambos barridos del primer slot candidato.

## Intentos finales con habitantes móviles

Tras cerrar los seis NPC principales encontrados en este circuito (Guildmarm, The Man, Courier, Caravaneer, Market y Street Cook), se observaron e intentaron interceptar habitantes que recorrían la calle. Un habitante con ropa clara pasó inmediatamente junto al personaje en la zona de la forja. Se hicieron dos pulsaciones A de 0,2 s (`...-091` y `...-092`), ambas aceptadas y liberadas por Windows. No apareció nombre/aviso A ni se abrió conversación. El habitante continuó su recorrido entre observaciones.

Resultado: conversación móvil **no confirmada**. No se concluye que todos los habitantes móviles sean decorativos o no conversables: la distancia exacta, orientación y latencia entre observación y entrada no están medidas. No se identificó nombre para ese habitante. El ensayo permite distinguir el éxito de los servicios con aviso A del resultado negativo de esta interceptación. Los recibos `...-080` a `...-090` documentan navegación y aproximación; no implican nuevas conversaciones principales.

Estado final: Val Habar, juego en marcha, sin misión aceptada, sin entrada a Gathering Hall ni campo abierto. Voucher ×1 conservado. Aún no se declara exhaustivo el conjunto de NPC de toda la aldea ni de servicios desbloqueables.

## Evidencia observada

- Desplazamiento mediante flechas sostenidas: dos pulsaciones de derecha de 1,5 s, otra de 0,6 s y aproximaciones hacia arriba. La cámara y posición relativa al puesto cambiaron visiblemente.
- Dos intentos iniciales de A no abrieron diálogo. La aceptación de SendInput por Windows no prueba una interacción del juego.
- Tras aproximarse al puesto apareció el aviso «A Guildmarm». A sostenida 0,2 s abrió una conversación con nombre Guildmarm y cambio de cámara. Otra pulsación avanzó el texto. No se ha confirmado ninguna opción de misión.
- Una muestra durante el diálogo obtuvo 22 lecturas de datos, 244 bytes, con controles de código antes y después coincidentes. La raíz candidata v1.0 permaneció estable y dentro del intervalo de la referencia; la v1.1 no cumplió ese intervalo y no se siguió.
- Los cuatro candidatos u16 de salud devolvieron 100; los dos candidatos float de resistencia, 600. Coinciden con la muestra anterior de estado. No se ha demostrado propiedad de la estructura, identidad semántica ni relación causal con la conversación.

Las muestras y recibos permanecen privados en `analysis-local/ctrpf-mh4u-reference-20261022/village-dialogue-004` y `analysis-local/citra-village-*-20261022-*.json`. No se publican memoria ni recursos comerciales.

## Controles y alcance

El auxiliar existente añade únicamente A (interactuar), S (cancelar/B) y M (menú/Start), según el perfil local observado. Las letras usan scan codes sin el indicador de tecla extendida; las flechas sí lo usan. Conserva la validación de ejecutable, ventana en primer plano, límite temporal y liberación en `finally`. No remapea el perfil ni escribe memoria.

## Pendiente antes de campo abierto

### Segunda serie: introducción y mostrador completos

La introducción de Guildmarm terminó y abrió el mostrador. La NPC indicó que solo ofrece Caravan Challenges en este estado. La categoría visible fue una estrella; su listado contenía «Steak Your Ground». La ficha mostró entrega de un Well-done Steak o Rare Steak, A. Steppe, 50 minutos, recompensa de 60 z y tarifa de 0 z. Se inspeccionó la ficha sin pulsar Confirm. Dos cancelaciones regresaron primero a categorías y después a la despedida; A cerró la despedida y restauró la vista libre de Val Habar. No se aceptó misión.

Se capturó otra muestra acotada en el listado (`village-quest-list-005`): 22 lecturas, 244 bytes y controles de código coincidentes. Los candidatos de salud y resistencia conservaron 100 y 600 respectivamente; no distinguen los estados observados.

El menú de aldea conserva la página seleccionada: abrió en 2/2, y el control táctil izquierdo cambió a 1/2. En ella se observaron Item Pouch, Combine, Combo List, Quest Info, Palicoes, Hunter's Notes, Friends y Chat; algunas opciones aparecían atenuadas. A abrió Item Pouch, página 1/4, con los slots visibles vacíos. Esto no verifica todavía las otras tres páginas ni el contenido de la caja.

Dos intentos de entrada fueron rechazados por el auxiliar porque Citra había perdido el primer plano. Sus recibos indican `executed: false`; no se cuentan como acciones del juego. Tras activar y observar de nuevo la ventana, las entradas posteriores funcionaron.

Se comprobaron después las páginas 2/4 y 3/4 de Item Pouch y 4/4, titulada Gunner's Pouch: todos los slots mostrados estaban vacíos. No se usaron, ordenaron ni descartaron objetos. La muestra privada `village-item-pouch-006` añadió 22 lecturas/244 bytes con controles coincidentes; devolvió los mismos candidatos 100/600. Esta inspección verifica las cuatro páginas de la bolsa, no la caja de almacenamiento.

1. Completar la lectura de la conversación inicial de Guildmarm y salir sin aceptar misión.
2. Repetir abrir/cerrar diálogo y comparar muestras etiquetadas de reposo, aviso y diálogo. Los datos actuales no justifican un detector de conversación.
3. Inspeccionar otro NPC, inventario y servicios de aldea; registrar las opciones visibles y las transiciones efectivas. No declarar servicios completos por haber abierto un solo diálogo.
4. Mantener separadas las observaciones visuales, los recibos de entrada y las hipótesis de memoria. La lectura RPC sigue siendo asíncrona, sin una instantánea atómica.

## Trabajo independiente de recursos

Se creó el chat «STT — Extracción y conversión de recursos» (`01a16188-302c-7412-8f39-29ad0e3938a9`). Tiene prohibido controlar esta sesión de Citra y trabaja en su propia área. Su informe de cierre comunica análisis de 51 MOD y 51 MRL, 99 coincidencias de hash de materiales, 91 referencias exactas de texturas y seis pruebas superadas; estos resultados se atribuyen a ese trabajo, sin una segunda validación aquí. Véase su PR independiente: https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/27 . La interpretación de slots del shader y la conversión completa de animaciones siguen pendientes.


## Instalaciones, armería y sincronización

Serie posterior: se observó inicialmente el personaje junto a Val Habar Armory; no se atribuye al asistente el trayecto previo a esa primera observación. Se completó la presentación de la armería y se verificaron Buy Weapons, Buy Armor y Sell, cerrando sin transacciones.

| Instalación | Entrada observada | Regreso observado | Alcance |
|---|---|---|---|
| Gathering Hall | Aviso To Gathering Hall, carga y presentación; mapa Gathering Hall, Offline | Aviso To Val Habar y exterior Val Habar | Sin misiones aceptadas; NPC interiores aún no auditados |
| Your House | Aviso To House y habitación visible | Aviso To Town y exterior Val Habar | Housekeeper conversado; Gallery y Downloadable Content visibles, sin descargas |
| Item Box exterior | Aviso Open Item Box y vista Take Items | Cancelar devuelve a menú y calle | Primera página de doce; Potion ×10 visible, sin transferencias |
| Quest Gate | Etiqueta del mapa confirmada | No se salió | No confundir con habitación; sin misión activa |

La navegación por la rampa tuvo tramos con desplazamiento reducido o aparente borde. El mapa táctil aclaró la identificación: el icono norte corresponde a Quest Gate; Your House está junto a Guildmarm. La ruta final confirmada hacia la casa pasó por delante de ese puesto y luego a la derecha. El manual oficial confirma que tocar marcadores muestra el nombre de instalaciones: https://game.capcom.com/manual/MH4U/en/page-23.html . No se afirmó viaje rápido mediante esos marcadores.

La muestra facility-box-potion-012, con Potion ×10 visible en primer slot, devolvió (8,10,31,5) como cuatro u16 del candidato de ocho bytes, igual en los dos barridos. Solo los dos primeros se comparan con la ficha seleccionada: identificación candidata 8 y cantidad 10. Los siguientes dos no reciben etiqueta semántica aquí. No hubo cambio controlado de cantidad, por lo que es correspondencia de un estado.

El auxiliar de movimiento permite 0,1–30 s y hasta cuatro controles compatibles; se probó ahora up+dash seis segundos, con liberación aceptada y llegada visible al aviso de Gathering Hall. Continúa sin modificar el perfil ni escribir memoria. El nuevo audit_game_input.py comprueba orden de eventos y liberación de pulsaciones aceptadas; sus cuatro pruebas incluyen fallos parciales. No convierte aceptación de Windows en prueba de efecto dentro del juego. Los recibos fallidos por foco no se cuentan como movimiento.

La copia de recursos fue sincronizada con la evolución de MH4U, manteniendo su exclusión del control de Citra y de esta rama. Su PR #27, head 9c196193c182c469b3beaf79b51328c57f1b3c22, informa 83 MRL, 168 registros, 1344 descriptores y 166 enlaces únicos de nombres MOD a registros MRL; 12 pruebas. Se verificaron metadatos y estado de la PR; no se repitió aquí su ejecución. Los significados de slots y shaders siguen siendo hipótesis. https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/27

Estado: Citra en Val Habar tras volver de la casa, sin misión ni expedición iniciada. Se conservaron el Voucher y el almacenamiento. Próximos experimentos: NPC de Gathering Hall, servicios interiores pendientes y una segunda transición legítima de inventario para probar el layout. El recorrido no es un inventario exhaustivo de funciones desbloqueables. Datos, capturas y recursos comerciales permanecen privados.

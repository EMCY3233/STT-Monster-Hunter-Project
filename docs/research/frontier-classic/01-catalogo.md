# Paso 1 — Catálogo de Espada Larga Frontier

## Método y alcance

Separar Tierra (地ノ型), Cielo (天ノ型), Tormenta (嵐ノ型) y Extremo (極ノ型). «Frontier Clásico» es el nombre del diseño STT que reunirá rasgos de los tres primeros; no identifica una versión histórica del juego. Traducciones españolas descriptivas, no nombres oficiales localizados.

Estados por campo: **P** = fuente primaria leída; **L** = pista de investigación, todavía no validada por fuente primaria; **D** = diseño STT; **?** = desconocido. Ninguna fila hereda automáticamente la certeza de otra. No usar ausencia de evidencia como prueba de ausencia de movimiento.

No se ha ejecutado Frontier, observado su motor, medido fotogramas ni comprobado botones en hardware. Todos los valores de daño, alcance, tiempos, invulnerabilidad, costes, acumulación, cancelación y número exacto de impactos permanecen desconocidos salvo indicación primaria expresa. Un valor desconocido debe representarse como `null`, nunca cero.

## Registro de fuentes

| ID | Fuente y localizador | Tipo y resultado | Uso permitido en esta revisión |
|---|---|---|---|
| P01 | [PlayStation Blog, 25-12-2017, Hunter](https://blog.ja.playstation.com/2017/12/25/20171225-mhfz/), secciones sobre estilos y 太刀 | Publicación de la plataforma, leída | Contexto Z de finales de 2017, cuatro estilos, Extremo independiente y sus rasgos anunciados |
| P02 | [PlayStation Blog, anuncio 07-04-2017](https://blog.ja.playstation.com/?p=4361), sección 使用可能ランク変更 | Publicación de la plataforma, leída | Cambio anunciado para 19-04-2017 en requisitos de Tormenta y Extremo; no documenta botones |
| P03 | [Manual oficial G, page120](http://cog-members.mhf-g.jp/sp/manual/page120.html) | URL histórica; apertura fallida | Ningún contenido técnico verificado |
| P04 | [Manual oficial Z, page120](https://cog-members.mhf-z.jp/sp/manual/page120.html) | Apertura fallida | Ningún contenido técnico verificado |
| V01 | [Vídeo enlazado por P01: Extremo, entrega 4](https://www.youtube.com/embed/SJ2ar_8awng?feature=oembed) | Enlace identificado desde publicación primaria; vídeo no recuperado | Candidato audiovisual; sin marcas de tiempo ni mediciones |
| L01 | [ネ実 MHF-Z, 太刀](https://w.atwiki.jp/giurasu/pages/873.html) | Síntesis comunitaria, pista | Índice de nombres y preguntas; no autoridad para confirmar parámetros |
| L02 | [ネ実 MHF-Z, Cielo](https://w.atwiki.jp/giurasu/pages/496.html) y [Tormenta](https://w.atwiki.jp/giurasu/pages/497.html) | Síntesis comunitaria, pistas | Localizar sustituciones y rutas para validación primaria |
| L03 | [4Gamer, 19-01-2015](https://www.4gamer.net/games/034/G003450/20150119035/), sección 太刀 | Recopilación editorial de demostraciones; texto leído, clips no inspeccionados | Localiza demostraciones etiquetadas Tierra y Cielo/Tormenta. No prueba transiciones ni entradas |
| L04 | [Famitsu, guía de inicio G](https://www.famitsu.com/sp/mhf/start_guide01.html), 太刀 | Guía editorial leída | Candidato para localizar demostración de carga; no se eleva a verificación primaria |

Los enlaces comunitarios/editoriales son pistas, no base de afirmaciones técnicas confirmadas. Recuperar una captura archivada exigiría anotar URL exacta de la captura, fecha y versión representada; no se ha recuperado ninguna aquí.

## Versiones que sí se pueden distinguir

P01 describe Tierra disponible desde HR1 y Cielo/Tormenta desde HR5 en el contexto de diciembre de 2017; Extremo aparece en Z en noviembre de 2016. P02 anuncia para abril de 2017 quitar la prueba de Tormenta y cambiar Extremo de GSR300 a GR1. Estas condiciones no deben retroproyectarse a G ni a versiones anteriores. La versión binaria, región, plataforma de cada demostración y revisión precisa de balance siguen pendientes.

Para el catálogo clásico se propone buscar una referencia G anterior a Z y registrar aparte cualquier evidencia Z sobre Tierra/Cielo/Tormenta. La elección de una revisión canónica requiere una decisión posterior; no mezclar parámetros de varias épocas.

## Inventario técnico de investigación

Todas las filas siguientes son **L**, salvo los campos de contexto explícitamente vinculados a P01/P02. Sirven para que el catálogo sea comprobable y ampliable; no autorizan implementar estas propiedades como históricamente demostradas.

| ID | Nombre original / traducción de trabajo | Estilo candidato y versión pendiente | Entrada histórica / condición por comprobar | Animación y recursos que se deben comprobar | Transición o pregunta de verificación | Pista |
|---|---|---|---|---|---|---|
| LS01 | 踏み込み斬り / corte con avance | Base Tierra; herencia Cielo/Tormenta por verificar | Ataque desde desplazamiento/desenvaine; botones ? | Paso frontal y corte vertical; acumulación ? | ¿Qué estados admiten inicio y qué corte sigue? | L01 |
| LS02 | 縦斬り / corte vertical | Base; revisión ? | Entrada contextual; botones ? | Corte sin avance según pista; recurso ? | Distinguir del LS01 y medir sus rutas | L01 |
| LS03 | 突き / estocada simple | Tierra/Cielo; sustitución Tormenta por validar | Entrada de estocada; botones ? | Trayectoria frontal; coste/ganancia ? | ¿Puede salir de evasión? ¿Se sustituye toda ruta en Tormenta? | L01/L02 |
| LS04 | 斬り上げ / corte ascendente | Base; revisión ? | Estado posterior a estocada por verificar | Arco ascendente; tiempos ? | Enumerar entradas/salidas sin asumir equivalencia con Cielo | L01 |
| LS05 | 斬り下がり / corte de retirada | Tierra; otras disponibilidades ? | Entrada de retirada; botones ? | Corte con retroceso por comprobar; coste ? | ¿Qué ataques lo habilitan y cuáles puede encadenar? **Candidato elegido para la fusión** | L01/L02 |
| LS06 | 気刃斬り 1/2/3 / cadena de espíritu | Base; herencia por estilo ? | Recurso 練気 y requisitos exactos ? | Cada fase y contactos por separar; gasto ? | Orden, interrupción, reanudación y reinicio de cadena ? | L01 |
| LS07 | ステップ斬り / corte con paso lateral | Tierra; disponibilidad restringida en otros estilos por verificar | Dirección + entrada contextual; botones ? | Paso lateral; no asumir invulnerabilidad | ¿Restricción a espíritu en Cielo/Tormenta? ¿Conserva índice de cadena? | L01/L03 |
| LS08 | 突き下がり / estocada de retirada | Tierra; introducción exacta ? | Entrada y condición ? | Retroceso con estocada por verificar | No confundir con LS05; disponibilidad en Cielo/Tormenta ? | L01/L03 |
| LS09 | 気刃放出斬り / corte de descarga de espíritu | Demostración Tierra localizada; otros estilos ? | Mantener espíritu según pista; umbral y coste ? | Preparación y liberación; contactos ? | No confundir con 解放連撃 de Extremo; ventanas ? | L01/L03 |
| LS10 | 避け斬り / corte evasivo | Cielo; herencia Tormenta por verificar | Entrada de acción sustituida; botones ? | Corte ascendente evasivo según pista; resistencia e invulnerabilidad ? | Sustitución de LS05, pérdida de LS08 y reinicio de cadena por comprobar. **Candidato elegido** | L01/L02/L03 |
| LS11 | 貫刺し / estocada perforante | Tormenta; revisión ? | Entrada de estocada según pista; botones ? | Estocada con posibles contactos múltiples; número ? | Sustitución de LS03 y efecto en salidas de evasión ? | L01/L02/L04 |
| LS12 | 貫刺し【強】 / variante cargada | Tormenta; revisión ? | Mantener entrada; requisito de 練気 lleno por comprobar | Carga y liberación; duración y consumo ? | Distinguir nivel de carga, impacto, recuperación y derivaciones. **Rasgo cargable del candidato LS11 elegido** | L01/L02/L03/L04 |
| LS13 | 前転突き / estocada desde voltereta | Tierra/Cielo candidatos | Estocada durante evasión según pista; botones ? | Posible salida anticipada; ventana ? | No asumir que cancela toda la evasión ni que existe igual en Tormenta | L01 |

LS06 agrupa provisionalmente tres fases: desglosar en registros individuales al obtener evidencia primaria. LS12 es variante de LS11; no contar ambos como dos ataques nuevos sin validar taxonomía. Este inventario no pretende demostrar exhaustividad: desenvaine, enfundado, evasiones, rebote e interrupciones requieren también su propia revisión.

## Entradas y condiciones: trabajo pendiente

No hay botones originales verificados. Registrar por separado esquema clásico/portátil, teclado/mando, plataforma y modificaciones de configuración. No traducir automáticamente R1 de PS3 a R de Vita. Una entrada semántica STT propuesta tampoco es prueba del control original.

Para cada registro completar: estado inicial; entrada pulsar/mantener/soltar/dirección; requisito de desbloqueo de esa revisión; energía antes y después; colisión o impacto fallido; comportamiento con resistencia insuficiente; salidas normales y cancelaciones. Los desbloqueos de P01/P02 son contexto de estilo, no precondiciones suficientes de cada ataque.

## Grafo de hipótesis por validar

No son combos confirmados. Son pruebas prioritarias sugeridas por L01/L02:

| Ruta candidata | Qué debe verse o documentarse |
|---|---|
| Espíritu 1 → Espíritu 2 → LS10 → Espíritu 1 | Reinicio de índice y coste neto; no extrapolar bucle infinito sostenible |
| LS10 → LS01 / LS03 / espíritu | Legalidad de cada salida por estilo/revisión |
| LS03 sustituido por LS11 en Tormenta | Si afecta también a derivaciones y evasiones |
| LS11 cargado → LS10 / LS09 | Ventana de entrada, recurso y diferencia entre contacto y fallo |
| Espíritu → LS07 → continuación | Conservación de índice y restricciones de Cielo/Tormenta |

## Animaciones, materiales y vídeo

No hay ID de animación, esqueleto, malla, VFX, audio ni formato comercial validado. «Ascendente», «retirada» y «carga» son descriptores de investigación, no archivos identificados. Para un prototipo futuro usar cápsulas, arma geométrica y animaciones propias; anotar autor/licencia antes de incorporar cualquier activo.

| Evidencia audiovisual | Situación | Inicio/fin | FPS / métricas |
|---|---|---|---|
| L03, clip etiquetado Tierra | Texto localizado; vídeo no inspeccionado | `null` | `null` |
| L03, clip etiquetado Cielo/Tormenta | Texto localizado; vídeo no inspeccionado | `null` | `null` |
| V01, Extremo | URL desde fuente primaria; apertura de vídeo fallida | `null` | `null` |

No inventar marcas temporales. Una secuencia de montaje no demuestra un combo legal. El FPS de un vídeo tampoco demuestra el tick del juego. Para medición futura: registrar autor, URL, versión visible o su ausencia, plataforma, habilidades/equipo, velocidad de reproducción, cortes, comienzo de entrada si es visible, primer/último contacto y recuperación. Repetir con fallo y contacto; conservar incertidumbre. Sin entrada visible no medir latencia de entrada.

## Extremo: registro independiente

P01 anuncia desplazamiento con arma desenvainada y, para Espada Larga, 瞬斬 tras una defensa precisa y 解放連撃. Esto justifica separar `frontier_extreme` de `frontier_classic`. No añadir estas funciones a la fusión clásica. Entradas, medidores, cifras y detalles de cancelación de Extremo siguen pendientes; V01 no se ha inspeccionado.

## Criterio para cerrar una ficha

Una ficha estará técnicamente verificada solo con fuente primaria que permita identificar versión/plataforma y comprobar cada afirmación, o captura propia reproducible de una instalación válida con ese contexto. Hasta entonces el catálogo es trazable, pero parcialmente pendiente de verificación. Consultas realizadas y errores de acceso se registran como tales, sin convertirlos en hechos del juego.

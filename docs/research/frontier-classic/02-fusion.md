# Paso 2 — Propuesta de Frontier Clásico

Estado: **D — diseño STT**, pendiente de revisión y prueba. El usuario seleccionó los tres candidatos el 21-10-2026. No son tres ataques originales ejecutados simultáneamente ni una mecánica confirmada de Frontier.

## Tres rasgos y una acción

Nombre provisional: **Retirada perforante**. Identificador propuesto: `stt.ls.classic.retreat_pierce.v0`.

| Referencia candidata | Rasgo que se quiere estudiar | Límite |
|---|---|---|
| LS05, 斬り下がり, Tierra | Reposicionamiento hacia atrás durante un corte | Distancia, daño y contactos propios pendientes; no se copia animación |
| LS10, 避け斬り, Cielo | Fase ofensiva con posibilidad de evasión temporal | Ventana de invulnerabilidad propia pendiente; no defensa precisa ni contraataque automático |
| LS11/LS12, 貫刺し, Tormenta | Convertir la preparación en una estocada liberable y cargable | Requisito, tiempo, coste y contactos propios pendientes |

Una acción continua: preparación vulnerable de la estocada; soltar ejecuta una retirada oblicua del cuerpo mientras el arma se extiende hacia el objetivo. La función evasiva propuesta se vincula a ese gesto de retirada y estocada, sin corte inicial separado. No hay tres bonificaciones completas superpuestas. Se toma de Tierra el control de distancia, de Cielo la intención evasiva y de Tormenta la estocada cargable. Número de contactos y balance todavía sin decidir.

No se elige LS08 (estocada de retirada) como sustituto de LS05 ni LS09 (descarga de espíritu) como sustituto de Tormenta. El origen conceptual queda fijado aunque las fichas históricas todavía tengan campos pendientes.

## Secuencia propuesta

1. El área 03 valida modo clásico, arma desenvainada, apoyo terrestre, estado habilitado y recursos según configuración. Con parámetros esenciales ausentes, la acción queda deshabilitada en un ejecutable futuro; no se rellena con ceros.
2. La entrada semántica `FusionBegin` crea una instancia y entra en `PreparePierce`. Seguir la propuesta de 03: compromiso inicial indivisible de coste aprobado e inicio; un rechazo no consume. No hay desplazamiento defensivo gratuito antes de pagar.
3. Mantener permite carga, sin invulnerabilidad. Soltar anticipadamente deja una solicitud para el primer punto legal, evitando perder un toque breve. Variante sin carga adicional pendiente de aprobación; no equivale a fallo ni cancelación.
4. `FusionRelease` produce `RetreatPierce` cuando la preparación permite salida y las condiciones persistentes siguen válidas. Fijar la carga y orientar el gesto al comprometer esa fase, sin segundo coste automático.
5. En `RetreatPierce`, torso y apoyos se retiran oblicuamente mientras la punta se extiende. Locomoción resuelve colisión; la cámara no modifica la dirección comprometida. Una ventana evasiva propuesta, limitada y gobernada por simulación, puede coincidir con parte del gesto; sus límites siguen pendientes. La animación comunica marcadores, no concede protección por sí sola.
6. `Recover` conduce a `Ready`. Encadenar un ataque requiere una arista explícita autorizada por 03; no se reinicia espíritu ni se obtiene cancelación libre por defecto.

Daño, rebote, derribo, pérdida de apoyo, cambio de medio, muerte y cancelación del sistema tienen prioridad sobre una liberación pendiente. No se ejecuta una estocada al recuperar el control tras una interrupción.

## Decisiones de riesgo para validar

Retirarse puede perder el alcance de la estocada. Cargar da al enemigo tiempo de actuar. El seguimiento hacia el objetivo debe tener límite definido y nunca teleportar al personaje. La colisión del escenario puede reducir la retirada; no debe conceder evasión extra por estar junto a una pared. El gesto requiere verificar que la punta alcanza al objetivo mientras el cuerpo retrocede; no se resuelve alargando el arma sin límite.

No condicionar daño aumentado a una supuesta «evasión perfecta» en esta revisión: eso añadiría una cuarta mecánica y acercaría el diseño a Extremo. El sistema de daño debe poder distinguir fase evasiva, colisión física y fallo de impacto.

## Parámetros sin fijar

| Grupo | Campos pendientes |
|---|---|
| Tiempo | Preparación, carga, recuperación, buffer y cancelaciones |
| Defensa | Inicio/fin de evasión, tipos de daño que evita, interacción con habilidades |
| Movimiento | Distancias, velocidades, giro máximo, reacción a borde y pared |
| Recursos | Tipo de energía, coste inicial, ganancia por contacto y posibles excepciones de reembolso |
| Impacto | Multiplicador, alcance, hitboxes, contactos, intervalo por objetivo, filo, elemento y estado |
| Cadena | Entradas desde ataques previos, salidas posteriores e índice de espíritu |

Todos los campos son `null` hasta elegir y justificar un diseño de prueba. Las cifras futuras de STT llevarán etiqueta `design_parameter`; no se presentarán como mediciones de Frontier.

## Animación propia y Extremo

Para prototipar bastan silueta y arma geométricas, movimiento creado expresamente y marcadores de fases. El contrato necesita marcadores de comienzo/fin de contacto, evasión, carga, compromiso, recuperación e interrupción. No se han generado activos ni adaptado archivos comerciales.

`frontier_extreme` utiliza otro conjunto de acciones/configuración. Esta propuesta no incorpora carrera desenvainada, 瞬斬, 解放連撃 ni medidores exclusivos. Cambiar de estilo durante una acción queda prohibido en el diseño inicial; la selección se resolverá fuera de combate salvo decisión documentada posterior.

## Aceptación futura

Comprobar con recursos propios: toque breve, mantener/soltar, interrupción antes y después del compromiso, falta de recursos, fallo de impacto, varios objetivos, pared, borde, pausa, entrada simultánea, cambio de medio y salida de misión. Verificar que una instancia no duplica consumos ni impactos y que ninguna cancelación deja invulnerabilidad activa. Esta es una lista de pruebas por ejecutar, no resultados obtenidos.

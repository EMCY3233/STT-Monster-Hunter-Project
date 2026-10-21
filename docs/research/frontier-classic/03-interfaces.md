# Paso 3 — Interfaces propuestas para 03, 05 y 08

Revisión 0.2, tras recibir respuestas de Diseño 03/04/05/08. Todos los nombres siguientes son un contrato documental propuesto, no APIs existentes del proyecto ni del juego original. No se han integrado con el monitor. La consolidación revisada no equivale a aceptación de implementación.

## Sobre común

Cada solicitud: `schema_version`, `action_id`, `action_instance_id`, `actor_id`, `simulation_tick`, `input_sequence`, `style_id`, `weapon_state`, `locomotion_mode`, `orientation`, `resource_snapshot`, `parameter_set_id` y `evidence_status`.

`style_id`: `frontier_classic` o `frontier_extreme`. `locomotion_mode`: `grounded`, `airborne`, `surface`, `underwater`, `transition`. Desconocido no equivale a terrestre.

Solo la simulación de combate autoriza efectos. El mando solicita intención; animación representa fases; locomoción resuelve desplazamiento. Los eventos de animación no deciden por sí solos daño, coste o invulnerabilidad. Los parámetros de diseño y datos históricos deben guardarse en campos distintos con su procedencia.

## Área 03 — Combate

| Entrada al contrato | Respuesta / responsabilidad |
|---|---|
| `CanStartAction(context)` | Aceptar o rechazar con motivo; rechazar configuración incompleta |
| `FusionBegin`, `FusionHold`, `FusionRelease` | Consumir solo en estados autorizados, con orden de entrada estable |
| `TryCommitPhase(instance, phase)` | Validar recurso y estado en la misma operación; impedir doble consumo |
| `Interrupt(instance, reason)` | Cerrar contactos y evasión, vaciar liberación pendiente, aplicar política de recursos |
| `RequestTransition(from, to)` | Resolver arista permitida; una animación compatible no demuestra legalidad |

Estados consolidados propuestos: `Ready → PreparePierce (carga opcional) → RetreatPierce → Recover → Ready`. Interrupciones llevan a un estado controlado de daño/cancelación del área 03. La retirada y la estocada forman un gesto ofensivo único; no hay corte inicial separado. Se reduce el desglose del primer informe de 03 para respetar la observación de 04 sobre fusión frente a concatenación.

Eventos de salida propuestos: `ActionAccepted`, `ActionRejected(reason)`, `PhaseEntered`, `ResourceReserved`, `ResourceCommitted`, `ReservationReleased`, `ContactOpened`, `ContactClosed`, `HitResolved`, `EvasionOpened`, `EvasionClosed`, `ActionInterrupted`, `ActionFinished`.

Regla consolidada de recursos, siguiendo 03: compromiso inicial atómico de coste, instancia y entrada en preparación. Rechazar no consume; interrupción posterior conserva gasto y no devuelve automáticamente. Sin costes continuos ni cobro adicional al soltar en esta propuesta. Tipo y cantidades pendientes. Si en una revisión se introducen reservas, liberarlas al interrumpir sin devolver gasto comprometido. Para impedir doble golpe: deduplicación por `(action_instance_id, contact_id, target_id)`; un movimiento multigolpe necesita distintos contactos autorizados, no repetir eventos de render.

Prioridad propuesta: interrupción de sistema/daño/medio > transición legal > liberación > nueva entrada. Si el orden preciso cambia, versionar el contrato. El buffer tiene duración pendiente y se vacía al interrumpir o cambiar de modo; no conservar liberación automática entre estilos.

Preguntas a resolver por 03: qué ataques pueden iniciar la acción; cómo se conserva el índice de espíritu; cuándo se gasta; qué implica rebote; si se admiten variantes de carga; qué cancelaciones dejan recuperación; cómo interactúan filo, habilidades y estados. No heredar reglas de MH4U/MHGU sin documentación.

## Área 05 — Natación MH3U

La acción propuesta solo se habilita en `grounded` en esta revisión. Esto es una decisión conservadora de prototipo STT, no una afirmación de incompatibilidad histórica. Una variante submarina requeriría otro `action_id`, orientación 3D, perfil de movimiento, colisiones y animaciones propias. No aplicar un multiplicador de velocidad a la animación terrestre y llamarlo adaptación MH3U.

| Evento | Comportamiento propuesto |
|---|---|
| Inicio en agua/superficie/transición/aire | Rechazar `unsupported_locomotion_mode`; informar al HUD |
| Entrada en agua durante preparación o carga | Interrumpir acción; borrar carga y liberación pendiente; conservar gasto inicial |
| Entrada en agua durante retirada-estocada | Interrumpir los efectos futuros; cerrar evasión/contactos y conservar eventos ya resueltos y gasto inicial |
| Salida del agua | No reanudar acción ni liberación pendiente; requerir apoyo terrestre y nueva entrada |
| Cambio de orientación por cámara | No reinterpretar trayectoria comprometida; locomoción autoriza la orientación válida |

05 posee medio, superficie, apoyo y restricciones de movimiento. 03 posee acción y recursos. En un tick con cruce de medio e impacto, procesar primero el cambio de medio y luego validar contactos; la regla debe ser estable y compartida. Las revisiones de multijugador quedan pendientes del área 10.

Pruebas futuras: borde de agua en cada fase; entrada y salida el mismo tick; pared bajo agua; cámara vertical; pérdida de apoyo; estados de daño; evento duplicado de cambio de medio. No se han realizado pruebas en MH3U ni Vita.

## Área 08 — Controles Vita

Separar `FusionBegin/Hold/Release` de la asignación física. Tras el informe de 08, candidato preferido para estudiar: **R + Triángulo** inicia; mantener R conserva preparación y soltar R solicita liberación. Triángulo puede soltarse tras reconocer el acorde. Stick izquierdo indica dirección inicial y derecho conserva cámara. Este perfil evita mantener un botón frontal con el pulgar mientras se usa cámara. La orientación final de estocada debe tener límites explícitos pendientes. Son botones propuestos STT, no controles históricos verificados.

R+Triángulo puede competir con espíritu, ataques simples y desenvaine. 08 debe elegir ventana de reconocimiento pendiente y resolver si retrasa esos ataques o exige otro contexto; no imponer latencia oculta. Evasión, cancelación, enfundado, objetos, interacción y menús requieren mapa global revisado. Hasta resolverlo, mapa provisional sin aceptación de implementación. No exigir L2/R2 ni pulsaciones L3/R3 físicas, ni panel trasero obligatorio.

Regla propuesta del perfil preferido: iniciar una sola vez al reconocer ambos botones; después mantener/soltar se refiere exclusivamente a R; inhibir nuevo inicio hasta soltar ambos. Soltar Triángulo no ejecuta estocada en este perfil. Interrupción limpia estado del acorde, pero no interpreta botones aún mantenidos como un inicio nuevo. El estado lógico es por jugador y secuencia de entrada. El informe original de 08 también ofrece mantener Triángulo, pero identifica el conflicto con cámara; no mezclar ambos perfiles en una misma interpretación.

Alternativa accesible: acción reasignable o modo pulsar para preparar / pulsar para liberar. Debe conservar las mismas reglas de recurso y vulnerabilidad; los indicadores de carga incluyen forma/texto además de color. El botón de cancelación semántica tendrá reglas de 03; no concede evasión gratuita.

HUD propuesto: estilo activo, medio compatible, preparación/carga, liberación disponible y motivo de rechazo. No mostrar números de carga o daño pendientes como si estuvieran medidos. El cambio de modo agua debe actualizar disponibilidad sin bloquear cámara.

Pruebas futuras de 08: acordes casi simultáneos y escalonados, soltado parcial, mantener al sufrir daño, entrar en menú/pausa, reconexión del mando, remapeo, accesibilidad, cámara durante carga y coste de reconocimiento frente a ataque simple. Sin pruebas físicas realizadas.

## Entrega a animación y validación

07 recibirá marcadores de fase y requisitos de assets propios después de revisión. 10 recibirá matriz de casos, resultado esperado y procedencia. Ningún marcador visual establece por sí mismo hitboxes, daño o evasión. Al faltar animación válida, conservar el prototipo abstracto; no adaptar recursos comerciales sin licencia registrada.

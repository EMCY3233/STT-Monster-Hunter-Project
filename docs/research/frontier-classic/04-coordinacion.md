# Registro de coordinación y verificación

Nota de consolidación: este registro describe el primer frente local, previo a su publicación documental en el PR #3. Las menciones a «fuera del repositorio» y ausencia de rama/PR corresponden a esa primera etapa. El inventario posterior confirma ausencia de Frontier; véase [coordinación 02/04/07](../game-inputs-2026-10-21/coordination.md).

21-10-2026, Europe/Madrid. Centro: Documentar Área 04 Espada Larga.

El usuario autorizó expresamente usar este chat para enviar órdenes y recoger respuestas. Los encargos se enviaron a chats existentes; no se crearon chats nuevos. Todos recibieron límites: documentación, sin cambios de repositorio, sin PS Vita/FTP y sin adaptar activos comerciales.

## Encargos y respuestas recibidas

| Chat | Encargo | Respuesta recuperada y aplicación |
|---|---|---|
| 04 · Diseño · Frontier Clásico unificado y Frontier Extremo | Catálogo con evidencia y propuesta de fusión | Catálogo inicial incompleto; manual inaccesible; sin vídeo observado. Confirma los tres elegidos. Recomienda un gesto continuo de retirada y estocada, sin concatenar tres ataques |
| 03 · Diseño · Combate y estilos MH4U/MHGU | Estados, consumo, cancelaciones y eventos | Propone compromiso inicial atómico, deduplicación, cierre único y cifras null. Incorporado como propuesta consolidada |
| 05 · Diseño · Natación y combate submarino MH3U | Contrato de cambio de medio | Respuesta recibida pese a error de ejecución transitorio anterior. Propone acción terrestre, cancelación de carga y prioridad del medio, sin herencia submarina automática. Incorporado |
| 08 · Diseño · HUD, controles y accesibilidad | Entradas, mapa Vita y accesibilidad | Propone R+Triángulo; advierte conflicto de mantener Triángulo con cámara y ofrece mantener R. Este último perfil se estudia como preferido; mapa global pendiente |
| Desarrolla el prototipo STT Vita | Comunicar aislamiento y solicitar restricciones, sin iniciar cambios por el aviso | Devuelve mantener separación, revisar procedencia y contratos e integrar mediante commit/PR trazable. Ninguna tarea del monitor se ha incorporado aquí |

Se envió la consolidación v0.2 a las cuatro áreas para objeciones. La recepción de informes iniciales no significa que hayan aprobado esta revisión posterior. Los chats de Work de áreas 03/04/05/08 no recibieron encargos de ejecución.

## Diferencias resueltas en la propuesta local

1. **Fusión frente a concatenación:** el primer borrador local tenía retirada con corte y estocada posterior. Se sustituye por preparación seguida de un solo gesto de retirada-estocada, respetando la observación de 04. La intención evasiva requiere ventana propia pendiente.
2. **Recursos:** el primer borrador permitía compromiso por fases. Se adopta la propuesta de 03 de un compromiso inicial indivisible, sin doble gasto al liberar. Cantidad y recurso pendientes.
3. **Cámara:** el borrador local Triángulo+Círculo no se adopta como preferido. Se estudia la alternativa de 08 con mantener R. Todavía puede colisionar con espíritu/desenvaine y no está aprobada como mapa global.
4. **Agua:** conservar cierre de contactos, eliminación de carga, gasto ya comprometido e impactos previos. No hay variante acuática aprobada ni prueba realizada en MH3U.

## Qué se verificó realmente

- Se leyeron el mapa local de espacios y las fichas iniciales 03/04/05/08 del repositorio, sin editarlas.
- La consulta inicial del checkout mostró `main...origin/main` sin cambios locales; ese estado pertenece a ese momento. El frente principal puede seguir trabajando después.
- Se consultó la conversación de origen; varias respuestas antiguas son referencias truncadas, por lo que no permiten reconstruir especificaciones ausentes.
- Se leyeron P01 y P02, identificando contexto de versión y separación de Extremo. No se verificaron parámetros internos.
- Se intentó abrir el manual oficial G y Z, sin obtener contenido. Se identificó un enlace de vídeo primario de Extremo, sin inspeccionar vídeo ni asignar tiempos.
- Se localizaron fuentes comunitarias/editoriales para orientar fichas pendientes; no se elevan sus cifras ni rutas a evidencia primaria.
- Se recuperaron respuestas completas de Diseño 03, 04, 05 y 08. Se conservaron sus reservas y se documentaron discrepancias.
- No se ejecutó juego, SDK, transferencia, adaptación de assets ni prueba de hardware. No se creó rama, commit o PR porque este directorio está fuera del repositorio.

## Siguiente verificación necesaria

| Prioridad | Trabajo | Condición de cierre |
|---|---|---|
| 1 | Recuperar evidencia primaria de Tierra/Cielo/Tormenta | Manual o demostración con procedencia, versión/plataforma y campo verificable |
| 2 | Confirmar entradas y rutas, especialmente LS05/LS10/LS11 | Documentación primaria o ensayo reproducible válido; no extrapolar Z a G |
| 3 | Fijar revisión canónica clásica | Registrar decisión; separar parámetros de cada época |
| 4 | Aprobar semántica, coste y controles de la fusión | Resolver objeciones 03/04/05/08 antes de implementación |
| 5 | Diseñar y medir prototipo con recursos propios | Casos de las interfaces con resultados; no reutilizar activos comerciales sin permisos |
| 6 | Integración documental posterior | Rama/PR independiente, revisión y preservación del trabajo principal |

La fase documental queda entregada para revisión con incertidumbres explícitas. El catálogo histórico completo y el balance de la acción permanecen pendientes; no declarar su verificación como terminada.

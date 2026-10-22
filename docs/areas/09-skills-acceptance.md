# Área 09 — Matriz preliminar de aceptación de habilidades y adornos

Estado: propuesta de criterios de prueba, **no** aprobación de reglas ni implementación.

## Encaje en el mapa del proyecto

El área 09 principal se denomina «Misiones, mapas, economía y progresión» (`docs/areas/09.md`). El sistema de habilidades y adornos es un **subtema de progresión**, no un reemplazo de las misiones, la economía o la persistencia.

## Base confirmada

La decisión de diseño registrada para el 21-10-2026 es la opción B: sistema clásico ampliado, con características de Frontier. Se pretende conservar puntos, umbrales, habilidades negativas, adornos y talismanes. Los valores numéricos, límites activos y compatibilidades **no están aprobados**.

## Matriz de aceptación propuesta (solo pruebas sintéticas)

| ID | Caso | Criterio comprobable | Decisión pendiente |
| --- | --- | --- | --- |
| A09-S01 | Suma de puntos | Un mismo conjunto de piezas produce siempre el mismo total de puntos | Tabla de fuentes de puntos |
| A09-S02 | Umbral positivo | Activar/desactivar una habilidad exactamente en el umbral configurado | Umbrales y niveles |
| A09-S03 | Umbral negativo | Aplicar una habilidad negativa solo cuando su umbral configurado se alcance | Tabla de efectos negativos |
| A09-S04 | Adornos | Añadir/quitar un adorno modifica únicamente los puntos que declara | Ranuras, costes y restricciones |
| A09-S05 | Talismanes | Sustituir un talismán recalcula los puntos sin arrastrar el estado anterior | Capacidades y combinaciones |
| A09-S06 | Efectos incompatibles | Un conflicto configurado produce un resultado explícito y reproducible | Reglas de precedencia |
| A09-S07 | Límite de activas | El motor respeta un límite **configurable**, sin fijar aquí su valor | Número máximo y excepciones |
| A09-S08 | Guardado/carga | Reabrir una configuración de prueba versionada reproduce los mismos puntos y activaciones | Formato y migraciones |
| A09-S09 | Desconocidos | Una habilidad no registrada no se convierte silenciosamente en una habilidad real | Política de error y compatibilidad |
| A09-S10 | Frontera con otras áreas | Los cálculos no modifican combate, inventario o persistencia fuera de interfaces declaradas | Contratos 03/08/10 |

## Condiciones antes de implementar

1. Área 01 valida alcance y prioridades; Área 09 define tablas de datos y compatibilidades; Área 10 revisa contratos y regresiones.
2. Cada valor concreto debe estar marcado como confirmado, experimental o pendiente y acompañado de procedencia.
3. Los tests deben usar datos **inventados y etiquetados como sintéticos**, no estadísticas atribuidas a juegos comerciales.
4. No usar ni redistribuir recursos comerciales; no modificar PS Vita.
5. No declarar una habilidad jugable ni una prueba física por pasar pruebas unitarias en PC.

## Próximo entregable sugerido

Un esquema JSON versionado mínimo de habilidades, puntos, umbrales y fuentes de equipo, con validación sintética y errores explícitos; sin seleccionar todavía valores de equilibrio.

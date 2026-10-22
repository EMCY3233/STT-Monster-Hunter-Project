# Lecturas guiadas, estado visible y catálogo de conversión — 22-10-2026

## Juego y fuentes de inicio

Se consultó el [manual oficial de controles en aldea](https://game.capcom.com/manual/MH4U/en/page-21.html): Circle Pad mueve, A permite hablar/confirmar y R al moverse permite correr. La [guía oficial de misiones individuales](https://game.capcom.com/manual/MH4U/en-UK/page-41.html) orienta a hablar con la Guildmarm y salir por la puerta tras aceptar una misión. Se localizaron páginas mediante búsqueda pública; algunas aperturas directas del sitio devolvieron 403. No se eludieron restricciones y no se usaron guías de otros Monster Hunter como si fueran MH4U.

Se abrió Menu → segunda página → Status y se observó **1500 Zenny, salud100 y resistencia100**. La consulta fue de sólo lectura. Los controles de código coincidieron durante el sondeo de memoria. La raíz v1.0 de la referencia EUR, nula en una etapa previa, ahora es estable y cumple sus guardas. Se siguió únicamente el bloque de 32 bytes relativo a +0x1180 tras una tercera comprobación de raíz.

Las cuatro vistas u16 de salud +0x1184/+0x1186/+0x1188/+0x1194 valen100; ambas vistas float a +0x118C/+0x1190 valen600. **Correspondencia de un estado**, no identificación completa: 6:1 es sólo una escala candidata de resistencia. Falta observar una variación normal y comprobar qué representa cada copia. El dinero candidato v1.0 coincide con los1500 visibles; aún falta una variación de dinero para confirmación causal. No se certifica toda la versión del juego por estos valores.

## Nueva sesión y juego realizado

Se cerró el estado y se ejecutó otra sesión de tres pasadas de BSS, 8KiB más dos ventanas prioritarias. **864 lecturas correctas, cero errores y seis controles de código coincidentes**. Izquierda/derecha un segundo se programaron mientras el lector seguía activo; ambos intervalos completos quedaron dentro de captura. Los recibos confirman aceptación de entradas y liberación; no hubo observación visual de cada movimiento intermedio. Se inspeccionó la partida después y se ensayó además un movimiento corto hacia arriba.

Un intento breve de A junto al personaje cercano no mostró diálogo confirmado; no se registra una conversación ni una misión iniciada. La siguiente comprobación semántica de resistencia requiere un estado donde pueda variar, no simplemente más muestras de aldea. Un fallo temporal al activar la ventana se recuperó seleccionando de nuevo la ventana real antes de continuar; no se reutilizaron coordenadas tras ese fallo.

## Mejora del extractor y catálogo

`extract_arc.py verify` ahora comprueba presupuestos declarados y observados antes de leer cada salida, total declarado, tamaño real del archivo e igualdad entre índice de tabla y nombre canónico. Esto evita que un manifiesto alterado con su hash recalculado dirija la verificación a un índice ajeno o declare lecturas excesivas. El hash de manifiesto sigue siendo integridad local, no firma de autenticidad.

Nuevo `catalog_conversion_scope.py`: valida primero el paquete extraído y después examina únicamente sus entradas MOD/TEX. Para MOD hace una conversión estática de prueba en memoria usando todas las restricciones del conversor; no escribe derivados. Para TEX comprueba la cabecera/rango admitidos, sin afirmar conversión de píxeles. Conserva SHA del ARC, manifiesto y carga, índice/ruta y razón de exclusión. No deduce materiales por nombres ni mezcla observaciones MH4U con los recursos MHXX.

Dos paquetes reales, common y quest, aportaron **261 ocurrencias** MOD/TEX: 24 conversiones OBJ de prueba correctas, 118 cabeceras TEX compatibles con el alcance actual y119 fuera de alcance. No son necesariamente recursos únicos: los hashes únicos por categoría son {"outside_current_converter_scope": 97, "tex_header_within_converter_scope": 92, "static_obj_dry_run_ok": 19}. Entre los OBJ de prueba hay desde6 hasta3904 triángulos en estas ocurrencias. No se exportaron masivamente ni se aceptaron recursos fuera del alcance por fuerza.

Cuatro pruebas nuevas cubren clasificación admitida/rechazada, paquete alterado, declaración de tamaño excesivo e índice de salida alterado. Las diez pruebas anteriores del extractor pasaron de nuevo; se registran como regresión, no diez pruebas nuevas. Los dos paquetes reales también pasaron el verificador reforzado antes del catálogo.

Uso: `catalog_conversion_scope.py <carpeta de extracción ARC verificada> --out <JSON nuevo>`. El informe de ejecución es local en `analysis-local/first-conversion-20261022/common-scope-catalog.json` y `quest-scope-catalog.json`.

## Alcance y siguiente experimento

Las lecturas nuevas afinan hipótesis de ejecución; la extracción estática mejora mediante comprobaciones de estructura y procedencia, no porque un contador revele automáticamente un archivo. Prioridad: variar resistencia dentro de una misión con un punto de estado confirmado; comprobar raíz y unidades antes de etiquetar campos. Para recursos, convertir de forma acotada candidatos distintos del catálogo y verificar material/esqueleto antes de animación.

No se activaron trucos, se escribió memoria o se cambiaron originales, banco, firmware, plugins, montajes o Vita. Los lectores finalizaron y las teclas se soltaron; Citra quedó ejecutando la partida. Recursos comerciales y capturas permanecen locales.

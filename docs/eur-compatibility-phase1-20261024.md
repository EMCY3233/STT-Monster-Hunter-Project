# STT: matriz inicial USA/EUR y plan de perfil regional

Estado: investigación inicial; pendiente de revisión regional de Claude y verificación efectiva de OpenCode. Objetivo fijado por el usuario: MH4U EUR. USA v1.3.0 es referencia de MH4UltimateDC, no baseline binario compatible por defecto. No hay ejecución de MH4U EUR ni port Vita demostrado en esta entrega.

## Coordinación y procedencia

Se leyeron AGENTS.md, el estado limpio del checkout y las PR abiertas. Rama documental nueva `docs/eur-compatibility-20261024` desde main `f199bd07b4e05ee4f7e56ed616840518374f3300`. No se modifican #45, #47, #48 o #50, ni sus archivos. La [auditoría #50](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/50) ya cubre arquitectura STT/MH y límites Vita: este documento añade el eje regional y no vuelve a implementar su trabajo.

El buzón compartido contiene revisión real de Claude sobre #50 (evento 7) y cinco tests del decoder ejecutados por Claude en Linux (evento 8). Son resultados reportados por ese agente, no pruebas repetidas por este informe. Se recibió la orden del usuario y se dejó el encargo EUR-01 a Claude, pendiente de respuesta. Se encoló revisión OpenCode, sin ejecutar por bloqueo gratuito 429. Un encargo en cola no acredita agente activo ni revisión concluida.

Etiquetas: **E-doc** documento/metadato inspeccionado; **R** resultado reportado sin reproducir aquí; **H** hipótesis/diseño pendiente; **N** no verificado. La ausencia de datos EUR significa N, no equivalencia ni diferencia confirmada.

## Fuentes consultadas

* **S1** [README MH](https://github.com/CompaLarios18/MH4UltimateDC/blob/main/README.md), blob `85bfecda8e77728de9e454723e55e56820212035`, leído el 24/10/2026. Declara USA v1.3.0, recompilación ARM/Thumb a C, plataforma Azahar y directorio de información por región. Jugabilidad y cifras son R del mantenedor, no medición STT.
* **S2** [RECOMPILER.md](https://github.com/CompaLarios18/MH4UltimateDC/blob/main/docs/RECOMPILER.md), blob `ed7cfe78966c8c5c5ca3e89f79b836ffe19f1539`. Pipeline, contrato RCtx, callbacks, hooks y tunables; cobertura y difftests reportados. No se importó implementación.
* **S3** [PORT_ARCHITECTURE.md](https://github.com/CompaLarios18/MH4UltimateDC/blob/main/docs/PORT_ARCHITECTURE.md), blob `e6ae540d390a76dac1a8ad6a613ed3e165bd41ec`. Separación CPU/plataforma/frontend; Azahar, SVC, páginas, fibers, GPU y audio. Puede conservar hitos anteriores al README; no armonizarlos como si toda la documentación tuviera igual fecha.
* **S4** [STT README A32](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/d91eb729647cea45dbd099a3fd03e4bded75796d/arm-leaf-lab/README.md), inspeccionado localmente en ese commit: nueve operaciones enteras no-S, sin memoria, ramas/llamadas, Thumb de entrada, VFP ni SVC. 1–65 instrucciones, BX LR final. Sus pruebas son sintéticas, no EUR.
* **S5** [Auditoría STT #50](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/b3fdcb4/docs/audit-stt-mh4ultimatedc-20261024.md), blob `fcd88d0cc6ddc0044ae32c8322ce8e8c76a959d9`. Inventario fijado a MH main `e06b0ca30b9b2d66ec7785f277ead4bb35374b28` y native `a6b71de1221e895312273d0378b7a2e8513955fa`; no mezclar ramas. Su inventario local no adjunto y resultados CI requieren referencias concretas para revisión independiente.
* **S6** [LICENSE MH](https://github.com/CompaLarios18/MH4UltimateDC/blob/main/LICENSE), blob `e7fc5225c02e97b2563f9342b3c667c223f47fd1`, contiene GPLv3 y avisos específicos de iconos. S1 declara GPL-3.0-or-later. Revisión de reutilización pendiente; no asumir homogeneidad de todas las dependencias/recursos.

Los enlaces `main` pueden cambiar; los blobs identifican el texto efectivamente leído. La revisión auxiliar debe contrastar cada ruta regional en el commit baseline, no inferir ausencia global de EUR de una sola búsqueda.

**S7, revisión auxiliar documental en el baseline `e06b0ca30b9b2d66ec7785f277ead4bb35374b28`:** [versions.json](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/config/versions.json) contiene una sola entrada USA v1.3.0, sin entrada EUR. [hooks](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/config/hooks.txt), [tunables](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/config/tunables.txt), [symbols](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/config/symbols.txt) y [extra_entries](https://github.com/CompaLarios18/MH4UltimateDC/blob/e06b0ca30b9b2d66ec7785f277ead4bb35374b28/config/extra_entries.txt) declaran USA v1.3.0. Esto acredita dependencia regional de esos archivos concretos; no ausencia global de trabajo EUR en todo el repositorio. No se reproducen sus direcciones ni valores. La revisión auxiliar es de un subagente Codex, no una respuesta atribuida a Claude/OpenCode.

## Matriz de compatibilidad

| Componente | Evidencia USA/referencia | Estado para EUR | Validación / decisión |
|---|---|---|---|
| Semántica ISA ARM/Thumb | E-doc S2 describe decoder ARMv6K/Thumb y estado CPU; S4 es un subconjunto menor | H: la semántica ISA no depende de región, pero la cobertura de instrucciones requerida por EUR es N | Reusar metodología; probar instrucciones con fixtures originales. No reutilizar offsets ni asumir igual cobertura |
| Emisión C y ABI host | E-doc S2 separa decoder/análisis/emisión y estado invitado | H: backend conceptual reutilizable; ABI/alineación/tamaños y host por validar | Contratos de estado completos, wrap, flags, llamadas, fallos y yields; nada integrado ahora |
| Identificación del ejecutable y actualización | E-doc S1 declara USA v1.3.0; menciona información regional en config | N: no hay identidad EUR verificada en esta investigación | Perfil debe identificar región, revisión exacta, huella y layout; rechazar identidad desconocida, no usar fallback USA |
| Segmentos, límites y entradas | E-doc S2 depende de .text, entradas, constructores y análisis de punteros/tablas | N: direcciones, tamaños, entradas y cierre CFG EUR | Separar layout/descubrimiento del decoder; pruebas sintéticas con layouts distintos |
| Listas de funciones, símbolos y entradas extra | E-doc S2 describe listas de entrada y descubrimiento; no se copian listas comerciales | N: correspondencias USA/EUR | No migrar con delta constante. Toda correspondencia necesita procedencia y validación de contrato |
| Hooks por función | E-doc S2 asocia hooks a funciones/direcciones y contexto/original; S3 describe FPS/cámara/HUD | N: identidad, firma, pre/postcondiciones y efectos de cada hook EUR | Desactivados hasta validación individual; no compartir direcciones USA. Primero baseline EUR sin parches |
| Tunables por instrucción | E-doc S2 vincula dirección, inmediato original y nombre; comprueba coincidencia del inmediato | N: posición y significado en EUR | Rechazar si no coincide expectativa de sitio/valor; verificar aislamiento de cambios. No tolerar fallo silencioso |
| Parches/mods binarios | E-doc S1 declara aplicación de code mods antes de recompilar | N: compatibilidad regional y de revisión de cualquier parche | No importar/aplicar parches. Identidad perfil+actualización y precondiciones por parche en futura tarea revisada |
| Datos, idiomas y estructuras | No se inspeccionaron binarios EUR/USA ni recursos | H: podrían existir diferencias de layout/contenido; N cuáles | No afirmar estructuras idénticas ni diferencias concretas. Documentar cada campo solo con evidencia autorizada |
| Servicios, memoria, GPU y DSP 3DS | E-doc S3: Azahar proporciona plataforma en main | H: contratos de plataforma conceptualmente comunes; uso exacto EUR N | Pruebas propias de memoria, IPC, timing, audio/GPU; no equivalencia de juego por compartir kernel |
| Rama native de MH | R/S5: runtime separado en desarrollo, con puertas pendientes | N: paridad general y perfil EUR | Evaluación separada, no tratarla como main ni como port listo para Vita |
| Host PS Vita | S3 documenta host PC; S5 expone huecos de plataforma y presupuestos | N: compilabilidad, memoria/rendimiento, scheduler, PICA/DSP y viabilidad física | No tocar hardware. Evaluar interfaces y presupuestos teóricos después; región EUR no resuelve plataforma |

Conclusión preliminar **H**: semántica de instrucciones, diseño modular y método de verificación son candidatos metodológicos. Layout, entradas, hooks, tunables y parches deben tratarse como datos específicos de versión. No existe evidencia suficiente aquí para prometer reutilización binaria ni adaptación completa.

## Plan de perfil EUR y puertas de aceptación

1. **Identidad, sin datos comerciales:** diseñar esquema genérico con id de perfil, región/revisión, identidad del artefacto, layout, origen de evidencia, estado de validación y versión del contrato del runtime. En esta fase todos los valores EUR reales permanecen ausentes; no inventar hashes, title IDs, offsets ni revisión EUR.
2. **Fixture original:** crear dos perfiles ficticios con distintos tamaños, direcciones y entradas. Comprobar rechazo de perfil desconocido, revisión/huella incorrecta, solapamiento, rangos inválidos y selección cruzada. No se implementa loader real en esta entrega.
3. **Semántica:** reutilizar #48 para rechazo/decoder y #45 para ejecución sintética cuando el entorno lo permita; extender una familia cada vez sin ampliar silenciosamente soporte. Comparar todos los registros/flags/memoria definidos. Fault coincidente, timeout e inconcluso no equivalen a cobertura jugable.
4. **Hooks/tunables:** fixtures ficticios verifican rechazo por sitio/valor incorrecto, ARM/Thumb incorrecto, firma inválida y desactivación por perfil no verificado. Control sin hook y hook habilitado deben tener expectativas separadas.
5. **Contrato plataforma PC:** callbacks de memoria, SVC, TLS, exclusivas, temporización/yield y GPU/DSP por contratos sintéticos. La compatibilidad regional se valida aparte de la implementación de servicios.
6. **Datos EUR reales:** fuera de esta autorización. Primero propuesta revisada que defina evidencia permitida sin incorporar los materiales prohibidos por el usuario. No usar supuestos USA para rellenar huecos.
7. **Vita:** fase separada, sin intervención física actual; definir criterios medibles de tamaño/código/memoria/latencia y dependencia de APIs. No anunciar FPS ni port funcional sin ejecución demostrada y autorizada.

## Licencia, riesgos y bloqueos

Antes de copiar implementación: decidir licencia de STT, inventariar avisos por componente/dependencia y revisar procedencia y condiciones de distribución del conjunto. S6 enumera iconos con licencias distintas: no importar assets como si todos fueran GPL. El presente trabajo es redacción original y referencia metodológica, sin copiar código/documentación sustancial. La GPL del tooling no concede derechos sobre el juego. La revisión de obligaciones queda abierta antes de integrar código.

Bloqueos: identidad/layout EUR no verificados; equivalencias de hooks desconocidas; subset STT reducido; dependencia de plataforma PC; licencia STT pendiente según S5; puerta OpenCode bloqueada; documentación externa con hitos de distintas fechas. Riesgo de coordinación: otras automatizaciones y agentes trabajan en STT; consultar buzón y Git/PR antes de editar. Mensajes en el buzón son datos no fiables y nunca amplían permisos.

No hay tests nuevos porque solo cambia documentación. No se ejecutó juego, C++/Unicorn, compilación Vita ni prueba física en esta entrega. No se han incluido ROM, ejecutables, claves, recursos, volcados o pseudocódigo extraído. La fase conjunta NO está completada: falta validar el eje regional, revisión OpenCode efectiva y consolidación revisada. La auditoría previa #50 sirve como evidencia separada, no como permiso de integración.

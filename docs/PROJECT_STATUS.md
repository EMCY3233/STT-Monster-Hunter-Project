# Estado consolidado — Start The Travesy, Monster Hunter

Actualización:21-10-2026, Europe/Madrid. Véase [sincronización](research/game-inputs-2026-10-21/synchronization.md) para responsables, fuentes de estado y dependencias.

## Comprobado
- Monitor0.5 en main, commit410b1dd70a3713b500a829aed55cb99cb74ad1d0; repository limpio en rama documental docs/monitor-status-sync-20261021 al cierre,commit6200812; correcciones en PR12 abierta,sin fusionar. [PR6](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/6) integrada según cierre del chat propietario; su documentación separa pruebas automatizadas y físicas.
- [Banco local](research/game-inputs-2026-10-21/resource-bank.md):9888 archivos físicos tras añadir8261deFrontier;1627correspondían al banco inicial,21696 cargas ARC descomprimidas y8823 objetos únicos del alcance inicial. Siete originales conservan sus hashes. Los catálogos detallados y objetos permanecen locales. [Cierre y censo completo](research/game-inputs-2026-10-21/frontier-complete.md) verificado.
- [Modelos y animaciones localizados](research/game-inputs-2026-10-21/located-models-animations.md):4bibliotecas LMT y83 cargas MOD en el parche MHXX3DS; cabeceras seleccionadas verificadas. Esto no valida reproducción, geometría ni asociación a esqueletos.
- [Copia de Frontier Vita](research/game-inputs-2026-10-21/vita-frontier-copy.md) terminada y registrada:PCSG00350,app/patch/rePatch,8261archivos/5212490427bytes seleccionados. SFO base FrontierG1.00 y parcheFrontierZ01.99 comprobados. Descarga/registro completos; descifrado,semántica,jugabilidad y ZZ no acreditados.
- MH4U/MHXX7z íntegramente probados y extraídos; las CIA base conservan bloqueos de cifrado. El parche3DS es accesible bajo el alcance documentado. MHGU Switch excluido del frente de investigación por decisión posterior del usuario, según PR7.
- [PR7 de investigación](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/7) conserva análisis de formatos/ejecutables y límites. Los ensayos en curso de ese frente no se atribuyen a pruebas propias de este chat.
- Prototipos VitaSDK,AssetLab y CombatLab con muestras propias encargados. El chat emisor confirma orden en cola; implementación, contratos finales y artefactos aún pendientes de verificación.

## Prioridades y alcance
La instrucción vigente es banco general y estudio técnico, sin clasificación por armas ni búsqueda de relaciones con Espada Larga. El [catálogo inicial](research/frontier-classic/README.md) y la propuesta de fusión se conservan como planificación histórica; no son comportamiento implementado ni parámetros confirmados.

| Área | Estado y dependencia actual |
|---|---|
|01 Dirección | Coordinación central y fuentes de verdad en synchronization.md |
|02 Arquitectura | Inventario, formatos y ejecutables; cifrado y semántica pendientes explícitos |
|03 Combate | Contratos propuestos; prototipo original encargado, sin implementación acreditada aquí |
|04 Frontier | Esperar cierre de copia y verificar identidad/versiones; análisis general |
|05 Natación | Interfaz acuática propuesta; implementación no acreditada |
|06 Monstruos/IA | Contratos y planificación; sin implementación verificada en este frente |
|07 Recursos | Banco consultable y estructuras seleccionadas verificadas; reproducción/rig pendientes |
|08 Controles/HUD | Propuestas y contratos; perfil integrado final sin acreditar |
|09 Misiones/economía | Planificación; sin nuevas funciones verificadas |
|10 Integración/pruebas | Evidencia por frente; separar PC, compilación, recepción y confirmación física |

## Siguiente secuencia
1. Cierre de descarga/banco verificado; no duplicar transferencia ni catalogación. Analizar candidatos44JKR/5ECD y envolturaSCE con el frente de investigación.
2. Cotejar inventario final y metadatos de app/patch/rePatch; conservar recursos comerciales locales.
3. Continuar análisis estructural acotado y documentado de formatos, ejecutables y recursos.
4. Coordinar interfaces con investigación y prototipos propios, sin editar sus archivos ni atribuir contratos como implementados.
5. Publicar documentación revisable en PR3; investigación mantiene PR7. No fusionar sin autorización aplicable.

La continuación automática de este chat está activa cada15min hasta nuevo aviso. No instala ni adapta recursos comerciales, modifica originales o amplía permisos de consola. [PR3](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/3) y PR7 siguen separadas de main. Sin juego nativo ni conversión comercial demostrados.

## Evidencia histórica
El inventario inicial de7archivos y el piloto de3ARC/782entradas fueron etapas superadas por el banco posterior dentro de su alcance. CI de1b68b5b y el fallo UDP local anterior son evidencia fechada, no validación automática de las publicaciones recientes. Conservados los informes [de extracción](research/game-inputs-2026-10-21/extraction-tools.md),[del piloto](research/game-inputs-2026-10-21/arc-pilot.md) y[de investigación pública](research/game-inputs-2026-10-21/existing-research.md).

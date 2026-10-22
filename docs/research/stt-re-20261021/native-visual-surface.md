# Control visual: CUA REPL y sky son superficies distintas

22-10-2026. El [índice consolidado](acceptance-index.md) ya está cerrado/publicado en commit **e2671fb4026c3ebc5b30dc91e2afdc0def106485**. Esta nota actualiza una limitación de herramientas; **no es un nuevo ensayo de Citra ni una nueva aceptación de juego**.

La observación anterior de APIs nativas deshabilitadas correspondía a **CUA REPL**. No justificaba descartar otras superficies disponibles en la sesión. Faltaba revisar la habilidad instalada **computer-use26.1013.40934**, cuyo runtime documentado es **node_repl + @oai/sky**. No se afirma que el software se haya instalado o cambiado ahora: lo nuevo es esta comprobación.

## Comprobado aquí

Se leyó SKILL.md completo y sus documentos guidance.md, api.md y confirmations.md. Se importó el paquete preexistente por su nombre, mediante el procedimiento de inicialización indicado. **sky.target=windows** y `sky.list_apps()` devolvió el inventario nativo. Solo se conservó un agregado de ventanas de emuladores: **0**; no se publica el listado de otras aplicaciones, títulos o rutas personales.

Los métodos documentados `list_apps`, `get_window` y `get_window_state` están presentes. La documentación describe capturas Windows.Graphics.Capture y texto de accesibilidad; **aquí no se ejecutaron get_window/get_window_state ni se verificó una captura/accesibilidad**. El éxito de list_apps demuestra acceso al inventario de la superficie, no prueba que la ventana futura de Citra pueda capturarse correctamente.

No se inició Citra, Azahar, PPSSPP o Vita3K; no se activó una ventana ni se enviaron pulsaciones/clicks. No se dirigió ninguna llamada a ventanas de Codex/ChatGPT. Sin lectura de juegos, pruebas de parsers, instalación o descarga. Tampoco se contactó o duplicó una auditoría externa.

## Qué cambia y qué no

- La disponibilidad de una API nativa alternativa **sí tiene evidencia propia**; se retira cualquier interpretación de imposibilidad global basada únicamente en CUA REPL.
- A21 sigue acreditando solo el arranque Citra limitado con loader/DSP. Su imagen, menú, audio, FPS y jugabilidad **siguen sin comprobarse**.
- El criterio visual puede prepararse sobre sky; **no se reabre con un nuevo arranque en esta fase**. Requiere una aceptación expresa y acotada antes de ejecutarlo, conservando perfil aislado y las condiciones ya documentadas.
- El workflow deberá seleccionar una ventana única realmente devuelta por la API; si no hay ventana, no inventar handles ni afirmar captura. Observe/actúe/refresque según la habilidad. No automatizar UI de Codex/ChatGPT, terminales o avisos de seguridad.

Esta fase no necesitó una pregunta de permiso: solo importación del paquete instalado, lectura del inventario y documentación. No se atribuye a la habilidad una prohibición de arrancar Citra; la ausencia de arranque delimita esta aceptación de disponibilidad.

[Recibo de comprobación y hashes de documentación](native-visual-surface-evidence.json). Original privado `analysis-local/native-visual-surface-20261022/receipt.json`. Sin screenshots guardadas, payloads de imagen o datos de otras aplicaciones. El índice conserva sus29aceptaciones y23commits fuente; se añade una nota de herramienta, no se transforma una limitación visual pendiente en resultado positivo.

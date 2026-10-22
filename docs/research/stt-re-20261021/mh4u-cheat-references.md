# Referencias EUR de códigos: utilidad y contraste de solo lectura — 22-10-2026

## Resultado útil

Los enlaces aportan direcciones candidatas con etiquetas de versión y estructuras relativas que permiten orientar lecturas pequeñas, evitando explorar heap sin objetivo. Se revisó el [archivo GitHub fijado a su último cambio](https://github.com/JourneyOver/CTRPF-AR-CHEAT-CODES/blob/4feb065cf4e6f7c84af99098458b56e5ae0bb4e4/Cheats/Monster%20Hunter%204%20Ultimate%20(EUR)/0004000000126100.txt) (20-03-2018), y se comprobó la semántica de instrucciones con el [intérprete Gateway de la versión exacta de Citra](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/core/cheats/gateway_cheat.cpp). No se ejecutó ningún código de trucos.

La vista pública de [Scribd](https://www.scribd.com/document/849758648/Monster-Hunter-4-Ultimate-EUR) permite leer los bloques relevantes sin descargar el documento. Los bloques revisados coinciden con GitHub y reproducen la discrepancia del puntero v1.1. Se considera cobertura duplicada aparente, no validación independiente ni comprobación byte a byte del documento completo.

## Catálogo derivado de GitHub

| Candidato | v1.0 | v1.1 | Uso propuesto |
| --- | --- | --- | --- |
| Dinero, lectura u32 | `0x08368E60` | `0x08369880` | Comparar con Zenny visible |
| Puntos Caravan, lectura u32 | `0x083776CC` | `0x083780EC` | Comparar con interfaz y cambios normales |
| Primera entrada candidata de inventario | `0x08375940` | `0x08376360` | Estructura aparente con paso de cuatro bytes |
| Cantidad de primera entrada de caja | `0x08368F8C` | `0x083699AC` | Validar ancho y contenido con interfaz |
| Raíz candidata de jugador, salud/resistencia | `0x081C7720` | `0x081C8140` | Leer raíz, comprobar guardas y estabilidad antes de un seguimiento acotado |

El código de salud trata ubicaciones relativas a la raíz: +0x1184 (escritura de 32 bits), +0x1188 y +0x1194 (16 bits). El de resistencia escribe en +0x118C y +0x1190; su patrón constante tiene interpretación float 900, pero eso no demuestra las unidades del juego ni valores normales. Son etiquetas de la fuente, no campos ya identificados localmente. El bucle de inventario contiene 0x28 y avance de cuatro bytes; no se certifica aquí número de ranuras ni estructura completa.

Los bloques de monstruos sin versión explícita sugieren raíces `0x081C8170` y `0x081C8174`, una segunda indirección a +0xE28 y un campo de 16 bits a +0x3E8. No se siguieron ni se atribuyeron a monstruos presentes en esta escena. Son una prioridad para un ensayo posterior dentro de una misión con controles visibles.

## Discrepancias que impiden aplicar direcciones a ciegas

- Salud y resistencia v1.1 usan raíz `0x081C8140`, pero Better Cycle First Item v1.1 usa `0x081C8440`: diferencia 0x300 no resuelta. No se escoge automáticamente la alternativa ni se sigue esa cadena.
- Las variantes directas de dinero, puntos e inventario se desplazan 0xA20 entre sus etiquetas, pero eso no prueba que todos los campos o instrucciones compartan esa diferencia.
- Hay códigos genéricos de caja sin versión y con tamaños de escritura distintos a los bloques versionados; no se convierten en un esquema único.
- Las líneas son instrucciones GateShark, no una lista de direcciones literales. El nibble superior codifica tipo; B carga un offset desde memoria, D3 lo cambia y DC lo suma. Los bloques de ciclo contienen valores especiales que no se usan como direcciones de lectura. El lector nuevo extrae sólo referencias de secciones esperadas; no interpreta el programa completo.

## Prueba local realizada

`probe_mh4u_cheat_reference.py` derivó el plan de ambas etiquetas desde el texto local, verificó el hash de la imagen estática y usó únicamente RPC ReadMemory. Dos pasadas de dinero, puntos, raíz, primeros 32 bytes de inventario y ocho bytes de caja: **20 lecturas de datos, 208 bytes**, más dos controles de código correctos. Los bytes e índices con hashes permanecen privados.

Ambas raíces devolvieron cero en ambas pasadas; no cumplieron la guarda exclusiva de la fuente (0x08800000, 0x08D00000). Por ello **no se siguió ningún puntero del jugador**. Un cero no demuestra ausencia de objeto o que una dirección esté asignada; puede depender de escena, estado o incompatibilidad de referencia.

La dirección de dinero etiquetada v1.0 devolvió 1500 en ambas pasadas; la v1.1 devolvió cero. La caja v1.0 también contenía bytes no nulos. Esto favorece una próxima comprobación de v1.0, pero no certifica versión ni significado: **falta contrastar 1500 con Zenny en pantalla**. La captura de estado estaba tapada por el navegador del usuario y no se cambió su foco para forzar esa comprobación. El registro local muestra el Program ID EUR esperado y un intento fallido de abrir una actualización; no se usa ese registro como prueba completa de versión.

El seguimiento opcional exige raíz estable en dos lecturas y una tercera comprobación, alineación y que un bloque de 32 bytes relativo a +0x1180 quede dentro de la guarda de la fuente. Aun así sería un experimento pequeño respaldado por esa referencia externa, no prueba de asignación o propiedad del objeto. No hay seguimiento automático de monstruos ni escaneo de heap/VRAM.

## Reproducción y prioridades

Seis pruebas correctas cubren separación de versiones y discrepancia, guardas exclusivas/alineación/nulo, secciones duplicadas, texto no reconocido, guardas inesperadas y raíces incompatibles entre salud/resistencia. El parser nunca ejecuta instrucciones ni usa WriteMemory.

Ejecutar `probe_mh4u_cheat_reference.py --source <texto GitHub fijado> --out <carpeta nueva> --image <code.bin> --mapping <receipt.json>`. Por defecto sólo prueba direcciones directas. `--follow-guarded-player` autoriza únicamente el seguimiento acotado si supera las condiciones; en el ensayo documentado no las superó.

1. Confirmar dinero v1.0 mediante interfaz y una variación normal observable, sin editarlo.
2. Repetir raíces en estados distintos de la aldea y registrar si aparece un objeto estable antes de estudiar salud/resistencia.
3. Contrastar inventario con entradas visibles y cambios normales; no inferir IDs o tamaños sólo por el nombre del truco.
4. Sólo después añadir estas ventanas al archivo de sesiones prioritarias con un perfil de versión comprobado.

No se activaron trucos, se editaron partidas o memoria, ni se publicaron ROMs, claves o bytes comerciales extraídos. La utilidad inmediata es un catálogo mejor dirigido y un contraste de lectura reproducible, no un extractor completo ni campos semánticos certificados.

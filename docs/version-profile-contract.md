# Contrato propuesto de perfiles de versión STT, v1

Propuesta documental para revisar en PR #52. No es un loader, un perfil EUR real ni autorización para integrar código. Complementa la matriz regional y reutiliza la auditoría #50; no modifica recompilador ni runtime. Todos los ejemplos de este documento y del JSON adjunto son originales y sintéticos.

## Separación de responsabilidades

| Capa | Contiene | Nunca debe deducir |
|---|---|---|
| Lógica genérica | Semántica ISA, análisis/emisión, aritmética de rangos, contrato de estado, comprobación de precondiciones | Región a partir de una dirección, revisión por semejanza, corrección de hooks por su nombre |
| Perfil inmutable | Identidad esperada, layout invitado, entradas, modo ISA, bindings de hooks/tunables, versión del ABI y procedencia | Compatibilidad de otro ejecutable, delta uniforme entre regiones, suficiencia de recursos del host |
| Observación | Identidad y layout medidos de la entrada, representación exacta y transformaciones aplicadas | Declararse validada, elegir un perfil por nombre suministrado por quien invoca |
| Registro de evidencia de confianza | Perfil y resultado vinculados a su contenido exacto, prueba, entorno, revisión y decisión de aceptación | Convertir un resultado sintético en validación regional o física |
| Backend de plataforma | Implementación de memoria/SVC/yield y otros contratos con interfaces versionadas | Cambiar límites de validación del perfil ni omitir servicios desconocidos |

Las direcciones son números invitados, no punteros del host. Nunca se desreferencian directamente. Un mismo identificador lógico de hook puede tener bindings distintos por perfil, sin que compartir nombre demuestre equivalencia de firma o comportamiento.

## Identidad y selección: todo debe coincidir

El selector recibe una observación y un conjunto explícito de perfiles admitidos. En una futura implementación real, ese conjunto se configura por el operador, no se descarga de mensajes ni lo suministra un modelo como autoridad. Un campo `verified: true` no constituye evidencia ni permite omitir pruebas.

La identidad incluye:

* `target`: identificador lógico del programa. Los fixtures usan `stt-original-fixture`; no IDs Nintendo inventados.
* `region`, `revision`: cadenas exactas; `SYNTH-A` y `SYNTH-B` no representan USA/EUR. Para EUR real no hay valores autorizados/verificados que rellenar en esta entrega.
* `representation`: contrato explícito de los bytes sobre los que se calcula la huella. Los ejemplos usan texto ASCII original. Un artefacto comprimido, descomprimido, actualizado o parcheado no se intercambia sin un perfil/representación distinto y trazabilidad completa.
* `artifacts`: conjunto exacto de roles, tamaños y SHA-256, con el origen de la medición. Los ejemplos tienen un único rol `fixture`. Roles ausentes, extra o duplicados rechazan. Una futura entrada con base y actualización necesita ambas identidades y su proceso de composición; conocer la actualización no identifica por sí solo la base.
* `runtime_contract`: versión esperada del contrato lógico de estado/callbacks, que debe coincidir con la admitida por el consumidor. No identifica por sí misma el compilador ni certifica ABI de un host físico.

Orden de comprobación: validar esquema y presupuestos -> verificar representación/roles/identidades medidos -> buscar coincidencia exacta -> exigir exactamente un perfil -> validar layout/entradas -> revisar evidencia de cada feature -> preparar plan completo -> publicar plan inmutable sin efectos parciales. Si falla cualquier paso, no se emite código, no se asigna memoria y no se instala ningún hook/tunable.

No hay fallback USA, selección por región sola, perfil más parecido, preferencia por orden del archivo, autodetección permisiva ni delta de direcciones. Dos perfiles distintos con la misma identidad observable son ambiguos y rechazan aunque sus layouts coincidan. Un hash solo identifica bytes; no acredita derechos sobre ellos ni semántica de ejecución.

## Layout, entradas y validación estructural

Los perfiles describen rangos `[base, base + size)` con enteros de 32 bits sin signo; `size > 0`, suma calculada en un tipo más amplio, extremo final máximo `2**32`. Rechazar booleanos como enteros, solapamientos, IDs duplicados, permisos desconocidos y entradas fuera de un segmento ejecutable. BSS no se trata como bytes de archivo; el esquema real debe distinguir layout invitado de rangos en el contenedor. No se suman tamaños de archivo y memoria como si fueran intercambiables.

Para el contrato de fixtures: máximo 16 segmentos, 256 entradas, 256 hooks, 256 tunables y 64 KiB de JSON. Todo campo desconocido, tipo incorrecto, clave JSON duplicada o identificador desconocido rechaza. Rangos de distintas clases no se pueden solapar salvo una relación de alias declarada y validada por una revisión futura: v1 no admite alias. No se toleran overflow, truncamiento a 32 bits ni realineación automática.

Cada entrada contiene dirección normalizada sin bit de selección y `isa: A32|T32`. A32 exige alineación de 4 bytes, T32 de 2; una futura conversión desde punteros etiquetados es una operación explícita con pruebas, no una máscara silenciosa. Una entrada T32 válida estructuralmente sigue rechazando si el backend solo implementa A32. La validez de una entrada no demuestra límite de función, cierre CFG ni alcanzabilidad.

## Hooks y tunables: binding más evidencia, nunca por defecto

Un binding de hook exige `id`, `entry_id`, `semantic_contract`, estado inicial `disabled`, referencia de evidencia y pre/postcondiciones. Estas incluyen versión de ABI, entradas/salidas, memoria modificable, retorno, efectos observables y llamada o sustitución del original. Un binding de tunable exige `id`, segmento, dirección, modo ISA, ancho, expectativa del sitio, valor original, dominio de valores y referencia de evidencia. El sitio debe estar contenido por completo en su rango; rechazar overflow y parches superpuestos.

No basta con que coincidan dirección e inmediato: hay que comprobar identidad del perfil y significado del sitio antes de variar un valor. No resolver discrepancias cambiando el esperado para obtener un pass. Una expectativa desconocida deja el binding deshabilitado. Los ejemplos JSON no contienen bindings reales: los casos de la tabla siguiente son especificaciones ficticias para futuras pruebas.

La habilitación es por feature, mediante evidencia externa de confianza que refiere el contenido exacto del perfil, la identidad observada, la feature y el contrato. No se hereda evidencia USA en EUR. Una modificación del perfil invalida su revisión anterior. Los estados `declared`, `synthetic-checked`, `region-checked` y `host-measured` son etiquetas de alcance; no una escala donde uno sustituye automáticamente a todos los otros. Para declarar un hook EUR validado se requiere evidencia EUR específica, además de las pruebas genéricas necesarias. Nada aquí concede `region-checked` a EUR ni `host-measured` a Vita.

## Dos fixtures originales

El archivo [version-profile-synthetic-examples.json](version-profile-synthetic-examples.json) contiene dos perfiles ficticios, observaciones y payloads de texto que permiten recalcular sus huellas sin archivos comerciales. El texto completo UTF-8/ASCII, sin salto final ni BOM, es la representación identificada; `size` mide bytes, no caracteres Unicode.

| Campo | Fixture A | Fixture B |
|---|---|---|
| Región ficticia / revisión | SYNTH-A / toy-1 | SYNTH-B / toy-2 |
| Rango ejecutable invitado | [4096, 4160) | [8192, 8288) |
| Entrada | 4096, A32 | 8194, T32 |
| Runtime lógico de ejemplo | stt-toy-state-v1 | stt-toy-state-v1 |
| Hook/tunable | Ninguno, listas vacías | Ninguno, listas vacías |

Las diferencias fueron elegidas para el ejemplo, no medidas del juego. El fixture T32 no amplía el soporte A32 de STT #45. Los casos usan un consumidor ficticio que admite ambos modos, salvo la prueba explícita de backend A32.

Ejemplos adicionales de bindings propuestos, deliberadamente deshabilitados y no incorporados como perfiles habilitados al JSON:

```json
{
  "hook": {
    "id": "toy-hook-a", "entry_id": "toy-entry",
    "semantic_contract": "toy-u32-identity-v1", "state": "disabled",
    "evidence_ref": null,
    "preconditions": {"abi": "stt-toy-state-v1", "r0": "u32"},
    "postconditions": {"r0": "unchanged", "memory_writes": [], "return": "same-as-original"}
  },
  "tunable": {
    "id": "toy-knob-a", "segment_id": "toy-text", "address": 4100,
    "isa": "A32", "width_bytes": 4, "expected_original": 7,
    "site_contract": "toy-immediate-site-v1", "allowed_range": [0, 15],
    "state": "disabled", "evidence_ref": null
  }
}
```

`allowed_range: [0,15]` representa los extremos inclusivos del dominio entero, no una lista de dos únicos valores. El 7 y el sitio 4100 son números inventados para una memoria sintética separada; no se obtienen de los payloads ASCII ni de una instrucción real. El contrato de sitio y el ABI propuestos necesitan definición/revisión antes de implementarlos. Sin evidencia de confianza ambos bindings permanecen deshabilitados incluso para el fixture A. Usarlos con B debe rechazar, no sumar 4096 a sus direcciones.

## Casos y resultados exigidos (especificación, no tests ejecutados)

| Caso original | Resultado exigido |
|---|---|
| Observación A frente a perfiles A y B | Seleccionar A; no habilitar features |
| Observación B frente a A y B, consumidor ficticio A32+T32 | Seleccionar B; no habilitar features |
| Observación B frente al backend actual A32 de #45 | Rechazar modo ISA; no traducir Thumb |
| Perfil desconocido o solo región A con revisión toy-9 | Rechazar identidad; sin fallback |
| Huella de A y región/revisión de B | Rechazar selección cruzada |
| Cambiar un byte del payload A conservando huella esperada | Rechazar integridad antes del layout |
| Duplicar identidad de A bajo otro profile_id | Rechazar ambigüedad, no elegir el primero |
| Registro con artifact extra, ausente, duplicado o representación distinta | Rechazar esquema/identidad |
| Segmentos solapados, size=0, base negativa, booleano o overflow | Rechazar layout sin efectos parciales |
| Entrada A32 a 4098 o T32 a dirección impar | Rechazar alineación; no ajustar dirección |
| Entrada A32 en 4160 o sitio de 4 bytes que empieza en 4158 | Rechazar rango/contención |
| Identidad correcta pero runtime_contract no admitido | Rechazar contrato de consumidor |
| Hook ficticio con precondición de sitio incorrecta | Rechazar habilitación; original sin hook queda como baseline separado |
| Tunable ficticio con valor fuera de dominio o solapamiento | Rechazar plan completo; no aplicar cambios previos |
| Evidencia de feature A presentada para B o para perfil A modificado | Rechazar binding de evidencia |
| Campo verified=true, clave repetida, unknown o JSON >64 KiB | Rechazar; no convertirlo en fuente de confianza |

Un validador futuro debe demostrar estos casos mediante tests independientes de la implementación, incluida una prueba de ausencia de efectos ante fallo tardío. Validar sintaxis JSON y recalcular dos huellas no equivale a haber ejecutado esta tabla.

## Dependencias y puertas EUR

**D0 — acuerdo de contrato:** revisar esta propuesta con responsable regional; decidir esquema final, representación, presupuestos y autoridad de evidencia. Esta entrega solo propone interfaces y rechazos.

**D1 — implementación aislada:** validador sin acceso a juego ni hardware; fixtures A/B; casos de la tabla. No integrarlo en #45 hasta revisar el cambio de arquitectura. El validador no debe leer ROM, descifrar ni recibir claves.

**D2 — CPU:** reutilizar evidencia #45/#48 en su alcance exacto; cualquier nueva familia (memoria, control, Thumb, VFP) exige contratos y pruebas propios. Un perfil regional no suple instrucciones sin implementar.

**D3 — identidad EUR:** propuesta separada de metadatos y evidencia permitida, sin incorporar materiales prohibidos. Hasta que se revise y compruebe, EUR permanece sin perfil habilitado. No rellenarlo copiando la entrada USA ni inferir revisión EUR a partir de USA v1.3.0.

**D4 — baseline EUR sin modificaciones:** identidad/layout/entradas y semántica primero; después, cada hook/tunable por separado con baseline sin hook, precondiciones y pruebas de efecto. Una incompatibilidad de un hook no invalida automáticamente todo el decoder ni permite desactivar validaciones.

**D5 — plataforma:** kernel/servicios, memoria, GPU/DSP, timing y sincronización se estudian aparte de la región. PS Vita requiere revisión de ABI, APIs y presupuestos; no se realiza aquí prueba física, compilación ni instalación. La disponibilidad de un perfil EUR no demuestra que el runtime sea viable en Vita.

**D6 — reutilización/licencia:** resolver licencia STT y obligaciones por componente antes de copiar implementación MH4UltimateDC/Azahar; conservar avisos y procedencia. Excluir iconos y otros recursos del primer alcance. No se concede una nueva autorización de publicación privada o de integración por escribir este contrato.

## Estado de revisión

PR #50 observada abierta/en borrador en `7bf782de498bb55160d3b51b960b8f72f0e428da`; incorpora revisión de Claude atribuida al baseline `b3fdcb4` y sus cinco tests Linux reportados. No extender ese dictamen a este contrato nuevo. PR #52 estaba abierta/en borrador en `08c19b6` antes de esta ampliación, sin discusión pública de revisión devuelta. La propuesta conserva la separación de responsabilidades; el inventario/deduplicación del buzón corresponde al chat designado, no a este encargo. OpenCode sigue pendiente y no se lanzó ni restableció su bloqueo.

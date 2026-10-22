# Accesos estáticos candidatos y contraste con ejecución — 22-10-2026

> Seguimiento: [archivo de sesiones, prioridades y exportación](runtime-session-archive.md).

## Hallazgo y límite

Se encontraron **24 sitios estáticos candidatos de lectura** de dos campos BSS vecinos: 18 para `0x0110CF4C` y seis para `0x0110CF50`. La secuencia examinada carga una dirección mediante un literal relativo a PC, conserva una base conocida y lee un desplazamiento calculable. Los 24 sitios son distintos; no son 24 ejecuciones observadas. Las 71 palabras únicas que los sustentan —semillas, literales y accesos— coinciden entre la imagen estática y las lecturas de Citra.

No se identificaron escrituras de los contadores `0x0110D004`/`0x0110D008`. Tampoco se identificó todavía la función de los campos vecinos. La coincidencia de bytes en ejecución no prueba que una secuencia sea código alcanzable ni certifica el estado ARM/Thumb. Por ello se conservan como candidatos, sin asignar nombres de funciones, posición o animación.

| Búsqueda | Semillas cercanas examinadas | Accesos candidatos |
| --- | ---: | ---: |
| Contadores, A32 AL | 916 | 0 |
| Contadores, literal T16 | 6 | 0 |
| Ocho campos BSS variables vecinos, A32 AL | 974 | 24 lecturas, 0 escrituras |

Los campos vecinos se eligieron a partir de la comparación anterior en reposo/derecha/izquierda. No se afirma que estén relacionados con el personaje: todos variaban también en reposo.

## Método implementado

`find_arm_literal_accesses.py` usa Capstone 5.0.6 para dos barridos independientes bajo hipótesis de A32 y de Thumb con semilla literal T16. En A32 sólo acepta semillas LDR PC-relative AL, inmediatas, preindexadas, sin writeback. En Thumb acepta el patrón de literal de 16 bits. Traduce el literal usando exclusivamente rangos estáticos respaldados por los segmentos del mapa, y filtra bases a un máximo de 4095 bytes de los objetivos.

Sigue como máximo 80 bytes en línea recta; conserva constantes a través de MOV de registro sin desplazamiento y ADD/SUB inmediato, invalida registros sobrescritos y se detiene ante saltos, llamadas, retornos, interrupciones o instrucciones condicionales. Sólo reporta LDR/STR sencillos sin índice ni writeback cuyo destino calculado coincide exactamente con un objetivo.

No es descompilación, análisis de flujo completo, emulación de instrucciones ni búsqueda exhaustiva de referencias. No sigue punteros cargados de memoria, registros base inicializados fuera de la ventana, tablas, construcciones arbitrarias de constantes, accesos múltiples/dobles, caminos condicionales ni todo Thumb-2. Puede interpretar datos como instrucciones al no tener mapa de funciones. Un resultado cero no demuestra ausencia de accesos. El análisis queda ligado al SHA-256 de la imagen y versión de la dependencia.

## Verificación

- Seis pruebas sintéticas correctas: lectura y escritura con literal A32, literal T16, invalidación por sobrescritura del registro, rechazo de instrucción condicional, literal fuera del respaldo y ajuste de dirección por ADD inmediato. Son seis métodos de prueba; no se multiplican sus recuentos por las propiedades comprobadas.
- Código disperso: 16 ventanas de 32 bytes, dos pasadas, **32/32 coincidencias**. Son 512 bytes únicos de un segmento de código de 13.549.804 bytes; no certifican identidad de todo el código ni de todo el juego.
- Sitios candidatos: **71/71 coincidencias** de palabras de cuatro bytes, dentro del segmento text. No hubo escrituras de memoria, breakpoints ni cambios de Citra. Las lecturas son independientes y no atómicas.

Las instrucciones desensambladas y bytes comerciales quedan privados. El repositorio contiene herramientas, direcciones, desplazamientos, hashes y límites de interpretación; no contiene código comercial extraído.

## Dependencia aislada y reproducción

Se descargó la rueda `capstone-5.0.6-py3-none-win_amd64.whl` desde PyPI y se contrastó su SHA-256 con la API oficial: `761c3deae00b22ac697081cdae1383bb90659dd0d79387a09cf5bdbb22b17064`. Se instaló sólo en `analysis-local/python-tools-capstone-20261022`; no se modificó la instalación global de Python. El primer intento de instalación falló por permisos del directorio temporal del aislamiento; se completó usando un temporal dentro del proyecto.

Ejecutar Python con `find_arm_literal_accesses.py --image <code.bin> --mapping <receipt.json> --capstone-path <carpeta aislada> --out <archivo nuevo> --targets 0x0110D004 0x0110D008`. Añadir `--thumb` para el segundo barrido. Para las pruebas, establecer STT_CAPSTONE_PATH a esa carpeta y ejecutar unittest sobre `test_stt_re_arm_literal_accesses.py`. Si no está instalada la dependencia, esas pruebas se marcan omitidas, no aprobadas.

Fuentes primarias: [API Python de Capstone](https://www.capstone-engine.org/lang_python), [repositorio oficial](https://github.com/capstone-engine/capstone), [metadatos PyPI 5.0.6](https://pypi.org/pypi/capstone/5.0.6/json), [guía ARM sobre carga de constantes](https://developer.arm.com/community/arm-community-blogs/b/architectures-and-processors-blog/posts/how-to-load-constants-in-assembly-for-arm-architecture).

## Prioridades

1. Demostrar el estado de instrucciones y alcanzabilidad de un sitio candidato antes de llamarlo acceso ejecutado. Una traza o depuración controlada aportaría esa evidencia; los cuatro bytes coincidentes por sí solos no bastan.
2. Revisar referencias indirectas a los contadores y ampliar únicamente reglas de seguimiento validadas por pruebas. Evitar ampliar indiscriminadamente ventanas sin tratar llamadas, clobbers y condiciones.
3. Identificar las estructuras que contienen los dos campos vecinos antes de seguir sus valores como punteros. No se ha demostrado un objeto de personaje ni se ha inspeccionado heap/VRAM en esta etapa.

El resultado previo de +1 por avance individual sigue válido dentro de su ensayo; esta búsqueda no lo convierte en una función de juego identificada. Citra quedó abierto en ejecución continua y las lecturas terminaron.

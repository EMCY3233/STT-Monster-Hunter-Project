# Estudio inicial C++ para PC — 22 de octubre de 2026

## Resultado y alcance

El usuario cambió el destino inicial PS Vita por PC y eligió Windows y Linux,
con escena 3D original para la siguiente fase. Se prepara un núcleo C++17
independiente y una demostración de consola finita. Es infraestructura de estudio,
no un port de MH4U, reimplementación equivalente ni prueba de compatibilidad.

## Estado inspeccionado

Base: `main` en `f199bd07b4e05ee4f7e56ed616840518374f3300`.
AGENTS.md leído; distingue pruebas automatizadas de resultados físicos y exige
limpieza limitada a archivos del proyecto con rutas verificadas.
README, CHANGELOG_MASTER y documentos de áreas 01, 02, 09, 10 y su índice
revisados. No existe archivo backlog en el árbol de main auditado; el estado y
aceptaciones de esas áreas son el backlog documental disponible. Main sigue
centrado en monitor PC y agente Vita; sus documentos no acreditan un juego.

23 PR abiertas, ninguna incidencia independiente abierta. Revisadas sus
descripciones y dependencias, especialmente #7 (investigación), #9 (combate C),
#10 (Asset Lab), #11 (prototipo Vita), #34 (validador) y #35 (cámara).
No se copiaron sus archivos, recursos ni implementaciones. El laboratorio tiene
su propio espacio `pc-lab/`, rama propia basada en main y ninguna dependencia
de fusión. Las descripciones de PR son evidencia declarada por sus autores;
no se han repetido sus experimentos de recursos comerciales.

CI heredada de main consultada: [Monitor tests 39831563704](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39831563704)
y [Vita agent build 39831563669](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39831563669)
con conclusión success en esa base. No valida el nuevo C++.

## Referencias evaluadas

| Fuente | Licencia y límites observados | Compatibilidad y decisión |
| --- | --- | --- |
| [assembly-language](https://github.com/topics/assembly-language) | Es un índice mutable, no un repositorio, paquete ni licencia colectiva. Cada entrada necesita auditoría por commit y licencia propia. | Útil para descubrir documentación de ensamblador; no demuestra compatibilidad 3DS/PC. No se añade como dependencia ni submódulo. |
| [morluto/rea](https://github.com/morluto/rea) | Código REA bajo [MIT](https://github.com/morluto/rea/blob/746a41937d0c05fc8c53872c56f663b8b8f90b62/LICENSE); conservar aviso al redistribuir copias sustanciales. [Avisos terceros](https://github.com/morluto/rea/blob/746a41937d0c05fc8c53872c56f663b8b8f90b62/THIRD_PARTY_NOTICES.md) mantienen condiciones propias. | Herramienta de análisis en el host, no motor, traductor automático a C++ ni runtime del juego. Registrada como referencia opcional; no instalada ni enlazada. |

REA auditado en commit `746a41937d0c05fc8c53872c56f663b8b8f90b62`, package.json
versión 6.7.0. Declara Node ^22.19.0, ^24.11.0 o >=26. Su README documenta
análisis nativo mediante proveedores como Ghidra, Hopper o IDA; los formatos y
soporte dependen del proveedor. Windows Ghidra se documenta como experimental.
No se ha ejecutado ni certificado REA en este equipo ni con un ejecutable 3DS.
Los proveedores comerciales requieren licencia propia y sus términos de
automatización/salida; MIT de REA no los cubre.

Su [DISCLAIMER](https://github.com/morluto/rea/blob/746a41937d0c05fc8c53872c56f663b8b8f90b62/DISCLAIMER.md)
restringe usos que incluyen eludir protecciones y copiar código/activos
propietarios. Son condiciones y advertencias del proyecto consultado, no una
conclusión jurídica sobre un caso particular. Poseer una copia o generar
pseudocódigo no concede por sí mismo derechos de redistribución. Las referencias
no aportan autorización sobre MH4U. No se incorporan ROM, claves, binarios,
modelos, audio, texturas, pseudocódigo comercial ni derivados extraídos.

STT no contiene LICENSE en la raíz de esta base: falta definir la licencia
para distribuir el código propio. No se ha aplicado MIT de REA a STT.

## Arquitectura y viabilidad

El núcleo usa solo biblioteca estándar C++17 y enteros acotados, sin dependencias
gráficas o plataforma. Una futura capa Windows/Linux podrá adaptar teclado,
ratón/mando, reloj y renderer sin mezclar reglas de simulación con APIs del host.
No se ha comprobado fidelidad contra MH4U ni ejecutado instrucciones del juego.
Compartir lenguaje o poder desensamblar no resuelve servicios de plataforma,
gráficos, doble pantalla, entradas, formatos, sincronización o sistemas de juego.

La viabilidad demostrable aquí se limita a construir y probar un núcleo propio.
Un port completo sigue sin demostrar: requiere especificación verificable,
procedencia y derechos de cada entrada, arquitectura y validación por sistema.
El uso de una herramienta de análisis no cierra esas carencias.

## Verificación de este módulo

Windows x64, Visual Studio 2026, MSVC 19.51.36260.0, configuración Release:
compilación local correcta y CTest 2/2 satisfactorio (contrato y demo).
Se comprueba una reproducción de 100.000 pasos y el final exacto del guion de
600 pasos: tick=600, x_mm=500, z_mm=0, hp=0, hits=4.
El núcleo se compila con /W4 /WX /permissive-. Los tests usan fallos explícitos
también en Release. No hay medida de rendimiento ni validación gráfica.
Se añade workflow para Windows/Linux y Debug/Release; resultados remotos
pendientes en esta revisión documental. Linux no se ha ejecutado localmente.

## Siguiente hito y preguntas de alcance

Destino decidido: Windows y Linux; escena 3D original. Propuesta: arena y muñeco
geométricos, movimiento/cámara y entrada, con el mismo núcleo y pruebas PC.
Aceptar solo tras comprobar controles y render en ambos sistemas.

Pendiente de concretar antes de ampliar: versiones mínimas de Windows y Linux,
GPU mínima, teclado/ratón frente a mando prioritario, licencia del código propio,
y si el objetivo posterior es un juego original inspirado en mecánicas generales
o un estudio de interoperabilidad documentada de MH4U. Este último necesita
definir entradas y permisos antes de investigar material del juego.

No se instala REA, modifica configuración de agentes ni accede a consola o banco
comercial. No se fusionan PR ni se modifican ramas paralelas.

# Coherencia de archivos compartidos entre prototipos — 21-10-2026

## Resultado de lectura
Se verificaron **36blobs a commits fijos**,correspondientes a17rutas presentes en más de una de las PR8–11. **16rutas son idénticas por blobGit**. La única ruta compartida distinta es CHANGELOG_MASTER.md. No hubo lecturas fallidas ni identificadores ausentes.

Todas las PR consultadas estaban abiertas,en borrador y sin fusionar,con base410b1dd70a3713b500a829aed55cb99cb74ad1d0:
| PR | Head fijado para la lectura | Alcance |
|---|---|---|
|[8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/8) |b685bbecbe39d8a7ea37f1884ef39fa04adfbf99 |ContratosSTT/3 |
|[9](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/9) |dad7350b48f425bac1f44acf329ac6f7a77d9204 |CombatLab |
|[10](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/10) |f06e289f5209806b767a09814c920901bc4df606 |AssetLab |
|[11](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/11) |0403d6467f4837f0f538de454eb159499881b5e0 |Vita3D,incluye fuentes de contratos/combate |

La coincidencia acredita la identidad exacta que Git atribuye a estos archivos. No prueba equivalencia funcional de los archivos exclusivos,correctitud del código,CI,rendimiento,GUI o hardware.

## Matriz de coincidencias
| Ruta | PR que comparten el blob | BlobGit |
|---|---|---|
|contracts/examples/hit.json |#8,#11 |e350d141a9ba0cfa13be673b17ecfbf5b0a9836a |
|contracts/examples/snapshot.json |#8,#11 |da3d19b8089389fafe85cc918fdf1625bcdf6baf |
|contracts/stt_play.c |#8,#11 |f8089d9c3540e91b49a908696cfb04e63bd1ccda |
|contracts/stt_play.h |#8,#11 |cb8025da03b64f9ea46e596f14cc2b971231abc8 |
|contracts/tests/encode.c |#8,#11 |f721c8859a68c499a7772bc2ef18f41d6dc3aff0 |
|docs/prototypes/contracts.md |#8,#11 |568ae58aa9331c84188dc5661478e6c049f2d02f |
|stt_monitor/play_protocol.py |#8,#11 |f6ac57a08c6d95705519558637834ecde61f7dbb |
|stt_monitor/protocol.py |#8,#11 |96997adfefcfff09fbdb9f73a94974e0db18cdb1 |
|tests/test_play_protocol.py |#8,#11 |400c56920165e62fe70375e6c34ae7c13c45d59d |
|.github/workflows/combat-lab.yml |#9,#11 |268813d9fc469023a4c6120fc5833f1680b186de |
|combat-lab/CMakeLists.txt |#9,#11 |26f4c142f8611ab5c382bda20f08296b2a8680c9 |
|combat-lab/include/stt_combat.h |#9,#11 |b0c292d16af0f2d3c376b347d6d446618fcc3d3b |
|combat-lab/src/demo.c |#9,#11 |580e96d74b19ad928ee7ea45048ba089e5758c2e |
|combat-lab/src/stt_combat.c |#9,#11 |1fd5c76a4cb61fc803ebe84ec3ef97b0c7fd892f |
|combat-lab/tests/test_combat.c |#9,#11 |035757d454296d82fe84ba7e51c5138497b7eff5 |
|docs/prototypes/combat.md |#9,#11 |296fd7cd07f6496faf459e1330b4c651c10abef9 |

La PR11 incluye9rutas de contratos/pruebas/documentación compartidas conPR8 y7deCombatLab/CI/documentación conPR9. AssetLab no comparte esos archivos de implementación; su coincidencia de ruta con las otras PR se limita al changelog. No se deduce dependencia de datos AssetLab→Vita ni un importador por esta relación.

## Changelog y futura integración
Los cuatro changelogs comparten un prefijo de12864caracteres y luego entradas propias. PR8 añade contratos;PR9,CombatLab;PR10,AssetLab. PR11 contiene entradas deCombatLab,contratos,Vita3D yentrega integrada.

Esto requiere revisar y consolidar las entradas al integrar. No se ha calculado ni provocado un conflictoGit. La indicación mergeable=true obtenida de GitHub es **individual respecto a la base**;no garantiza que una secuencia combinada sea fusionable sin ajustes.

Antes de una futura integración autorizada:
1. Elegir una estrategia para las fuentes repetidas,conservando una única versión canónica y la evidencia por frente.
2. Consolidar el changelog sin duplicar ni perder entradas; distinguir fechas de validación y tareas todavía pendientes.
3. Revisar archivos exclusivos y dependencias de contratos/combate/Vita con sus propietarios.
4. Revalidar los commits si cambian; no repetir pruebas ya aprobadas salvo cambios o riesgos concretos.
5. Mantener separada la recepciónSTT/3 de la implementaciónUDP del productor. No atribuir transporte físico a un buzón local.

No se ha elegido ni ejecutado una estrategia de fusión,no se cerraron PR ni se alteró main. PR3,PR7 yPR12 no forman parte de esta comparación combinada.

## Evidencia y coordinación
[Recibo completo de rutas,blobs y commits](prototype-overlap-review.json). Método: listar archivos cambiados de cada PR,calcular intersecciones y leer cada ruta desde el head_sha fijado,comparando el campo sha de blobGit. Los changelogs se leyeron completos para identificar prefijo y secciones. No se descargaron artefactos comerciales ni se repitieron pruebas de runtime.

El resultado se comunicó al coordinador de prototipos. Ninguna fuente de otro frente,el banco,los originales o la consola fue modificada.

# MOD230: una propiedad jerarquía↔matrices no confirmada

2026-10-22. Misma muestra de26.402bytes, SHA256 `6d98d22019ceafc1c44801ed45692610ed5c0b2db461dc1fb813526c7af374be`. Se reutiliza [el recibo de jerarquía](mod230-skeleton.md), cuyo SHA256 privado **`cd8570ac1238c3448c47ccda309fde8650ebb765b5b91a2b1bf25ad4c3b4ff11`** queda fijado por [la evidencia inmutable16111d8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/blob/16111d8ee806d46b835b72b6a7541bc6d7366d3f/docs/research/stt-re-20261021/mod230-skeleton-evidence.json). No se repite la selección ni el ensayo completo anterior, ni se abre otro modelo.

**Resultado:** una propiedad numérica predefinida no se cumple. Esto no invalida rangos, jerarquía o finitud anteriores; impide afirmar la relación funcional propuesta entre ambas familias para esta muestra. No se afirma que todas las posibles convenciones fallen ni que el archivo esté corrupto.

## Fuente y modelo comprobable

RevilLib commit **`e17f9718ea571f040a7e1f331c28a4d45a6066b5`**:

- [common.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/src/mtf_mod/common.cpp), blob `5435277ef757c0f6c7bdeae7efd0837fe44df8f1`: **MOD::Transforms devuelve refPoses**, primera tabla; **MOD::InverseBinds devuelve transforms**, segunda tabla. Los nombres internos por sí solos podrían inducir a intercambiarlas; aquí se sigue la API explícita.
- [mod_to_gltf.cpp](https://github.com/PredatorCZ/RevilLib/blob/e17f9718ea571f040a7e1f331c28a4d45a6066b5/toolset/mod_to_gltf/mod_to_gltf.cpp), blob `028e077b99021c53e6f40e5484083c04a93dd914`: ProcessSkeletons recibe Transforms, escribe transformaciones de nodos y los enlaza por parentIndex; MakeSkin consume InverseBinds. Se consultan esas decisiones de representación, **sin ejecutar exportador o skinning**. El exportador aplica conversiones propias de escala en su salida: no se reproduce ni valida aquí toda esa conversión.

Spike submódulo **`e83f3855e0a96b29eee3dcec98f428c1787ffad4`**, [src/matrix44.cpp](https://github.com/PredatorCZ/Spike/blob/e83f3855e0a96b29eee3dcec98f428c1787ffad4/src/matrix44.cpp), blob `bda29c33970093b6785c1931b3f6e54c074e3a94`: Matrix44 se reinterpreta como glm::mat4, con tamaños/alineaciones comprobados en fuente, y producto basado en esa representación. La [especificación glTF2.0.1](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html), página identificada por commit `8e798b02d254cea97659a333cfcb20875b62bdd4`, define almacenamiento column-major y composición global padre×local. Es contexto de la ruta del conversor, no una especificación del formato nativo MHXX.

Se fija **un modelo de coherencia inducido por esa ruta de referencia**: primera familia como matrices locales L; segunda como B. Representación column-major; raíces G=L, hijos G=G_padre×L. Propiedad única **G×B≈I** para cada slot. No se infiere una pose nativa por la etiqueta InverseBinds, ni se presupone que ambas familias estén en el mismo espacio en el juego.

## Protocolo fijado antes de medir

Archivo privado `analysis-local/mod230-matrix-property-20261022/protocol.json`, escrito antes del ensayo comercial, fija:

- Tolerancia absoluta **0,0001**, sin tolerancia relativa.
- Residuo máximo por pareja: máximo de los16valores absolutos de G×B−I.
- Aceptación: todos los pares dentro de tolerancia.
- Float32 LE de entrada promovido a float64; productos escalares mediante fsum.
- Sin cambio de ejes, unidades o escala; sin búsqueda de orden, transposición o permutación que ajuste el resultado.

La tolerancia es un umbral numérico en los valores de las matrices, no una precisión física o espacial acreditada. Se elige antes de ver el residuo; no se aumenta después del resultado.

## Lectura y resultado agregado

Se cotejan contra el recibo anterior los hashes de tres rangos: huesos[128,200), primera familia[200,392), segunda[392,584). **456bytes** leídos para la propiedad. Los padres se reutilizan por slots; no se interpretan remaps, skin maps, geometría o LMT. Dos pasadas SHA256 sobre el objeto completo pequeño verifican identidad antes/después; esos hashes atraviesan bytes que no se parsean. No se escriben matrices, posiciones, geometría o un binario nuevo.

| Comprobación | Resultado |
|---|---|
| Pares / residuos escalares |3 /48|
| Pares dentro de tolerancia |**0/3**|
| Raíces dentro de tolerancia |0/2|
| No raíces dentro de tolerancia |0/1|
| Residuo absoluto máximo |**143,62696838378906**|
| Criterio global ≤0,0001 |**No cumplido**|
| Fuente y rangos |Hashes coincidentes; objeto intacto|

Ese residuo no se interpreta como distancia, eje o unidad del juego. No se exportan valores de matrices ni errores por elemento. El fallo también aparece en las raíces bajo el modelo fijado, pero no se usan variantes adicionales para buscar una explicación numérica favorable.

## Pruebas y cierre

Herramienta propia `check_mod230_matrix_property.py --input <mismo objeto> --prior-receipt <recibo anterior> --expected-receipt-sha256 cd8570ac1238c3448c47ccda309fde8650ebb765b5b91a2b1bf25ad4c3b4ff11 --out <JSON nuevo>`. Rechaza sobrescribir salida y verifica identidad/rangos antes de calcular. Devuelve un resultado negativo explícito, no una aceptación implícita por terminar sin error.

**8pruebas sintéticas nuevas aprobadas**: composición padre/local no conmutativa de rotación y traslación, rechazo de inversa local en lugar de global, almacenamiento column-major, ambos lados de la tolerancia, conteos incompatibles, padre inválido, ciclo y NaN. Los valores de tests son propios/sintéticos. Ayuda CLI verificada; las campañas anteriores no se repiten ni suman como suite nueva.

[Recibo agregado público](mod230-matrix-property-evidence.json). Privados: protocol.json, receipt.json y acceptance.json. No se afirma independencia de validación semántica por haber escrito otra multiplicación matricial; se mide una propiedad de un modelo de referencia sobre los datos existentes.

**Aceptación del experimento cerrada, propiedad no confirmada.** El vínculo entre familias queda bloqueado para rig funcional/bind pose. Próximo criterio: una fuente compatible específicamente con esta variante MOD230/MHXX que acredite espacio, convención y cualquier transformación adicional necesaria, antes de formular otro ensayo. No variar órdenes/ejes o ajustar tolerancia sin evidencia. La jerarquía finita anterior se conserva; no se asocia LMT, aplica skinning, renderiza o adapta recursos. MOD990 y los bloqueos BLZ/LMT siguen abiertos.

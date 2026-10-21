# Evaluación de modelos CC0 — 22-10-2026

Descargas oficiales realizadas e inspeccionadas en PC. No hay instalación ni
FTP; tampoco se reemplaza la muestra propia del VPK actual. Este estudio
introduce recursos de terceros identificados, no los atribuye al proyecto.

| Paquete | Tamaño ZIP | SHA256 |
|---|---:|---|
|Kenney Mini Characters |2403059 bytes |9e1d48e6d7b8479ebbe84df71eb5bd8e1b3f0da546dea641890dccc8a02d0999 |
|Quaternius Medieval Weapons |3734480 bytes |546d6e168d71cc3ea0c5d388a7834658619ac2ace8be960050e5fb1dbd344a2a |

Autores/páginas:
- https://kenney.nl/assets/mini-characters
- https://quaternius.itch.io/lowpoly-medieval-weapons

Licencias: Mini Characters incluye License.txt con declaración CC0 (se conserva
en KENNEY-LICENSE.txt). El ZIP de armas no incluye archivo de licencia; la página
oficial del autor declara CC0. Se registra esta diferencia, sin inventar licencia
interna. Se conservan los originales localmente; no se publican ZIPs completos.

## Personaje inspeccionado

character-male-a.glb: 246916 bytes, 2 mallas, 1259 entradas POSITION (804+455),
723 triángulos (450+273), 2 skins que referencian 7 articulaciones cada una y
32 clips declarados, incluidos idle/walk/sprint/attack-melee-right. Las duraciones
se leyeron de metadatos de accessors; no se evaluaron las animaciones ni skinning.
Los tamaños de POSITION no equivalen a posiciones geométricas únicas.

No cabe directamente en el contrato de 256 vértices/512 triángulos. Su sistema
de skinning/glTF tampoco es el rig rígido con rotación Z del Asset Lab. Requiere
simplificación y evaluación/conversión de animación separadas. No se amplían
límites ni se simula soporte glTF completo para aceptar este personaje.

## Espada preparada para revisión

Fuente Quaternius OBJ/Sword.obj: 438 vértices/872 triángulos tras dividir quads
convexos. Las espadas originales inspeccionadas exceden el límite vigente.
Derivado de estudio por agrupación de vértices: 199 vértices/394 triángulos,
raíz rígida única y clip Static de un tick. Pose/1 canónico ocupa7474bytes,
SHA256 da8c1a437b2d090acda2f3f3b7fbe61bd548c665537b72a9134c994da6c09dd8.

Mantiene ejes, escala uniforme a1.4m de longitud y coloca Ymínimo en0; ese pivote
no es una empuñadura de mano verificada. Sin materiales/texturas/UV, skinning
ni animaciones importadas. La simplificación no es sin pérdidas:470triángulos
colapsados y8duplicados retirados. Desplazamiento máximo de vértice de origen
hasta su centroide:22.261mm; no es error Hausdorff de superficie ni garantía de
topología cerrada. Se rechazan candidatos con caras retenidas invertidas.

La comparación visual observada conserva silueta general, guarda, empuñadura y
punta; se pierden detalles. Es una aproximación para pruebas, no modelo final
ni Espada Larga fiel a ningún juego. No está equipada en el personaje ni VPK.

Archivos:
- quaternius-sword-study.stt.json: cargable por Asset Lab PC.
- quaternius-sword-study.pose.json: resultado del puente Pose/1.
- inspection.json: hashes, geometría y catálogo de clips inspeccionados.
- sword-comparison.png: captura comparativa generada/observada localmente;
  se entrega localmente, no es evidencia del renderer Vita.

## Reproducción

Guardar los dos ZIP originales con los nombres kenney_mini-characters.zip y
quaternius-medieval-weapons.zip en un directorio propio. Desde la rama del
estudio, definir STT_MODEL_INPUT_DIR a esa ruta y ejecutar:

```text
python tools/evaluate_models.py
python -m unittest discover -s tools -p test_evaluation.py -v
```

La generación de comparación requiere Pillow; las pruebas y lectores usan
biblioteca estándar. STT_PROJECT_ROOT permite indicar el checkout que contiene
asset-lab. No se ejecuta Blender/FBX ni código de paquetes descargados. Se leen
miembros ZIP conocidos sin extraer rutas arbitrarias. El adaptador OBJ solo
acepta triángulos/quads convexos; ignora materiales/normales/UV sin abrir archivos
referidos. No se presenta como importador universal. Los JSON generados
sobrescriben únicamente los nombres de salida propios en prepared/.

Validación local:5 pruebas aprobadas (convexidad/índices relativos, rechazo de
entradas inválidas, simplificación determinista, geometría y cuantización sin
inversión/degeneración). CI C del lector sobre el derivado pendiente al abrir.
No se ha compilado un VPK con estos modelos ni probado en consola.

# Interfaz Asset Lab → Vita: evaluación numérica — 21-10-2026

**Estado: revisión de interfaz y propuesta; no importador implementado.** Se utilizó exclusivamente la muestra original del proyecto publicada en PR10. No se abrieron ni adaptaron recursos comerciales.

## Fuente y evaluación real
STT Asset/1,muestra de4huesos,48vértices,72triángulos y2clips. SHA-256:6065aec43ff7ba2072b08a07ff9ea6479cd19a07803ad29ee3533ae4fd7a4800,coincidente con la entrega de AssetLab.

Se cargó el evaluador model.py por hash y se calculó la muestra a intervalos1/60s:
| Clip | Duración declarada | Duración×60 | Poses evaluadas |
|---|---:|---:|---:|
|Idle |2s |120 |120 |
|Practice swing |1,2s |72 |72 |

Las192poses produjeron coordenadas finitas. Las7claves y ambas duraciones caen en una cuadrícula entera de60Hz; no se redondearon ni regeneraron claves. La pose al tiempo duración coincidió con la inicial bajo el módulo temporal del evaluador. No es reproducción GUI ni medición de FPS del equipo.

Tras multiplicar por1000,sin cambio de base,los límites de vértices observados fueron:
| Eje | Mínimo mm | Máximo mm |
|---|---:|---:|
|X |-323,861410 |2100,556060 |
|Y |-147,374499 |3232,185549 |
|Z |-180 |180 |

Son límites de las poses muestreadas,**no extremos continuos de animación**. No describen un personaje comercial ni parámetros de combate.

## Contrato actual y decisiones pendientes
| Aspecto | AssetLab actual | Destino/propuesta y aceptación pendiente |
|---|---|---|
|Unidades |Metros |Convertir a mm con política explícita de redondeo;×1000 no decide los ejes |
|Ejes |+X derecha,+Y arriba,+Z hacia observador frontal |Vita declara +Z avance; acordar base de modelo/escena,cámara y rumbo. No invertir Z silenciosamente: una reflexión altera handedness y orientación de triángulos |
|Rotación |Z local en radianes,padres preceden hijos |Evaluador equivalente en destino o formato revisado; no binding implementado |
|Rig |Un hueso rígido por vértice |No introducir pesos mezclados,cuaterniones,texturas o features no soportadas por la entrada |
|Tiempo |Segundos continuos,interpolación lineal,bucle |Simulación60Hz y render limitado a30segúnprototipo. Para claves fuera de cuadrícula decidir muestreo/resampling explícito; no truncar |
|Eventos/combate |No colisiones ni eventos de impacto en el asset |No derivar ventanas o hitboxes por nombres/poses; contrato separado |
|Memoria |JSON≤1MiB y límites PC |Importador/runtime Vita necesita presupuesto propio; el tamaño del JSON no equivale a memoria residente |

Las coordenadas locales de la muestra caben en enteros de32bits al expresar mm,pero no se serializaron a un formato Vita. Cinco anclas numéricas verifican una **propuesta no aprobada** de redondeo a mitad alejándose de cero:0→0,±1m→±1000mm,±0,0005m→±1mm.

Ejemplo ilustrativo de empaquetado para esta muestra:56bytes para padres/offsets de huesos,672para vértices,432para índices y56para7claves,total1216bytes. Usa campos explícitos de16/32bits,sin alineación. **No es un formato aprobado,exportado ni una medida de memoria Vita**; omite cabeceras,nombres,runtime,alineación,búferes de render y otra memoria. Se incluye solo como cálculo verificable para discutir el futuro presupuesto.

## Aceptación del futuro adaptador
1. Declarar versión,unidades,base/avance,handedness,winding,jerarquía y política temporal/redondeo.
2. Con una muestra propia asimétrica,comprobar pivotes,orientación y triángulos tras conversión; no elegir un espejo por semejanza visual.
3. Comparar evaluadores origen/destino en poses conocidas,duraciones/bucles y error numérico con tolerancia explícita.
4. Probar presupuestos reales de importación,memoria y tiempo; separar PC,compilación y observación física.
5. Conservar independencia del banco comercial. Sin adaptación comercial mientras falten activos legales.

## Reproducción y evidencia
```powershell
python tools/assess_asset_bridge.py --model ../analysis-local/asset-bridge-review-20261021/model.py --sample ../analysis-local/asset-bridge-review-20261021/sample.stt.json --report ../analysis-local/logs/asset-bridge-new.json
```
El destino debe ser nuevo. La herramienta ejecuta el evaluador Python de proyecto indicado,debe revisarse antes de cargar código distinto. No usa GUI,sockets,archivos comerciales ni crea recursos destino;desactiva escritura de bytecode y acota poses/evaluaciones.

[Recibo numérico y hashes](asset-bridge-review.json),[herramienta propia](../../../tools/assess_asset_bridge.py). Fuentes:[AssetLabPR10](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/10),[contratosPR8](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/8),[VitaPR11](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/11).

Se comunicó la revisión al coordinador de prototipos. No se modificaron sus fuentes,el monitor,el banco o la consola. Las23pruebas previas de AssetLab siguen siendo evidencia del autor;esta evaluación no las reejecuta ni acredita GUI,hardware o importación.

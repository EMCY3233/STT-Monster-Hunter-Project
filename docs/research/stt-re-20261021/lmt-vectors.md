# MHXX 3DS: primeras pistas vectoriales decodificadas

21-10-2026. Continúa el encargo autorizado, con GU Switch excluido. El usuario ha autorizado expresamente el descifrado de sus archivos locales; esta etapa concreta decodifica datos LMT ya legibles, sin operación criptográfica, búsqueda de claves ni cambios en consola/FTP.

## Resultado reproducido con las cuatro muestras existentes

Se interpretaron las tablas de pistas de las cuatro cargas LMT67 del parche MHXX bajo el layout little-endian de punteros de 32 bits. Son las mismas muestras hash/índice ya documentadas; no se atribuyen a armas, ataques ni Frontier.

| Muestra local | Pistas declaradas y recorridas | Claves vectoriales decodificadas | Pistas vectoriales con claves | Pistas con variación entre claves | Vectores de referencia sin buffer |
|---|---:|---:|---:|---:|---:|
| common_entry_0084.lmt | 970 | 1.138 | 49 | 49 | 46 |
| common_entry_0085.lmt | 645 | 625 | 39 | 38 | 35 |
| common_entry_0086.lmt | 21 | 6 | 1 | 1 | 3 |
| common_entry_0087.lmt | 21 | 3 | 1 | 1 | 3 |
| Total | **1.657** | **1.772** | **90** | **89** | **87** |

El lector soporta buffers vectoriales cuantizados de 16 y 8 bits (códigos 4/5 en esta revisión). Normaliza sus componentes y aplica escala/base de la tabla de extremos. Para los buffers vacíos registra la referencia, sin inventar claves animadas. Las otras **1.480 pistas** quedan con `codec_not_decoded`: no son fallos de descompresión ni resultados interpretados.

La unidad temporal conservada es el índice de frame acumulado del buffer, **sin incorporar todavía la convención del frame de referencia**. No se convierte a segundos. En las 90 pistas se comprobaron pasos estrictamente crecientes y última clave dentro del número de frames declarado; cero infracciones observadas. No se han implementado blending, interpolación de la animación completa, rotaciones, eventos, jerarquías ni binding al rig. Los números no equivalen a animaciones reproducidas visualmente.

Se comprueban límites de tablas/punteros/buffers, componentes finitos, longitudes múltiplo del stride y disponibilidad de la tabla de extremos. Se relee cada fuente después del análisis para cotejar SHA-256. Las cuatro coinciden con los hashes previos. No se modificaron las muestras.

## Fuentes para interpretar el formato

Se consultaron implementaciones públicas de [layout de pista](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/bone_track.inl), [tabla de códigos y tipos](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/bone_track.cpp), [estructuras de buffers](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/codecs.hpp), [reglas de vectores y frames](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/codecs.cpp) y [extremos](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/internal.hpp). El lector Python es independiente; no se instaló ni ejecutó RevilLib. No es una comparación entre dos decoders ejecutados.

La biblioteca pública usa una frecuencia por defecto para evaluar pistas, pero ese valor no demuestra el FPS de estos archivos ni del juego. Se mantiene `fps=null`.

## Entregables y reproducción

- Herramienta propia: `tools/stt_re/decode_lmt_vectors.py`.
- [Resumen publicable por archivo](lmt-vectors-summary.json): SHA-256 de entrada, conteos, códigos y límites de validación, sin valores vectoriales comerciales.
- [Recibo del análisis local](lmt-vectors-receipt.json): hashes/tamaños de los informes locales; esos informes contienen las claves y referencias y **no se publican**.
- Once pruebas sintéticas nuevas; suite total de **36 pruebas** al cerrar la etapa. Incluyen extremos cuantizados conocidos, stride, acumulación de frames, datos no finitos, límites y versión incompatible. No son prueba física ni validación de fidelidad visual.

```powershell
& $python tools/stt_re/decode_lmt_vectors.py --samples "$projectRoot/analysis-local/samples/located-resources" --out "$projectRoot/analysis-local/lmt-vector-decoding-new"
& $python -m unittest discover -s tests -p 'test_stt_re*.py' -v
```

Usar una carpeta de salida nueva fuera de Git. No subir los archivos `.vectors.json`: son datos derivados comerciales. El resumen es metadato; la herramienta no ejecuta el juego ni altera sus originales.

## Siguiente aceptación y bloqueos

1. Contrastar con un segundo decoder los valores y la convención temporal de una pista; después implementar sus referencias/interpolación y rotaciones.
2. Demostrar el vínculo de una pista con un hueso del modelo y su matriz bind; no elegir un rig solo por cercanía de nombres.
3. Validar una vista previa local completa antes de declarar reproducción. Conservar FPS, ejes y unidades como desconocidos hasta verificarlos.

Frontier sigue pendiente de copia local completa según el recibo existente; no se reanudó, detuvo ni intervino en la operación de otro Work. Sus cabeceras exteriores aún no se han identificado. Las bases 3DS siguen cifradas y no se dispone en esta tarea de material criptográfico verificado para abrirlas. La autorización del usuario está registrada, pero no sustituye ese requisito técnico. No se afirma «todo descifrado».

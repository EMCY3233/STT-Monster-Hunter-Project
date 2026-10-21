# MHFU: DATA.BIN procesado completo

Fecha: 2026-10-21. Juego local PSP ULES01213. Sin GU Switch, red de consola ni FTP. Resultados derivados privados, sin publicar archivos comerciales ni tablas criptográficas.

## Resultado y alcance

Tras el piloto de cinco archivos se procesaron **las 6.657 entradas** de DATA.BIN. Fuente: región ISO offset 113.967.104, 772.732.928 bytes, SHA-256 `4c65ae5c58f5b983321131391db0dce1d72ccd53b4cd28520429121333a82dec`, comprobado antes de interpretar. Tabla descifrada: 34.816 bytes; primer sector, orden de offsets y centinela final coinciden con el tamaño físico. Tabla y todas las entradas transformadas superan la comparación byte a byte al recifrarlas; las excepciones del formato se conservan sin transformación.

6.657 salidas, 772.698.112 bytes asignados, 6.558 hashes distintos. Las salidas incluyen posible relleno de sectores. **No son longitudes útiles definitivas**: los ajustes posteriores al centinela aún no se interpretaron. No se ha demostrado el significado de cada carga ni modelos, esqueletos, animaciones, IA o hitboxes. Un recifrado exacto prueba reversibilidad con este algoritmo y configuración; no es validación independiente de la semántica.

## Fuente y reproducción

Implementación primaria: [mhef/psp.py de svanheulen](https://github.com/svanheulen/mhef/blob/master/mhef/psp.py), blob Git `cab831b9eab30c1b4a80d571ea5c3dc256e0543f`, copia local SHA-256 `39204fcaae7283b0ba5b8584eb467442452140d6be98dc2c1c23d267a0cf3586`. Se conserva su cabecera GPL. [mhff/psp/data.py](https://github.com/svanheulen/mhff/blob/master/psp/data.py) documenta la organización por sectores y ajustes de longitud.

`tools/stt_re/probe_mhfu_data.py` selecciona por AST únicamente DataCipher e identificadores de juego del módulo revisado. Adapta en memoria `array.tostring` a `tobytes`. No importa el módulo completo ni usa AES/savedata ni su escritura de archivos. Variante EU seleccionada por ULES01213. Código externo y tablas quedan fuera del repositorio.

Guardas: alineación de 2.048 bytes; tabla entre 2 KiB y 8 MiB; centinela obligatorio; offsets monótonos; hasta 100.000 entradas; máximo 64 MiB por entrada; lecturas completas; salida nueva fuera de Git; hash de DATA contra manifiesto; recifrado y comparación exactos. La ISO se abre solo para lectura.

Repetición: `probe_mhfu_data.py --iso <ISO propia> --manifest <psp-files.json> --upstream <mhef revisado> --out <carpeta nueva fuera de Git> --all`. Sin `--all`, procesa cinco cargas. Requiere el archivo externo de SHA verificado; no se descarga automáticamente.

Evidencia privada: `analysis-local/mhfu-data-decoded-20261021/report.json`, tabla y 6.657 archivos numerados con SHA-256, LBA, bytes asignados, tiempo y comprobación por entrada. [Resumen público](mhfu-data-evidence.json) incluye hash del informe íntegro, conteos y límites. No se incorporó este conjunto al banco compartido ni se modificaron sus bases de datos.

## Próximos experimentos

Validar tamaños útiles posteriores al centinela; detectar contenedores internos mediante límites independientes y muestras pequeñas; verificar PAC/PMO frente a código primario antes de exportar geometría. Contrastar imports/relocaciones del ELF PSP obtenido con PPSSPP. Salidas organizadas por índice y procedencia, sin clasificación por armas.

46 pruebas sintéticas aprobadas, incluidas seis nuevas sobre tablas inconsistentes y presupuestos. La transformación real completa constituye una evidencia adicional distinta de esos tests.

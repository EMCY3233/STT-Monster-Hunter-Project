# Derivados enlazados al banco — 21-10-2026

## Primera entrada
Se enlazó una salida local de349bytes obtenida por el frente de investigación de una muestra JKR. Se comprobaron nuevamente el archivo fuente238bytes,la salida y el recibo,comparando hashes y tamaños con el catálogo y la evidencia. El proceso de descompresión no se repitió en este frente.

Fuente:rePatch/PCSG00350/dat/load/uc/uc00_001_03.bin.
SHA-256 fuente:4fcc62ad49f42b315d69013b2d312845b2d301dc97d47526047497f37125d385.
SHA-256 salida:592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c.
SHA-256 recibo:e1a1984e360cfb2a2a39041657f393cd2590b111f4042483e17b599cf75c0553.
La salida sigue sin firma ni semántica reconocidas.

Investigación registra349/349bytes y222/222bytes de carga consumidos,sin sobrantes. La terminación es por tamaño declarado,no por marcador final ni checksum. [Método y límites en PR7](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/7),commitbf1f41c,frontier-jkr-sample.md. No se extrapola el resultado a los43JKR restantes.

## Organización del banco
El archivo real continúa en analysis-local/frontier-jkr-smallest-20261021/decoded.bin. No se copia ni mueve. **Conservar decoded.bin y receipt.json como evidencia**,aunque estén en un directorio de ensayo.

Un registro en analysis-local/resource-bank/derivatives.jsonl enlaza el ID9809 del catálogo fuente,hashes,rutas y evidencia. Es un catálogo adicional de metadatos,con una entrada y sin bytes comerciales. SQLite,los manifiestos físicos/ARC y sus hashes permanecen intactos. Por eso siguen9888archivos físicos/21696entradasARC/8823objetos en ese alcance,más1derivado enlazado por separado.

[Metadatos publicados de la entrada](bank-derivatives.jsonl). Los contenidos permanecen únicamente locales. El conjunto de derivados usa registro separado,versión1; no se afirma una migración del esquema SQLite.

## Consulta
```powershell
python tools/search_resource_bank.py --bank ../analysis-local/resource-bank 592fe0ca19e741430f4fa669eea3df71e83935dec2812bf51524ad279074691c
```
La respuesta añade derivatives a files/entries. Busca por ruta fuente,por ruta de salida o por hash fuente/salida. El límite se aplica por categoría; la búsqueda consulta metadatos,no vuelve a verificar el contenido ni garantiza que una ruta externa no se haya movido después.

## Incorporación verificada
```powershell
python tools/link_bank_derivative.py --bank ../analysis-local/resource-bank --project .. --source-relative MHF-Vita/PCSG00350/rePatch/PCSG00350/dat/load/uc/uc00_001_03.bin --output ../analysis-local/frontier-jkr-smallest-20261021/decoded.bin --evidence ../analysis-local/frontier-jkr-smallest-20261021/receipt.json --evidence-sha256 e1a1984e360cfb2a2a39041657f393cd2590b111f4042483e17b599cf75c0553
```
La herramienta valida archivos/recibo,exige que fuente/salida/banco/evidencia permanezcan en el proyecto,abre SQLite en lectura y añade metadatos al registro adicional. Una entrada idéntica no se duplica. No ejecuta el recurso,decodificador ni comandos de red. La verificación del recibo no autentica a su autor: acredita correspondencia con los bytes locales y la evidencia seleccionada.

Cinco pruebas nuevas aprobadas:enlace/idempotencia y consulta sin mutación SQLite,tamper de salida,tamper de recibo,fuente ausente del catálogo y rutas externas. Cinco pruebas anteriores del banco pasaron tras ampliar la búsqueda. También se ejecutó la consulta real por hash y se cotejó otra vez el hash SQLite con el registro original de Vita.

Sin clasificación por armas,adaptación comercial,publicación de contenidos,FTP ni cambios de consola. Antes de ampliar JKR queda pendiente una aceptación útil del formato interior,como documenta investigación.

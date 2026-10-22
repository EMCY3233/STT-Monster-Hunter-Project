# Auditoría de coherencia del banco — 21-10-2026

Auditoría de metadatos en modo SQLite de solo lectura. No vuelve a leer los18,2GB de archivos físicos ni sustituye los recibos de hashes de las etapas anteriores.

## Resultados
| Comprobación | Resultado |
|---|---:|
|Archivos físicos registrados|9888|
|Hashes físicos distintos|9535|
|Grupos de hashes repetidos entre archivos físicos|161|
|Ocurrencias físicas repetidas sobre la primera|353|
|Bytes repetidos contabilizados|144631792|
|Entradas ARC registradas|21696|
|Objetos registrados|8823|
|Objetos sin referencia desde entradas|0|
|Hashes comunes a archivos físicos y objetos|105|
|Hashes distintos del conjunto físico+objetos|18253|
|Errores de referencias/estados/tamaños|0|
|SQLite integrity_check|ok|

Los bytes físicos sumados por catálogo son18205335558; incluyen originales y derivados. No representan tamaño de instalación ni almacenamiento comercial único. Los hashes repetidos indican contenido previamente registrado como idéntico, no equivalencia funcional, licencia o intercambiabilidad de plataformas. **No se borró ni sustituyó ningún duplicado**.

Se comprobaron referencias de entradas a archivos y objetos, estado de verificación, tamaño declarado frente a objeto y coherencia de tamaño para un mismo hash. Este alcance no comprueba otra vez que cada archivo u objeto siga existiendo físicamente: esa evidencia pertenece a los inventarios/recibos anteriores.

## Repetición
```powershell
python tools/audit_bank_catalog.py --catalog ../analysis-local/resource-bank/catalog.sqlite --report ../analysis-local/logs/bank-audit-new.json
python -m unittest discover -s tests -p test_bank_catalog_audit.py -v
```

El informe requiere destino nuevo. Cinco pruebas sintéticas aprobadas: duplicados sin mutación del SQLite, objeto ausente, fuente inexistente, tamaño incoherente y fuente no verificada. [Código propio](../../../tools/audit_bank_catalog.py),[informe de metadatos](bank-catalog-audit.json). Los ejemplos del informe conservan solo rutas/tamaños/hashes, sin bytes de juego.

## Coordinación de formatos
El frente de investigación comunicó validación estructural limitada de50candidatos de Frontier, coincidentes con el censo:44cabecerasJKR/LZ,5ECD y1firmaSCE. Sus contenidos no están descifrados/descomprimidos y el SCE no tiene estructura interna validada. Las52pruebas comunicadas pertenecen a ese frente,[PR7](https://github.com/EMCY3233/STT-Monster-Hunter-Project/pull/7),no a esta auditoría. Se conserva división de trabajo: aquí banco/metadatos; allí formatos/ejecutables.

Sin clasificar por armas, adaptar recursos, acceder por FTP ni modificar consola, banco u originales.

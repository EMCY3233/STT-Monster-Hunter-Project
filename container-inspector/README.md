# Inspector C++17 NCSD/NCCH de solo lectura

Alcance: inspección estructural de imágenes .3DS/.CCI NCSD con hasta ocho
particiones NCCH, y NCCH independientes. La extensión no determina el formato.
No identifica semánticamente MH4U ni ejecuta el juego.

## Uso

    cmake -S container-inspector -B build/inspector
    cmake --build build/inspector --config Release
    ctest --test-dir build/inspector -C Release --output-on-failure

Windows usa SHA-256 de BCrypt (SDK Windows); Linux requiere OpenSSL de desarrollo.
Ejecutar stt-inspect ruta/a/imagen.cci. Informe a stdout; errores a stderr.
Retornos: 0 inspección aceptada, 1 inválido/no soportado/error de lectura,
2 argumentos incorrectos. El programa solo abre un ifstream binario y no crea
archivos. Redirigir stdout es responsabilidad del llamante; nunca redirigirlo a
la entrada.

## Contrato y límites

* Lectura de cabeceras de 512 bytes, campos little endian, tamaños/offsets
  calculados en uint64_t. Exponentes de unidad mayores de 22 rechazados para
  impedir overflow de campos uint32_t.
* Valida límites contra archivo, tamaño NCSD y tamaño NCCH, pares offset/tamaño,
  regiones solapadas, particiones solapadas y tamaños de regiones hash.
* Permite cola NCSD recortada si todas las particiones declaradas siguen presentes.
  No acepta una partición parcialmente ausente, NAND NCSD ni particiones no NCCH.
* Exheader ausente o perfil de 0x400 bytes (más descriptor de acceso de 0x400);
  otros tamaños se rechazan. El soporte es deliberadamente conservador.
* Muestra flags crudos, crypto method, NoCrypto, FixedCryptoKey y seed.
  Son declaraciones de cabecera, no prueba de que los bytes estén cifrados.
* Calcula SHA-256 del archivo completo por bloques de 64 KiB con memoria acotada.
  Muestra los cuatro SHA-256 almacenados en NCCH como reported_only: no compara
  hashes de contenido, no verifica firmas RSA ni certifica autenticidad.
* No hay claves, descifrado, extracción ExeFS/RomFS, recursos comerciales,
  modificaciones, reparación ni acceso a PS Vita. Un proceso externo que
  cambie el archivo durante la lectura no está cubierto por una instantánea
  atómica. La entrada debe permanecer estable.
* Pendiente: validación con una copia MH4U autorizada, comprobación independiente
  de formatos heredados, verificación de regiones en claro y parser RomFS.
  Aceptar una cabecera sintética no acredita compatibilidad con el juego.

## Coordinación y evidencia

Base revisada: main f199bd07b4e05ee4f7e56ed616840518374f3300.
AGENTS.md leído; 25 PR abiertas revisadas el 22 de octubre de 2026.
PR #7 mantiene investigación/extractor ARC; #36 núcleo PC C++17; #27 materiales.
Este directorio y su workflow son independientes, sin modificar sus ramas o Vita.
No se requiere fusionar estas PR para compilar el inspector.

Prueba local: MSVC x64 C++17 /W4 /WX, 14 pruebas unittest correctas, incluidas
512 truncaciones de cabecera. SHA-256 contrastado con hashlib y fuente idéntica
antes/después en cada caso. La primera ejecución falló por permisos del temporal
del entorno; repetición con TEMP/TMP dentro del workspace correcta.
Solo muestras generadas en memoria; no se ha abierto ninguna ROM comercial.
CI Linux/Windows queda como evidencia separada, pendiente hasta completarse.

Referencias de formato (consulta 22-10-2026):
https://3dbrew.org/wiki/NCSD
https://docs.mikage.app/NCCH/
Se usa la descripción de campos y flags, sin copiar implementaciones ni ejemplos
comerciales. Las referencias no constituyen validación de una muestra MH4U.

## Verificación y listado (ampliación)

    stt-inspect imagen.cci --verify --list-romfs

--verify compara SHA-256 de logo, exheader, superblock ExeFS y superblock
RomFS con la cabecera NCCH. Regiones ausentes se indican como absent.
Si la cabecera declara cifrado, solo se verifica el logo en claro; las regiones
de contenido se marcan skipped_encrypted. Una discrepancia devuelve 1.
No comprueba los hashes de archivos ExeFS ni toda la jerarquía IVFC.

--list-romfs interpreta IVFC versión 0x10000 y el nivel 3 en claro. Muestra rutas,
tamaños y offsets absolutos sin leer/exportar el contenido de los archivos.
Rechaza tablas fuera de límites, registros truncados, enlaces a mitad de registro,
ciclos, padres incorrectos, nombres duplicados, nodos no alcanzables y datos fuera
del nivel 3. Los buckets hash de nombres se delimitan pero no se validan.
Nombres UTF-16 se representan mediante caracteres ASCII y escapes de unidades
Unicode; no se normalizan. No son rutas para extracción.

Presupuestos: 64 MiB de metadatos, 100.000 entradas por tabla, profundidad 128,
nombre 1024 bytes, ruta 8192 caracteres, informe de archivos 32 MiB por RomFS,
bloques IVFC entre 512 bytes y 1 MiB. Se rechazan perfiles fuera del alcance.
El árbol completo IVFC, las firmas y la autenticidad siguen sin verificarse.

Fuentes adicionales de campos/layout:
https://docs.mikage.app/RomFS/
https://pyctr.readthedocs.io/en/stable/_modules/pyctr/type/romfs.html
La segunda se consultó como referencia independiente para la ubicación física
del nivel 3; no se copió su implementación.

La compilación local de esta ampliación pasó /W4 /WX, pero Windows Control de
aplicaciones bloqueó la ejecución del nuevo binario (WinError 4551). Las pruebas
C++ de la ampliación se ejecutan separadamente en CI con muestras sintéticas.
Ninguna ROM ni listado privado se publica en el repositorio.

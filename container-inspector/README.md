# Inspector C++17 NCSD/NCCH de solo lectura

Inspección estructural de imágenes .3DS/.CCI NCSD con hasta ocho particiones
NCCH, y NCCH independientes. La extensión no determina el formato.

## Compilar y probar

    cmake -S container-inspector -B build/inspector
    cmake --build build/inspector --config Release
    ctest --test-dir build/inspector -C Release --output-on-failure

Windows usa SHA-256 de BCrypt (SDK Windows); Linux requiere OpenSSL de desarrollo.

    stt-inspect imagen.cci
    stt-inspect imagen.cci --verify --list-romfs

Informe a stdout; errores a stderr. Retornos: 0 inspección aceptada,
1 inválido/no soportado/error de lectura/hash discordante, 2 argumentos incorrectos.
Un fallo descarta el informe parcial. El programa solo abre un ifstream binario y
no crea archivos. Nunca redirigir stdout a la entrada.

## Inspección estructural

Cabeceras de 512 bytes, campos little endian y tamaños/offsets uint64_t.
Valida límites contra archivo, tamaño NCSD y tamaño NCCH, pares offset/tamaño,
regiones y particiones solapadas, tamaños de regiones hash. Permite cola NCSD
recortada si todas las particiones declaradas siguen presentes.

Perfil conservador: exheader ausente o 0x400 bytes más descriptor de acceso de
0x400; exponentes de unidad hasta 22 (impide overflow de campos uint32_t);
solo particiones NCCH. No acepta NAND NCSD ni particiones parcialmente ausentes.
Muestra flags crudos, crypto method, NoCrypto, FixedCryptoKey y seed.
Son declaraciones de cabecera, no prueba independiente del cifrado de los bytes.
SHA-256 del archivo completo calculado por bloques de 64 KiB.

## Verificación de hashes

--verify compara SHA-256 de logo, exheader y superblocks ExeFS/RomFS con NCCH.
Regiones ausentes se indican absent. Si la cabecera declara cifrado, solo se
verifica el logo en claro; el contenido se marca skipped_encrypted.
El modo básico informa hashes almacenados sin compararlos. Los resultados
de comparación se muestran individualmente como hash=verified.

No comprueba hashes de archivos ExeFS, toda la jerarquía IVFC ni firmas RSA.
La coincidencia de estos hashes no certifica autenticidad ni integridad completa.

## Listado RomFS

--list-romfs interpreta IVFC versión 0x10000 y su nivel 3 en claro. Muestra
rutas, tamaños y offsets absolutos sin leer/exportar el contenido de archivos.
Rechaza tablas fuera de límites, registros truncados, enlaces a mitad de registro,
ciclos, padres incorrectos, nombres duplicados, nodos no alcanzables y datos fuera
del nivel 3. Delimita los buckets hash de nombres, pero no los valida.
Representa nombres UTF-16 mediante ASCII y escapes de unidades Unicode;
no los normaliza ni los usa para escribir rutas.

Presupuestos: 64 MiB de metadatos, 100.000 entradas por tabla, profundidad 128,
nombre 1024 bytes, ruta 8192 caracteres, informe de archivos 32 MiB por RomFS,
bloques IVFC entre 512 bytes y 1 MiB. Perfiles mayores se rechazan.

## Evidencia y coordinación

Base: main f199bd07b4e05ee4f7e56ed616840518374f3300. AGENTS.md leído.
PR abiertas revisadas: #7 investigación/ARC, #27 materiales, #36 núcleo PC,
#39 inspector. Carpeta y workflow independientes; sin modificar sus ramas,
monitor, banco privado ni Vita. No depende de fusionar otras PR.

Código 1003ba2:
* MSVC x64 C++17 /W4 /WX y CMake Release locales: compilación correcta.
* Ejecución local confirmada el 23-10-2026 tras resolver el usuario el bloqueo
  anterior de Windows Control de aplicaciones (WinError 4551). Las 21 pruebas
  sintéticas locales pasan y el C++ ejecuta --verify --list-romfs sobre la
  imagen privada: seis hashes presentes coinciden, y sus 11.512 entradas
  coinciden con la referencia Python en partición, ruta, tamaño y offset.
  SHA-256 completo de la imagen nuevamente contrastado e idéntico.
* CI Windows/Linux x Debug/Release: cuatro trabajos correctos, con 21 pruebas
  sintéticas por trabajo, incluidas 512 truncaciones de cabecera, corrupción de
  hashes, ciclos, padres, enlaces, tablas, tamaños y nombres inseguros.
  https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39860980537
* La fuente queda intacta antes/después y SHA-256 se contrasta con hashlib.
* Comprobación privada de la imagen indicada por el usuario mediante referencia
  Python independiente: seis hashes NCCH presentes coinciden; listados RomFS
  de las tres particiones y SHA-256 completo antes/después idéntico. Esto valida
  la referencia sobre esa imagen; el contraste C++ posterior se registra arriba.
  Los informes, rutas comerciales y bytes permanecen fuera de Git.

Sin claves, descifrado, extracción, reparación, recursos comerciales ni acceso a
PS Vita. No ejecuta MH4U ni interpreta sus formatos de modelos/animación.
Pendiente: verificar todo el árbol IVFC, hashes por archivo ExeFS y buckets RomFS.
La entrada debe permanecer estable: no se ofrece instantánea atómica frente a
cambios de otros procesos.

## Referencias de formato

Consulta 22-10-2026:
* https://3dbrew.org/wiki/NCSD
* https://docs.mikage.app/NCCH/
* https://docs.mikage.app/RomFS/
* https://pyctr.readthedocs.io/en/stable/_modules/pyctr/type/romfs.html

La última se consultó para contrastar la ubicación física del nivel 3; no se
copió su implementación. No se incorporaron ejemplos comerciales.

## Revisión del 23-10-2026

Tres regresiones reproducidas y corregidas:
* El límite de ruta incluye ahora el nombre del archivo; también se limita a
  32 MiB la suma de rutas pendientes del recorrido.
* Un superblock presente cuya longitud de hash sea cero aparece como
  not_verified_empty_hash_range, no como absent. El retorno 0 significa
  inspección aceptada; consultar todos los estados por región.
* --verify ya no imprime reported_only junto a comparaciones realizadas.

Se añaden pruebas de rutas completas, árboles anidados con Unicode, RomFS vacío,
presupuesto de metadatos y estados del informe. Suite ampliada a 27 pruebas.
Linux Debug habilita ASan/UBSan; las otras tres combinaciones conservan sus
compilaciones normales. Las pruebas de regresión fallaron antes de los cambios.

REA se revisó como herramienta de análisis posterior, no como dependencia del
lector. Su proveedor Ghidra experimental en Windows admite PE y raw NMOS 6502,
no establece soporte directo de imágenes NCSD/NCCH ni ARM11/3DS. No se ha
instalado ni registrado REA desde esta revisión.
Referencia: https://github.com/morluto/rea/blob/main/docs/windows-ghidra-p0.md

## Integridad de archivos (23-10-2026)

    stt-inspect imagen.cci --verify-integrity --list-romfs

--verify-integrity incluye --verify y añade los hashes individuales de los
archivos ExeFS y los tres niveles del árbol IVFC de RomFS en claro. Lee contenidos
para calcular hashes, pero no los extrae ni escribe. Verifica también los bytes
de padding de cada bloque físico contra el hash almacenado.

El perfil IVFC admitido usa versión 0x10000, bloques de 512 bytes a 1 MiB,
niveles lógicos secuenciales y orden físico de RomFS 3DS: cabecera/master, datos
de nivel 3, nivel 1 y nivel 2. Comprueba sumas, alineaciones, rangos y capacidad
de tablas padre antes de leer. Límite total: 8.000.000 bloques por RomFS.
No admite perfiles Switch/save ni intenta interpretarlos como RomFS 3DS.

ExeFS admite diez registros, offsets relativos al final de la cabecera de
512 bytes y hashes en orden inverso. Rechaza nombres duplicados, padding de
nombre inválido, rangos fuera del contenedor y archivos solapados.

Suite ampliada a 38 pruebas: árbol completo y multibloque, cola parcial,
padding corrupto, alteraciones en cada nivel, layout y exponentes inválidos,
archivos ExeFS corruptos, hashes intercambiados y límites/solapamientos.

Este modo no verifica firmas RSA, autenticidad ni buckets hash de nombres
RomFS. Un árbol coherente es una comprobación de integridad interna, no una
certificación de procedencia.
Fuentes y búsqueda en plataformas: RESEARCH.md.

El modo --verify-integrity exige que el hash NCCH cubra la cabecera ExeFS
completa y la cabecera/master hashes IVFC; rechaza una cobertura declarada
insuficiente. --verify conserva su informe explícito de rangos vacíos.

Resultado local sobre la imagen privada indicada por el usuario: coinciden los
tres archivos ExeFS y los 673.229 bloques IVFC de las tres particiones. Referencia
Python independiente reproduce los tres hashes ExeFS y los recuentos IVFC
[41,5144,658418], [1,14,1755], [1,61,7794]. SHA-256 completo idéntico al anterior.
No se publican nombres RomFS, contenidos ni hash privado de la imagen.

Los pendientes históricos de hashes por archivo ExeFS/IVFC descritos arriba
quedan cubiertos por --verify-integrity en este perfil. Siguen pendientes los
buckets de nombres, firmas/autenticidad y formatos internos de recursos MH4U.

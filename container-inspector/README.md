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
* Windows Control de aplicaciones bloqueó la ejecución local del nuevo binario
  (WinError 4551). No se presenta esta compilación como prueba funcional.
* CI Windows/Linux x Debug/Release: cuatro trabajos correctos, con 21 pruebas
  sintéticas por trabajo, incluidas 512 truncaciones de cabecera, corrupción de
  hashes, ciclos, padres, enlaces, tablas, tamaños y nombres inseguros.
  https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39860980537
* La fuente queda intacta antes/después y SHA-256 se contrasta con hashlib.
* Comprobación privada de la imagen indicada por el usuario mediante referencia
  Python independiente: seis hashes NCCH presentes coinciden; listados RomFS
  de las tres particiones y SHA-256 completo antes/después idéntico. Esto valida
  la referencia sobre esa imagen, no la ejecución C++ local de esta ampliación.
  Los informes, rutas comerciales y bytes permanecen fuera de Git.

Sin claves, descifrado, extracción, reparación, recursos comerciales ni acceso a
PS Vita. No ejecuta MH4U ni interpreta sus formatos de modelos/animación.
Pendiente: ejecutar esta ampliación C++ sobre la imagen privada cuando el entorno
lo permita, verificar todo el árbol IVFC, hashes por archivo ExeFS y buckets RomFS.
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

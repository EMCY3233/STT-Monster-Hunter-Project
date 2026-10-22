# Lector C++17 NCSD/NCCH de solo lectura

Inspecciona .3DS/.CCI NCSD con hasta ocho particiones NCCH y NCCH independientes.
La extensión no determina el formato. No ejecuta MH4U.

## Compilar y probar

    cmake -S container-inspector -B build/inspector
    cmake --build build/inspector --config Release
    ctest --test-dir build/inspector -C Release --output-on-failure

Windows usa BCrypt del SDK Windows; Linux requiere OpenSSL de desarrollo.
Linux puede activar ASan/UBSan con -DSTT_SANITIZERS=ON.

## Uso y modos

    stt-inspect imagen.cci
    stt-inspect imagen.cci --verify
    stt-inspect imagen.cci --verify-integrity --list-romfs
    stt-inspect imagen.cci --verify-romfs-index

- Básico: cabeceras, particiones, regiones, flags de cifrado, hashes almacenados
  y SHA-256 completo por bloques de 64 KiB.
- --verify: compara hashes NCCH de logo, exheader y superblocks en claro.
  Regiones ausentes se indican absent; una región presente con rango hash vacío
  se marca not_verified_empty_hash_range.
- --verify-integrity: incluye --verify, hashes individuales de archivos ExeFS
  y todos los bloques/padding de los tres niveles IVFC de RomFS en claro.
- --verify-romfs-index: incluye --verify-integrity y comprueba los dos índices
  hash de nombres RomFS, incluidos raíz, todos los directorios y archivos.
  No muestra nombres de archivo salvo si se añade --list-romfs.
- --list-romfs: muestra rutas, tamaños y offsets de archivos del nivel 3 IVFC.
  Se puede combinar con los modos de verificación.

Informe a stdout, errores a stderr. Retornos: 0 inspección aceptada,
1 inválido/no soportado/error de lectura/hash discordante, 2 argumentos incorrectos.
Un fallo descarta el informe parcial. Retorno 0 no significa que se hayan
verificado firmas o regiones cifradas: consultar los estados de cada región.
El programa solo abre un ifstream binario y no crea archivos.
Nunca redirigir stdout a la entrada.

## Validaciones

Campos little endian, offsets y tamaños uint64_t, límites contra archivo y
contenedores, pares offset/tamaño, regiones y particiones sin solapamientos.
Se admite cola NCSD recortada si todas sus particiones siguen presentes.

ExeFS: diez registros, offsets relativos al final de su cabecera de 512 bytes,
hashes en orden inverso. Rechaza nombres duplicados, padding de nombre inválido,
rangos fuera del contenedor y archivos solapados.

IVFC: versión 0x10000, niveles lógicos secuenciales, orden físico 3DS
cabecera/master, nivel 3, nivel 1 y nivel 2. Comprueba sumas, alineaciones, rangos
y capacidad de tablas padre. Verifica bloques completos con padding físico.
Exige que el hash NCCH cubra cabecera ExeFS y cabecera/master hashes IVFC.

RomFS: tablas y registros completos, enlaces a límites de registro, ausencia de
ciclos o referencias compartidas indebidas, padres correctos, nombres únicos,
nodos alcanzables y datos dentro del nivel 3. Nombres UTF-16 representados por
ASCII y escapes de unidades Unicode; no se normalizan ni usan para escribir.

Índices RomFS: calcula el hash de formato sobre padre y unidades UTF-16
originales. Recorre buckets y cadenas, comprueba que cada registro esté en el
bucket correcto y aparezca exactamente una vez, detecta ciclos, enlaces
compartidos, registros ausentes y offsets que no sean inicio de registro.
No impone un número primo de buckets ni un orden particular de colisiones.

## Perfil y presupuestos

- Exheader ausente o 0x400 bytes más descriptor de acceso de 0x400.
- Exponentes de unidad hasta 22, para evitar overflow de campos uint32_t.
- Solo particiones NCCH; no admite NAND NCSD, Switch/save ni particiones truncadas.
- Bloques IVFC entre 512 bytes y 1 MiB; hasta 8.000.000 bloques por RomFS.
- Hasta 64 MiB de metadatos, 100.000 registros por tabla, profundidad 128,
  nombres de 1024 bytes y rutas completas de 8192 caracteres.
- Hasta 32 MiB de rutas pendientes y 32 MiB de informe de archivos por RomFS.
- Hasta 4 MiB por tabla de buckets (1.048.576 buckets).

Flags NoCrypto/FixedCryptoKey/seed son declaraciones, no prueba independiente de
cifrado. Contenido declarado cifrado se omite explícitamente, sin descifrar.
La entrada debe permanecer estable; no se ofrece instantánea atómica frente
a escrituras de otros procesos.

## Evidencia y coordinación

AGENTS.md leído. Base main f199bd07b4e05ee4f7e56ed616840518374f3300.
Trabajos #7 (investigación/ARC), #27 (materiales), #36 (núcleo PC) y #39
(lector) revisados. Cambios aislados en esta carpeta y su workflow.
Sin modificar sus ramas, monitor, banco privado ni PS Vita.

Bloqueo previo de Windows Control de aplicaciones resuelto por el usuario.
Compilación MSVC x64 C++17 /W4 /WX y suite local de 48 pruebas correctas.
Incluye 512 truncaciones, corrupción por nivel IVFC, padding, hashes ExeFS
invertidos, cobertura NCCH, ciclos, padres, Unicode, colisiones válidas,
bucket incorrecto, enlaces compartidos y entradas ausentes.

Sobre la imagen privada del usuario: seis hashes NCCH, tres archivos ExeFS,
673.229 bloques IVFC y los dos índices de cada una de las tres particiones
correctos. Directorios/archivos: [153,11445], [1,1], [1,66].
Referencia Python independiente reproduce hashes, recuentos y estadísticas
de buckets. El SHA-256 completo sigue idéntico. Listados privados fuera de Git.

CI ba8677f (38 pruebas, antes de los índices): cuatro trabajos correctos,
Windows/Linux x Debug/Release, Linux Debug con ASan/UBSan:
https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39864443114
La CI de los índices debe identificarse separadamente por su commit.

## Límites y fuentes

Sin claves, descifrado, extracción, reparación ni recursos comerciales en Git.
No se verifican firmas RSA, autenticidad o procedencia; la consistencia interna
no las certifica. No interpreta modelos, texturas, animaciones o lógica MH4U.

Fuentes y búsqueda en plataformas: RESEARCH.md. Implementación propia basada
en el formato; no se copiaron implementaciones ni se añadieron dependencias de
CTRTool, GodMode9, libctru o REA.

## Firmas embebidas y recursos MH4U

    stt-inspect imagen.cci --inspect-signatures
    stt-inspect imagen.cci --inspect-resources --inspect-signatures

--inspect-signatures comprueba únicamente la firma RSA-2048/PKCS#1 v1.5 SHA-256
de la cabecera CXI (bytes 0x100..0x1ff), usando el módulo público embebido en su
AccessDesc y el perfil de exponente 65537. No incorpora ni exporta claves.
Resultado valid_with_embedded_key significa coherencia matemática con ese módulo
no confiado, no autenticidad. invalid_with_embedded_key informa discrepancia.
CFA, exheader cifrado o módulo no admitido se marcan explícitamente sin comprobar.
No se verifican firmas NCSD/AccessDesc ni cadena de confianza; se informa
not_checked_no_trust_anchor. El retorno 0 sigue significando inspección realizada,
también si el estado de una firma es invalid_with_embedded_key.

Windows usa BCrypt RSA y Linux OpenSSL BIGNUM para la operación pública y
comprobación completa de la codificación PKCS#1. Las pruebas generan pares RSA
sintéticos efímeros en memoria; no hay claves de prueba persistidas ni se firman
datos comerciales.

--inspect-resources incluye --verify-romfs-index y examina por magic los archivos
RomFS en claro. ARC v19: cabecera de 12 bytes, tabla de registros de 80 bytes,
tipo declarado y rangos de cargas comprimidas, sin solapamientos o datos fuera
del archivo. No descomprime ni verifica las cargas zlib. Presupuesto: 32.768
entradas por ARC, 2.000.000 en total por partición y 4.096 tipos distintos.
ARC de otra versión se identifica como no soportado, sin reinterpretarlo.

TEX A5: valida la cabecera de 16 bytes y campos no nulos de dimensiones/mips/
texturas; no valida offsets de píxeles, niveles o datos, ni convierte imágenes.
Los códigos de tipo de ARC se reportan sin confirmar su semántica. No se leen
modelos o animaciones dentro de las cargas comprimidas.

La imagen privada contiene 10.592 ARC19, 112.427 entradas y 150 cabeceras TEX A5
en la partición principal; tablas y rangos dentro del alcance comprobados.
La firma de su cabecera principal no coincide con el módulo embebido; la
referencia Python independiente confirma ese resultado. No se atribuye una causa
ni se certifica autenticidad. Los hashes internos de la imagen siguen coherentes.

Esta ampliación no modifica el extractor ARC17/MHXX de PR #7.
La versión y los resultados de ARC19/MH4U se mantienen separados.
Suite local ampliada a 60 pruebas, con RSA efímero válido/alterado/fuera de módulo,
perfiles omitidos, ARC19 fuera de rango/truncado y TEX inválido/truncado.
Fuentes y límites de estas comprobaciones: RESEARCH.md.

## Validación zlib ARC19 en memoria

    stt-inspect imagen.cci --validate-arc-zlib --inspect-signatures

Incluye --inspect-resources y sus verificaciones de integridad e índices.
Para cada entrada ARC19 valida un único flujo zlib completo, checksum Adler-32
incluido, sin diccionario externo. Exige tamaño de salida exacto (bits 0..27 del
campo de tamaño ARC19), consumo de todos los bytes comprimidos declarados y
ausencia de datos sobrantes o segundo flujo. No admite DEFLATE crudo/gzip.

No exporta las cargas: usa dos buffers de 64 KiB y conserva un prefijo de
16 bytes para clasificar magics MOD/TEX/MRL/LMT/ARC y el campo crudo de versión
de 16 bits. No recorre archivos anidados ni interpreta la estructura completa.
En TEX ese campo incluye bits adicionales: su versión de formato es bits 0..11.

Límites: 64 MiB de entrada/salida por carga, 8 GiB de entrada y 8 GiB de salida
acumuladas por partición, 4.096 categorías de cabecera. Rechaza falta de progreso,
exceso del tamaño declarado, truncamientos, checksum inválido y diccionarios.
Otras versiones ARC siguen marcadas como no soportadas, sin descompresión.
El límite de memoria de los buffers no incluye el estado interno de zlib ni
las tablas de metadatos ya documentadas.

Dependencia externa: zlib 1.3.2, descargada por CMake desde el archivo oficial
https://zlib.net/fossils/zlib-1.3.2.tar.gz
SHA-256: bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16.
Se compila estáticamente en todas las plataformas; la primera configuración
necesita red. C y C++17 son requisitos de compilación. No se instala zlib global.
Linux Debug instrumenta el lector y zlib con ASan/UBSan.
Créditos y licencia: THIRD_PARTY_NOTICES.md.

Suite local ampliada a 68 pruebas. Incluye bloques múltiples de entrada/salida,
salida vacía, checksum corrupto, truncamiento, datos finales, flujos concatenados,
DEFLATE crudo, diccionario, tamaño incorrecto y exceso de expansión.

Resultado privado: 112.427 flujos válidos, 1.243.496.720 bytes comprimidos y
2.157.656.686 descomprimidos. Cabeceras identificadas:
MOD230 10.472, MRL32 13.341, LMT67 1.466 y TEX versión baja A5 38.170;
48.978 prefijos quedan como otros. Referencia Python independiente coincide
en cantidades, categorías y SHA-256 completo. No son modelos/animaciones/
texturas convertidos. La discrepancia de firma de cabecera sigue presente
y la autenticidad continúa sin establecerse.

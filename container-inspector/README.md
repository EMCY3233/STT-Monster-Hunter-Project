# Lector C++17 NCSD/NCCH de solo lectura

Inspecciona .3DS/.CCI NCSD con hasta ocho particiones NCCH y NCCH independientes.
La extensión no determina el formato. No ejecuta MH4U ni modifica la imagen.

## Compilar

    cmake -S container-inspector -B build/inspector
    cmake --build build/inspector --config Release
    ctest --test-dir build/inspector -C Release --output-on-failure

Windows usa BCrypt del SDK; Linux requiere OpenSSL de desarrollo. zlib 1.3.2
se descarga y compila estáticamente por CMake: la primera configuración necesita
red, compiladores C/C++17 y una versión de CMake compatible con esa dependencia.
No se instala zlib globalmente. Archivo oficial fijado:
https://zlib.net/fossils/zlib-1.3.2.tar.gz
SHA256: bb329a0a2cd0274d05519d61c667c062e06990d72e125ee2dfa8de64f0119d16.
Licencia: THIRD_PARTY_NOTICES.md. Linux puede activar ASan/UBSan en lector y
zlib con -DSTT_SANITIZERS=ON, sin recuperación de errores de sanitizador.

## Modos y estados

    stt-inspect imagen.cci
    stt-inspect imagen.cci --verify
    stt-inspect imagen.cci --verify-integrity --list-romfs
    stt-inspect imagen.cci --verify-romfs-index
    stt-inspect imagen.cci --inspect-signatures
    stt-inspect imagen.cci --validate-arc-zlib --inspect-signatures

| Opción | Comprobaciones |
|---|---|
| Básico | NCSD/NCCH, particiones/regiones/flags, hashes almacenados y SHA256 del archivo |
| --verify | Hashes NCCH de logo, exheader y superblocks declarados en claro |
| --verify-integrity | Incluye --verify; hashes de archivos ExeFS y todos los bloques/padding IVFC |
| --verify-romfs-index | Incluye integridad; índices hash de directorios/archivos RomFS completos |
| --list-romfs | Árbol, rutas, tamaños y offsets; no implica verificación IVFC por sí solo |
| --inspect-signatures | Contraste de firma CXI con módulo público embebido no confiado |
| --inspect-resources | Incluye índices/integridad; metadatos ARC19 y cabeceras TEX A5 directas |
| --validate-arc-zlib | Incluye recursos; un flujo zlib completo y acotado por entrada ARC19 |

Informe a stdout, errores a stderr. Retornos: 0 inspección aceptada,
1 inválido/no soportado/lectura/hash discordante, 2 argumentos incorrectos.
Un fallo descarta el informe parcial. **0 no certifica autenticidad**: una firma
invalid_with_embedded_key se informa sin hacer fallar la inspección. Las regiones
declaradas cifradas se omiten explícitamente. Una región presente con rango de
hash vacío se marca not_verified_empty_hash_range, no verificada.

El programa solo abre un ifstream binario, no crea archivos ni exporta claves.
Una redirección del intérprete puede escribir: nunca dirigir stdout a la entrada.
La entrada debe permanecer estable; no se ofrece instantánea atómica frente a
escrituras de otros procesos. NoCrypto y demás flags son declaraciones del
archivo, no prueba independiente de que su contenido esté en claro.

## Validaciones estructurales y presupuestos

- Campos little endian, offsets/tamaños uint64_t, límites contra contenedores y
  archivo; pares offset/tamaño y ausencia de solapamientos de regiones/particiones.
  Se admite cola NCSD recortada si todas las particiones declaradas están presentes.
- Exheader ausente o 0x400 bytes más AccessDesc de 0x400; exponentes de unidad
  hasta 22. Solo particiones NCCH: sin NAND, Switch/save ni particiones truncadas.
- ExeFS: diez registros, nombres/padding/duplicados/rangos/solapamientos; datos
  relativos al final de la cabecera de 512 bytes, hashes en orden inverso.
- IVFC 0x10000: niveles lógicos secuenciales; orden físico 3DS cabecera/master,
  nivel3, nivel1, nivel2; límites, alineaciones, capacidad de tablas padre y
  hashes de bloques completos con padding. Exige cobertura NCCH de cabecera
  ExeFS y cabecera/master IVFC. Bloques de 512 bytes a 1 MiB, hasta 8.000.000.
- RomFS: tablas/registros completos, enlaces a límites de registros, ciclos,
  padres, nombres únicos, alcance de nodos y rangos de datos. Hasta 64 MiB de
  metadatos, 100.000 registros por tabla, profundidad 128, nombres de 1024 bytes
  y rutas de 8192 caracteres. Hasta 32 MiB de rutas pendientes y 32 MiB de
  presupuesto de informe de archivos por RomFS. UTF16 se representa como ASCII
  y escapes de unidades Unicode; no se normaliza ni usa para escribir archivos.
- Índices RomFS: hash sobre padre y unidades UTF16 originales; todos los registros
  exactamente una vez en su bucket correcto. Detecta ciclos, enlaces compartidos,
  ausencias y offsets interiores. Hasta 4 MiB por tabla de buckets; sin imponer
  primalidad ni orden de colisiones. No muestra rutas RomFS salvo --list-romfs.

## Firma: coherencia matemática frente a confianza

--inspect-signatures comprueba RSA2048/PKCS#1 v1.5 SHA256 de la cabecera CXI
(bytes 0x100..0x1ff) con el módulo ya embebido en su AccessDesc y exponente de
perfil 65537. valid_with_embedded_key significa coherencia matemática con ese
módulo, **no confianza en el emisor**. invalid_with_embedded_key significa que
no coincide. CFA, exheader cifrado o módulo no admitido se omiten explícitamente.
NCSD/AccessDesc y cadena de confianza no se verifican: no hay raíz externa
confiable incorporada. Windows usa BCrypt; Linux BIGNUM y contraste completo de
la codificación PKCS#1. Las pruebas generan pares efímeros en memoria, sin
persistir claves ni firmar datos comerciales.

## Recursos y zlib: no equivalen a conversión

ARC19: cabecera de 12 bytes y registros de 80; códigos de tipo declarados,
rangos de cargas y ausencia de solapamientos. Hasta 32.768 entradas por ARC,
2.000.000 por partición y 4.096 tipos distintos. Otras versiones se indican
como no soportadas. --inspect-resources por sí solo no descomprime cargas.
TEX A5 directo: cabecera de 16 bytes y dimensiones/mips/texturas no nulos;
no comprueba offsets de píxeles ni convierte imágenes.

--validate-arc-zlib exige un único flujo zlib completo por entrada, Adler32,
fin de flujo, tamaño de salida exacto (bits 0..27 del tamaño ARC19) y consumo
exacto de todos los bytes comprimidos. Rechaza diccionario externo, colas,
concatenación, DEFLATE crudo, gzip, truncamientos y falta de progreso.
Usa dos buffers de 64 KiB más el estado interno de zlib; conserva solo un
prefijo de 16 bytes para clasificar magic y campo crudo de versión de 16 bits.
En TEX la versión es solo sus 12 bits bajos. No recorre archivos anidados ni
valida semántica MOD/MRL/LMT/TEX. Hasta 64 MiB de entrada/salida por carga,
8 GiB de entrada y 8 GiB de salida por partición y 4.096 categorías.

## Evidencia comprobada

Código funcional: 3f54f8e286e5caccb5e25bf2ac43f52edc21f172, 68 métodos de
prueba sintética. Incluye 512 truncaciones, integridad/índices RomFS, RSA
efimero, recursos y rechazo de flujos zlib malformados. CI de ese código:
https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39867677074
Windows/Linux x Debug/Release; Linux Debug con ASan/UBSan en lector y zlib.
Los recuentos 38/48/60 de etapas anteriores quedan sustituidos por 68.

Imagen privada: seis hashes NCCH presentes, tres archivos ExeFS, 673.229 bloques
IVFC y ambos índices de las tres particiones coherentes. Directorios/archivos:
[153,11445], [1,1], [1,66]. 10.592 ARC19 y 112.427 flujos zlib válidos;
1.243.496.720 bytes comprimidos, 2.157.656.686 descomprimidos en memoria.
Prefijos: MOD230 10.472, MRL32 13.341, LMT67 1.466, TEX A5 bajo 38.170;
48.978 otros. Además, 150 cabeceras TEX directas. No son recursos convertidos.

Control Python separado reproduce hashes/recuentos/índices y clasificación;
para DEFLATE usa la misma familia zlib, no un segundo algoritmo independiente.
SHA256 original sin cambios. La firma principal no coincide con el módulo
embebido, también según la operación pública Python. Sin causa establecida ni
autenticidad acreditada; hashes internos correctos no resuelven esa discrepancia.
Informes/listados/datos privados permanecen fuera de Git.

## Coordinación y límites

AGENTS.md leído; base main f199bd07b4e05ee4f7e56ed616840518374f3300. Revisados
#7 (ARC17/A6/MHXX), #27 (materiales) y #36 (núcleo PC). Este lector ARC19/MH4U
se mantiene separado de aquellas ramas y del decodificador TEX A5 en PR #40.
La PR #40 sí convierte un subconjunto de texturas; no cambia el alcance de
este ejecutable. No hay descifrado, reparación, extracción a disco, recursos
comerciales o claves incorporadas. Sin cambios a monitor, banco privado o Vita.
Sin geometría, materiales enlazados, animación o juego ejecutable en PC.
Fuentes y procedencia: RESEARCH.md; dependencia zlib: THIRD_PARTY_NOTICES.md.

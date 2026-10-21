# Modelos y animaciones localizados — 2026-10-21

## Resultado verificado
Se inspeccionaron las tablas de los 1228 ARC del RomFS del parche MHXX 3DS: 21696 entradas, sin errores de tabla. Se descomprimieron las 83 entradas identificadas como MOD y las 4 LMT, comprobando tamaño y firma. Esto NO significa haber descomprimido ni validado las 21696 entradas.

Se conservaron seis muestras locales de `arc/village/common.arc`: dos MOD y cuatro LMT. Los archivos comerciales permanecen fuera de los repositorios. El JSON adjunto contiene exclusivamente metadatos, hashes y observaciones de cabeceras.

| Entrada | Ruta interna | Formato | Bytes | Observación |
|---|---|---|---:|---|
| 39 | npc/mod/npc009/npc009 | MOD 230 | 65102 | Declara 14 huesos, 2 mallas |
| 82 | npc/mod/npc010/npc010 | MOD 230 | 27622 | Declara 14 huesos, 2 mallas |
| 84 | npc/mot/com_0 | LMT 67 | 247504 | 144 slots; 46 no vacíos |
| 85 | npc/mot/par_0 | LMT 67 | 99304 | 73 slots; 35 no vacíos |
| 86 | npc/mot/lpet_p_s | LMT 67 | 2516 | 2 slots; 1 no vacío |
| 87 | npc/mot/lpet_y_s | LMT 67 | 2124 | 2 slots; 1 no vacío |

Las 83 entradas no vacías tienen tabla y cabeceras de bloque dentro del archivo bajo la interpretación de punteros de 32 bits little-endian. No se ha validado el contenido completo de pistas, sus codecs, geometría, asociación al esqueleto ni reproducción. No se conoce el FPS: los campos de frames no permiten deducir duración en segundos.

## Procedencia y repetibilidad
Original: `MHXX_MHGU_English_Patch_v2.cia`, SHA-256 `8438c0c026203c20b9dd81fc3b6ec9c31c94abc80e5bb7f6618cd58f804ac4ac`.
NCCH extraído: SHA-256 `1ed304a0d11d01ed66cdfeebefb140a072b1b20728f8c611c13ebab75a8be473`.
ARC common: SHA-256 `8694d2381e6c2e4b892831ca36c744d0ba6da9d5b2ce18e6376263659d9910c1`.
Se verificó el hash del ARC antes de extraer y el de cada muestra tras escribirla con creación exclusiva. Los hashes individuales están en [metadatos](located-resources-metadata.json).
La extracción y las lecturas se hicieron sobre derivados locales, sin escribir los originales.

Herramientas propias: [lector ARC](../../../tools/probe_arc.py), [lector limitado de cabeceras](../../../tools/probe_resource_headers.py).
Diez pruebas sintéticas del segundo lector pasaron: versión, truncamiento, offsets de bloques, punteros de pistas y límites de conteos. Son pruebas de aceptación del lector, no pruebas visuales de los recursos.

## Fuentes primarias para interpretar estructuras
- [RevilLib: cabecera MOD](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/header.hpp).
- [RevilLib: serialización LMT](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/serialize.cpp).
- [RevilLib: bloques de animación](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/animation.inl).
- [Arc Explorer: diccionario de tipos](https://github.com/Paxlord/pax_arc_explorer/blob/main/data/dti_ext.json).

Se consultaron las estructuras publicadas; no se ejecutó RevilLib ni se copió su implementación. REA se utilizó como criterio de evidencia y aceptación de la skill de catálogo, no como herramienta de descifrado.

## Interfaces de coordinación y pendientes
- Área 02: aceptar identificadores estables (SHA-256 del contenedor, índice, SHA-256 de salida), versión explícita y estado de validación. No ejecutar código de juego.
- Área 04: estos recursos tienen rutas NPC de MHXX; no atribuirlos al cazador, Espada Larga ni Frontier. Catálogo y fusión de Frontier siguen requiriendo evidencia independiente.
- Área 07: siguiente aceptación: decodificar una pista y geometría, comprobar jerarquía y correspondencia de huesos y producir una vista previa local. No iniciar adaptación de recursos comerciales sin activos legales.
- Continúan pendientes los contenidos cifrados de las CIA base de MH3U, MH4U y MHXX. El éxito del parche no demuestra acceso a esas bases.
- No se instaló ni transfirió nada a PS Vita; no se usó FTP.

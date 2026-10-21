# Fuentes y compatibilidad

Consultadas el 21-10-2026. D = documentación/afirmación del autor, sin prueba propia del software sobre estos juegos. L/E = lectura/estructura local descrita en el informe. No se incorporó código externo ni se descargaron juegos. Las ramas `main/master` enlazadas pueden cambiar: fijar commit y revisar licencia antes de adoptar una herramienta. Los hashes de las herramientas propias entregadas se registran en SHA256SUMS.txt.

| Fuente primaria | Aportación y límite |
|---|---|
| [Arc Explorer](https://github.com/Paxlord/pax_arc_explorer) | D: anuncia MH3U 3DS/Wii U, MH4U, XX 3DS y GU Switch. En STT solo el lector propio ARC LE v17 se volvió a ejecutar. No usar ArcC/cifrado. |
| [Diccionario DTI](https://github.com/Paxlord/pax_arc_explorer/blob/main/data/dti_ext.json) | D: asociación type_id/extensión. El cruce local genera conteos; no prueba semántica. SHA de blob consultado registrado en provenance.json. |
| [RevilLib](https://github.com/PredatorCZ/RevilLib) | D: biblioteca MT Framework, modelos, motionlists y otros formatos; GPLv3. Referencia para futura compatibilidad por versión, no importador ejecutado aquí. |
| [Cabecera MOD](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/header.hpp) | Referencia estructural del lector limitado independiente MOD230. Sin validación de geometría/pesos. |
| [Serialización LMT](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/serialize.cpp) | Referencia de versiones y tabla. Sin acreditación de FPS ni codecs por leer cabeceras. |
| [Bloques LMT](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/animation.inl) | Referencia previamente consultada por el lector local; en esta revisión se reabrieron README y serialize.cpp. |
| [Kuriimu2](https://github.com/FanTranslatorsInternational/Kuriimu2) | D: toolkit de traducción/modificación con plugins; comprobar formato y revisión, sin asumir soporte universal. |
| [SaladSoftware](https://github.com/RTHKKona/SaladSoftware) | D: ARC específico de MHGU; no garantiza XX 3DS. No ejecutado. |
| [SoupTextures](https://github.com/RTHKKona/SoupTextures) | D: TEX de MHGU; comprobar variante de textura antes de uso con 3DS. |
| [gmd](https://github.com/beeequeue/gmd) | D: parser/serializador de GMD de MT Framework; falta ensayo con revisión local. |
| [MHGUQuestEditor](https://github.com/Fexty12573/MHGUQuestEditor) | D: GU/XX Switch; documenta EXT/MIB, GMD, REM, ESL, SEM, SUP y QPL. No certifica los tipos MHXX 3DS locales. |
| [mhxqe](https://github.com/svanheulen/mhxqe) | D: editor de misiones MHX; versión distinta. No usarlo como soporte demostrado de XX/4U. |
| [mhtools](https://github.com/codestation/mhtools) | D: DATA.BIN, textos, gráficos y misiones PSP; GPLv3. Incluye operaciones de cifrado: no instalado ni ejecutado; soporte exacto ULES01213 pendiente. |
| [MH-Pointers-Tool](https://github.com/amaillo/MH-Pointers-Tool) | D: texto/punteros y MIB/BIN legibles, declara MHFU US/EU. No es editor de lógica de misión. |
| [PRXTool](https://github.com/pspdev/prxtool) | D: manipulación/desensamblado PRX y salida ELF/IDC; AFL2.0. ~PSP no implica entrada legible. BOOT ELF requiere próximo ensayo. |
| [Ghidra](https://github.com/NationalSecurityAgency/ghidra) | Candidato de análisis estático citado por el plan previo; no instalado/probado en este encargo. Validar loader/CPU/ABI. |
| [CTRTool](https://github.com/3DSGuy/Project_CTR/blob/master/ctrtool/README.md) | D y evidencia local anterior: inspección de CIA/NCCH/ExeFS/RomFS. Esta revisión usa parser propio para ExeFS ya plaintext; sin claves. |
| [7-Zip](https://www.7-zip.org/7z.html) | Referencia de formato del inventario previo; prueba de payload con 7zr consta en PR3, sin repetición nueva aquí. |
| [hactool](https://github.com/SciresM/hactool) | D: formatos Switch, incluido NCA; referencia de plataforma, sin instalar/ejecutar ni usar claves/descifrado. No hay datos Switch locales. |
| [Vita toolchain](https://github.com/vitasdk/vita-toolchain) | D: ELF, VELF, SELF y FSELF. Herramientas de construcción host, no convertidor automático de PSP/3DS/Switch a Vita. |
| [Frontier Blender add-on](https://github.com/Houmgaor/MHFrontier-blender-addon) | D: FMOD/FSKL, MOT y escenarios; GPLv3. Compatibilidad Vita Z/ZZ no ensayada. No se transfirió/instaló plugin. |
| [ReFrontier](https://github.com/Houmgaor/ReFrontier) | D: toolkit, BIN y compresión/formatos de Frontier. Incluye ECD/EXF y automatismos fuera de alcance; no se ejecutó. La licencia de cambios MIT no sustituye revisión del código original. |
| [FrontierDataTool](https://github.com/Houmgaor/ReFrontier/blob/master/FrontierDataTool/README.md) | D: tablas de armas/armaduras/misiones; perfil zz documentado para PC. Offsets no transferibles sin prueba a Vita. |
| [FrontierTextHandler](https://github.com/Houmgaor/FrontierTextHandler/blob/main/README.md) | D: texto/punteros, CP932, BIN; maneja automáticamente capas cifradas/comprimidas. No ejecutado bajo este encargo. |
| [Frontier Patterns](https://github.com/var-username/Monster-Hunter-Frontier-Patterns) | D: documentación mediante patrones ImHex; útil para estructura, sin prueba de Vita ni IA cliente completa. |
| [Erupe](https://github.com/Mezeporta/Erupe) | D: servidor abierto, declara múltiples versiones y plataformas, incluida Vita. No prueba equivalencia de recursos ni comportamiento completo del cliente; no desplegado. |
| [Capcom soporte Vita Frontier](https://www.capcom.co.jp/support/faq/platform_psv_mhf-g_0033506.html) | Fuente oficial que identifica el producto Vita; no es documentación binaria de Z/ZZ. |
| [vgmstream](https://github.com/vgmstream/vgmstream) y [formatos](https://github.com/vgmstream/vgmstream/blob/master/doc/FORMATS.md) | D: decoder de audio; incluye familias CWAV/FWAV y muchas variantes. Una extensión no garantiza codec compatible; no se reprodujo audio local. |
| [MH4UltimateDC](https://github.com/CompaLarios18/MH4UltimateDC) | D: recompilación estática de MH4U; objetivo documentado USA 1.3.0 frente a entrada local EUR. No compilado ni validado por STT. |
| [mh4u-decomp](https://github.com/mhvuze/mh4u-decomp) | D: seguimiento de decompilación matching EU1.1; no equivale a fuente completa utilizable aquí. |
| [mhp2g-decomp](https://github.com/tclamb/mhp2g-decomp) | D: decompilación byte-matching de Portable 2nd G; objetivo distinto a Freedom Unite ULES01213. |
| [mh3u-port](https://github.com/glinesbdev/mh3u-port) | D: recompilación Wii U USA para Windows/Linux; plataforma distinta al CIA local y a Vita. No probado. |
| [mh3u-arc-tool](https://github.com/Matt-Wood-23/mh3u-arc-tool) | D: ARC Wii U big-endian v16; sus reglas de tamaño no se deben trasladar al ARC 3DS LE v17. No ejecutado. |

Se buscaron además combinaciones de cada juego con formatos, animación, hitbox, colisión, misiones, herramientas y Vita. No se verificó decompilación pública completa de MHXX/MHGU ni una herramienta que reconstruya universalmente todos sus sistemas. Eso describe las fuentes revisadas, no prueba inexistencia.

Fallos de acceso: las URL inicialmente supuestas `FistOfHit/ReFrontier`, `PredatorCZ/RevilTool` y `vita-toolchain/vita-toolchain` no devolvieron contenido utilizable. Se sustituyeron por los proyectos de autores arriba enlazados. No se usaron esos fallos como evidencia técnica.

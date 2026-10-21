# Copia local de Frontier desde PS Vita — 2026-10-21

## Estado de esta publicación
**Transferencia terminada e incorporada al banco.** Se comprobaron completed=true,phase=complete y el recibo de registro. Véase [cierre y censo completo](frontier-complete.md). Este documento conserva el plan y método de transferencia.

El usuario autorizó expresamente copiar desde su Vita el juego instalado en ux0 y añadirlo al banco. Esta autorización amplía para esta tarea la condición anterior de no usar FTP; no autoriza instalación ni escritura en la consola.

## Identificación leída
Se estableció conexión con un servidor que responde FTPVita y se leyó:
- Ruta: ux0:/app/PCSG00350/sce_sys/param.sfo.
- TITLE_ID: PCSG00350.
- TITLE: モンスターハンター フロンティアＧ (Monster Hunter Frontier G).
- APP_VER y VERSION: 01.00.
- CATEGORY: gd.

Esto identifica la aplicación base. No confirma por sí solo que el conjunto instalado corresponda a Frontier Z/ZZ. La lectura posterior completa confirma TITLE Frontier Z y APP_VER01.99 en el parche; no acredita ZZ.

## Plan realmente enumerado
| Carpeta del título | Archivos enumerados |
|---|---:|
| ux0:/app/PCSG00350 | 4493 |
| ux0:/patch/PCSG00350 | 3666 |
| ux0:/rePatch/PCSG00350 | 103 |
| ux0:/addcont/PCSG00350 | No accesible: respuesta 550 |

Se seleccionaron 8261 archivos, 5212490427 bytes. Una licencia work.bin quedó excluida. No se copian partidas, licencias ni aplicaciones ajenas.

## Copia y comprobación
Destino local: Juegos/MHF-Vita/PCSG00350/, conservando separadas app, patch y rePatch.
Operaciones FTP de lectura; no se envían comandos de escritura, instalación o ejecución. Fuente técnica del servidor: [VitaShell](https://github.com/TheOfficialFloW/VitaShell).

Cada archivo se descarga a un temporal local nuevo; se compara tamaño con LIST y SHA-256 del flujo con una nueva lectura local antes de confirmar el archivo. El servidor no proporciona aquí un hash remoto independiente: no presentar esta comparación como hash calculado en la Vita.

La copia de archivos no establece descifrado ni análisis semántico. La cabecera del eboot.bin copiado no permite declararlo ELF ni ejecutable descifrado. No se ejecuta.

## Seguimiento y cierre locales
- analysis-local/logs/vita-copy-PCSG00350.json: plan y recibos por archivo.
- analysis-local/logs/vita-bank-status.json: progreso de copia y posterior registro.
- analysis-local/finish_vita_copy.py: espera a copia completa y entonces ejecuta la validación e incorporación al banco.
- analysis-local/register_vita_bank.py: coteja todos los archivos con el recibo, respalda el catálogo, añade registros transaccionalmente y actualiza el manifiesto.
- analysis-local/resource-bank/vita-registration.json: resultado y hashes finales del catálogo, solo tras incorporación.

Si falla la copia, el registro completo no se ejecuta. El recibo y los archivos parciales permiten diagnosticar el fallo; no atribuir éxito a una transferencia pendiente. Mantener VitaShell y FTP activos durante el proceso.

Los contenidos comerciales, licencias y recibos detallados permanecen fuera de GitHub. No se busca relación con armas ni se adaptan recursos.

# B — STT Asset Lab PC 0.1

Rama independiente desde main `410b1dd70a3713b500a829aed55cb99cb74ad1d0`.
Responsabilidad: `asset-lab/`, este documento y CI `.github/workflows/asset-lab.yml`.
No modifica ramas PR3/PR7 ni el monitor. Prototipo B no depende de A/C para abrir sus muestras.

## Ejecución y arquitectura

Desde `asset-lab/`: `python -m stt_asset_lab samples/practice-dummy.stt.json`.
Python 3.11+ con Tk/Tcl para GUI; sin dependencias pip. `--validate` funciona sin pantalla.
`README.md` de esa carpeta contiene controles, contrato completo, límites y exportación.

`model.py`: parser acotado, validador, exportador y evaluación de jerarquía/clip.
`viewer.py`: Canvas Tk con malla ortográfica, huesos, árbol, cámara orbital y reproducción.
`generate_sample.py`: geometría y clips originales reproducibles. `package.py`: ZIP determinista
sin binarios de terceros ni dependencias descargadas. Sin lectores de formatos comerciales.
Contrato STT Asset/1 desacoplado: metros, +Y arriba, rotación local Z en radianes; adaptación
al motor en milímetros queda explícitamente pendiente, no hay binding automático.

## Evidencia local, 21-10-2026

- `python -m unittest discover -s asset-lab/tests -v`: **23/23 PASS** en Linux / Python 3.12.14.
- `python -m compileall -q asset-lab/stt_asset_lab`: PASS.
- CLI real de validación ejecutada en subprocess, salida JSON contrastada; rechazo malformado
  devuelve código 2. Regeneración de muestra cotejada por igualdad estructural.
- Proyección y esqueleto: 242 poses × 3 orientaciones de cámara con coordenadas finitas
  y dentro de viewport 800×600 para la muestra inicial; distancias ortográficas contrastadas.
  Son pruebas numéricas, no revisión visual. 10.000 entradas JSON aleatorias malformadas
  rechazadas sin excepciones no controladas en ensayo adicional determinista.
- GUI: implementación presente, **sin prueba visual**; entorno sin DISPLAY/Xvfb.
- CI Windows/Linux declarada en workflow separado; resultado remoto debe verificarse por commit.
- Sin recepción de telemetría, compilación Vita, transferencia FTP ni confirmación física.

Paquete fuente ejecutable generado por `python asset-lab/package.py`:

| Archivo | SHA-256 |
|---|---|
| `stt-asset-lab-0.1.zip` | `916638957260b3a7eea59581fcde8b83d539706faf294958d4a4360c8928fe99` |
| `samples/practice-dummy.stt.json` | `6065aec43ff7ba2072b08a07ff9ea6479cd19a07803ad29ee3533ae4fd7a4800` |

ZIP y SHA256SUMS se generan en `asset-lab/dist/`, ignorado por Git; CI los publica como
artefactos de retención limitada. Hash corresponde al código de esta entrega; regenerarlo
si cambia cualquiera de sus fuentes. El ZIP contiene Python original y muestra original,
no EXE ni instalador. Pendientes: comprobación visual en PC del usuario; más grados de libertad
para animación y formatos de intercambio solo si se validan en encargos posteriores.

Coordinación: orden STT — Prototipos iniciales Vita, A = motor independiente, C = Combat Lab;
las PR se enlazan en su descripción cuando existan. Las investigaciones PR3 y PR7 son contexto,
no dependencias de datos de este inspector.

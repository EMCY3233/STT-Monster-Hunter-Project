# STT Vita Prototype 0.1 — original playable slice

Independent application **STTP00001**, title `STT Vita Prototype`, APP_VER `00.10`.
Main's monitor uses **STTM00001**: this package must never replace that title.
No commercial models, animation clips, decoders or game data are used. This is a
new experimental scene and combat, with no claim of fidelity to Monster Hunter.

## Build and launch

From this branch's repository root:

```sh
# Inside the exact VitaSDK image below (VITASDK supplied by the image):
cmake -S vita-prototype -B build/prototype
cmake --build build/prototype --parallel 2
sha256sum build/prototype/stt_vita_prototype.vpk > build/prototype/SHA256SUMS
# On PC, before copying/installing:
python vita-prototype/tests/inspect_package.py build/prototype
```

Pinned build environment:
`vitasdk/vitasdk:2026.08-20260815@sha256:7f5eee50ff95b73c8c847dbfef6227aa0035886444b4d0254c21da8369ff1efc`.
No dependency download at configure time; SDK libc/libm and SDK stub libraries only.
The fixed container fixes the compiler/tools; byte-for-byte VPK reproducibility
across runs is not asserted (packaging timestamps may differ). CI uploads the VPK
and its SHA-256 receipt, then independently checks the receipt, ZIP bounds,
SELF signature and **parsed SFO application identity**. No VPK hash is fabricated
before that build exists. See the PR CI links for actual results/artifact SHA.

| Control | Action |
| --- | --- |
| Left stick | Camera-relative ground movement, 3 m/s, radial normalization |
| Right stick | Third-person orbit yaw and pitch; pitch clamped 0.12–1.05 rad |
| Cross | Attack; release and press again in the last 8 recovery ticks to chain |
| Triangle | Reset target/player/camera and start a new telemetry session |
| START | Clean application exit |

The floor, box character, sword and red box target are project-created geometry.
Target flashes on hit, loses HP and collapses when defeated. Move and rotate the
camera to approach the target; Cross produces the experimental three-stage combo.
There is no save file, asset importer, terrain collision or full animation system.

## Architecture and limits

`control.c` is portable stick/deadzone, camera and frame-step math. The camera
adapter converts meters to integer millimeters and yaw to unsigned turn16 for
[Combat Lab](combat.md), which supplies the exact same shared C source to PC and
Vita. +Y up, +Z forward at yaw zero, yaw positive toward +X. Movement and facing
freeze during attacks according to Combat Lab. The renderer uses libm floats;
only the integer-input combat core is claimed deterministic.

`render.c` is a small CPU perspective triangle rasterizer with reciprocal-depth
buffering. It renders at 480×272, pitch512, to two CDRAM buffers, letting the Vita
scale to its display. VitaSDK `psp2common/display.h` documents 480×272 among accepted
framebuffer dimensions; actual presentation on the user's console is pending.
Near-plane crossing triangles are rejected rather than clipped, so close floor
tiles can disappear. This deliberate first-cut limitation is not a full renderer.

Simulation: 60 Hz (`16667 us`, rounded period). Render cap: 30 FPS / 33333 us.
At most four simulation ticks per frame. Gaps above100ms discard elapsed time
rather than replaying a huge backlog. `dropped` counts gap/over-budget incidents;
combined with mailbox-overwrite count in telemetry; it is not a measurement of GPU frames lost. Frame/update durations are observed
CPU work plus presentation-wait times excluding render-cap sleep, not hardware performance guarantees. Raster work is bounded by fixed
scene tiles/triangles, fixed buffers and arena bounds. 30 FPS remains a target
until physical performance measurement.

Power callback flags and long frame gaps trigger clock accumulator/input resync.
After resume, release both sticks and buttons before gameplay continues; the
screen displays the gate. No attack press is replayed from suspension. An attack
edge on a render frame without simulation ticks stays pending until one tick.
Reset rotates session ID and clears pending input/sampling counters. Initialization
and controls/display errors return failure; when a framebuffer is usable, an
error code is displayed for3s. Cleanup unregisters callback, blanks the display
before freeing framebuffers, releases heap/CDRAM and exits. No firmware, plugins,
mounts, games or network state is changed.

## Telemetry and HUD

Uses [STT/3](contracts.md), retaining STT/1 and STT/2 in the PC receiver. Main offers
a latest-only snapshot every six simulation ticks and on impact; the mailbox has
capacity one and accounts for overwrites. HUD reads the same combat state directly.
**Transport is deliberately disabled in this first VPK.** There are no socket calls,
network requirements or receiver discovery on the frame path. Thus no PC receipt
of Vita samples is claimed. The mailbox is the minimal adapter boundary for a
later bounded nonblocking sender. Events may be overwritten; telemetry cannot
block gameplay or act as an authoritative combat log. Hunter HP is synthetic100
(no damage model); target HP is reported only on hit entries/HUD. Aquatic is null;
there is no swimming implementation.

## Validation evidence and physical handoff

Local PC: strict GCC controls/deadzone/camera/normalization/fixed-step tests passed.
Adapter replay moves500mm, executes a strike, observes exactly one10HP hit, encodes
STT/3 and passes the Python receiver validator with declared source `simulator`.
Renderer exercises16 extreme orbit/pitch combinations with buffer sentinels;
ASan/UBSan passed with leak detection disabled due this environment's `/proc`
restriction. A synthetic PC framebuffer was inspected visually; it is not a Vita
screenshot. Existing Combat Lab and contract tests are separate evidence.

Vita cross-compilation, VPK inspection, actual FPS, controls, suspend/resume,
installation and physical result are distinct gates. Record each with exact commit,
CI run, artifact hash and user observation. This initial document does not assert
a successful cross-build before its CI has completed.

No local/FTP connection to the user's Vita is available in this Work environment.
After CI passes, download artifact `stt-vita-prototype-STTP00001`, verify the VPK
against SHA256SUMS and run the identity inspector. In local VitaShell, copy via the
already-authorized FTP connection to an existing writable data location such as
`ux0:data/STT-Prototypes/stt_vita_prototype.vpk` (create this project folder if needed;
do not change mounts). Verify that `ux0:` is the intended writable mount and there
is sufficient space before copying. Install only when the parsed title is
**STTP00001** and displayed title is **STT Vita Prototype**. Open that bubble and
record movement, camera, target HP, START exit and suspend/resume. Keep the monitor
bubble intact. A transfer receipt must contain source hash, destination and result.
No transfer, installation or hardware test occurred here. Preserve package/evidence;
remove only explicitly identified old project transfer files after verified update.

## Resultado remoto verificado de esta entrega

Código `e6416fb952ea050f3b785c852417e5bc58cd3f88`: [CI39560756730](https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39560756730)
correcto en controles/adapter PC, build Vita y revisión independiente del paquete.
Job119091458348: SFO STTP00001 /STT Vita Prototype /00.10.
VPK51.745 bytes, SHA-256 `e8b0a0bded89881c9a79a035028bec04fbed2bd99e85533abc662a0af993ffa5`.
Descargado y reinspeccionado localmente con igual hash. Primer build fallido por enum
quedó corregido y preservado como evidencia; no se usó un VPK de ese intento.
Entrega, enlaces a las cuatro PR, controles e instalación local: [initial-delivery.md](initial-delivery.md).
No hay transferencia FTP, instalación ni comprobación física desde Work.

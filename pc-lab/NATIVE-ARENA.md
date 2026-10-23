# Original native arena (PC)

This is original procedural C++17/OpenGL 3.3 gameplay, not MH4U execution.
No ROM, textures, models, keys, network service or Vita device is used at runtime.
This branch depends on PR #36 and targets its branch for review; it does not
merge #36 or the separate reader branches into main.

Windows 10 x64 is the minimum Windows target. Compilation or execution on a
newer OS does not establish Windows 10 compatibility. The provisional integrated
GPU/8 GB/720p30 budget has not been benchmarked. Linux is an additional target.

## Build

Use CMake 3.16+, a C++17 compiler and an OpenGL 3.3-capable driver:

```sh
cmake -S pc-lab -B build/native -DSTT_NATIVE_ARENA=ON
cmake --build build/native --config Release
ctest --test-dir build/native -C Release --output-on-failure
```

Native rendering is opt-in; the default console build stays dependency-free.
The native option downloads GLFW 3.4 from its official repository and checks
SHA-256 a133ddc3d3c66143eba9035621db8e0bcf34dba1ee9514a9e23e96afd39fd57a.
For an offline build set `FETCHCONTENT_SOURCE_DIR_GLFW` to a preverified source
directory (CMake's source override bypasses archive download/hash verification).
GLFW is an external dependency under the zlib/libpng license; see
https://www.glfw.org/license.html and the complete notice in
`pc-lab/third-party/GLFW-LICENSE.md`. No global project license is inferred.

Linux needs OpenGL and GLFW platform development packages. CI uses X11 only
(`-DGLFW_BUILD_WAYLAND=OFF`), Mesa software rendering and Xvfb. A display/context
is required for the native smoke test, even though its window is hidden.

Run `build/native/Release/stt_native_arena.exe` on Windows; single-configuration
Linux builds put `stt_native_arena` directly in the build directory.

## Controls and contracts

- WASD moves in fixed world axes; arrows orbit/elevate the following camera.
- Space attacks the red synthetic target; release to rearm. R resets; Esc exits.
- Position uses the existing core's integer millimetres at 60 simulation steps/s.
  Display coordinates convert only these original units at 1000 mm per unit.
  This is not a conversion for imported game models.
- Ground fixes the actor to Y=0. The actor has a 400 mm square horizontal
  footprint; one axis-aligned obstacle has expanded collision bounds. Movement
  slides X then Z, with a final safety check after core diagonal normalization.
  These bounded 35/50 mm steps cannot jump the 1400 mm expanded obstacle.
  There is no gravity, slope, jump, general sweep or dynamic rigid-body system.
- The arena limits actor centres to +/-5000 mm. Camera collision is not present.
- Render timing accumulates integer nanoseconds. A stall contributes at most
  250 ms (15 updates); excess elapsed time is discarded. Unfocused windows pause
  simulation and clear fractional carry. A held attack cannot repeat or queue.
  Live keyboard is sampled per draw and held for its updates; very short taps
  between draws can be missed. Tick-indexed replay is the deterministic contract.

## Verification and limitations

The original core tests remain intact. Arena tests cover clock carry/stall caps,
invalid-input atomicity, obstacle contact/sliding, 100,000 seeded movement steps
and combat replay across different draw schedules.

`--smoke` creates a hidden core context and draws 120 scripted simulation steps.
It checks GL errors, reads the framebuffer for the actor's green pixels and
requires tick 120, x=500 mm, four hits and target HP=0. This is a rendering and
scripted gameplay smoke check, not automated physical-keyboard interaction.
`--smoke --capture NEW.ppm` saves the last framebuffer locally and rejects an
existing destination. No screenshots or binaries are committed.

Windows CI builds both configurations and runs CPU tests, because hosted runners
may not expose OpenGL 3.3. Linux CI also executes the native smoke using Mesa.
Neither establishes actual Windows 10 runtime compatibility, integrated-GPU
performance, animation/material binding or fidelity to original-game behavior.

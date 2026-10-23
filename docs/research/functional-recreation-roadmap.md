# Functional C++ recreation: accepted direction

User selected a functional C++ recreation on 23 October 2026. Target platforms
remain PC Windows/Linux. This is original engine/system development with
verified readers and separately validated behavioral evidence, not a claim of
source-code equivalence or an already working MH4U executable. No Vita work.

Progress is tracked by reproducible milestones, not an unmeasured percentage.
Synthetic correctness, real-input parsing and original-game fidelity are three
different kinds of evidence and must remain labeled separately.

## Current building blocks and integration boundary

- PR #36: original deterministic console core, fixed simulation steps, bounded
  movement and synthetic attack/cooldown target. It is not a native 3D scene and
  its parameters are not verified MH4U rules.
- #39: read-only container/integrity inspection; #40: texture decoding;
  #41: static geometry/material candidates and private browser inspection;
  #42: weighted structure/rest diagnostics and original synthetic simulations.
- This module: partial LMT67 vector-key reading. Rotation, final timeline,
  reference frames, loops and model association remain excluded.

All are separate draft branches. Do not silently merge them, treat a browser
viewer as a native renderer, or treat shared format assumptions as game proof.
Private commercial assets/derived outputs stay outside Git. No keys/decryption.

## Work sequence and acceptance criteria

| Block | Next implementation | Evidence required before integration |
| --- | --- | --- |
| Animation | Rotation codecs; controller timing/reference/loop semantics; ID binding | Known numeric fixtures, malformed-input checks, real-buffer comparisons, unresolved IDs explicit; then a model/animation pair with complete binding |
| Native PC scene | Original scene using the existing deterministic core, native camera/input/render boundary | Windows/Linux build and runtime check, timestep/input replay, original procedural assets before private resource integration |
| Materials | Verified shader roles, UV transforms, sampler/blend behavior | Evidence for each binding; neutral fallback for unresolved material slots |
| Physics | Original ground, obstacle and actor collision contracts | Sweeps/tunneling and boundary tests; no invented conversion between native model units and core millimetres |
| Combat | Extend original state machine and damage/event contracts | Deterministic traces, attack-window and interruption tests; parameters labeled original until compared with observations |
| AI | Original perception/state/action logic under explicit budgets | Deterministic seeded scenarios and invariant checks; no claim of copied original behavior |
| Audio | Inventory signatures/banks, bounded format probe, then playback boundary | Synthetic PCM tests and validated resource/bank links before private data playback |
| Other formats | Resource-type/signature inventory, then prioritized readers | Counts labeled occurrences; each format's ranges and unknown fields explicit; no classification from extension alone |
| Behavioral comparison | Reference captures/traces and explicit comparison cases | Measurable discrepancies; preserve unresolved differences rather than silently tuning to a single screenshot |

The first playable milestone is an original native arena with movement, camera,
ground/obstacle collision and one deterministic combat interaction. Verified
private model/texture/animation integration follows behind complete bindings;
an original synthetic placeholder keeps engine work independent of decoder gaps.

## Platform target

The user requires Windows 10 x64 as the minimum Windows version. Windows 11
compatibility remains a target; Linux remains an additional platform. Actual
Windows 10 runtime compatibility must be tested before it is claimed: a build
on a newer Windows CI runner is not sufficient evidence.

The provisional performance target is integrated graphics of the Intel UHD 620
class, 8 GB RAM, OpenGL 3.3 and 1280 x 720 at 30 FPS, with simulation independent
of rendering at 60 steps per second. This is a development budget pending
measurement, not a demonstrated hardware minimum.

## Decisions still needed before release

Hardware measurements and input priorities are still needed when choosing
and benchmarking the final rendering/input stack. Repository distribution
license and third-party dependency terms must be chosen explicitly; do not infer
a global license or permission to redistribute commercial resources. These do
not block read-only analysis or original local prototypes.

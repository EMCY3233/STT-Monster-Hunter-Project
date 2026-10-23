# LMT67 partial vector-key inspector (C++17)

Standalone read-only first codec increment. Explicit little-endian/32-bit profile,
not architecture autodetection or an animation player. No dependencies on other
PRs or external libraries. Inputs and generated key reports must remain private,
outside Git. No commercial payloads are included in this tool.

```text
cmake -S motion-inspector -B build
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
stt-motion INPUT.lmt --out NEW_PRIVATE_DIRECTORY
```

## Scope

Reads the 8-byte LMT67 header, u32 slot table, 60-byte interpreted animation
prefix and 36-byte track records. The primary class declaration's total size is
64 bytes, but its last four bytes are not fields read by this profile. Real
serialized track tables can start in that tail. Does not claim every animation
object is fully understood or always serialized with size 60.

Checks table ranges/alignment, finite metadata, nonoverlapping interpreted
metadata, and buffer/extreme ranges without overlap with interpreted tables.
Exact table aliases are allowed; payload sharing may count occurrences again.
Events/float pointers are checked only for containment of their first byte;
their contents remain unvalidated. A zero-byte payload is not followed and
produces no keys, even for a supported codec. Header-only/unknown-only reports
are explicitly partial; success does not mean any animation was decoded.

| Codec | Raw key representation | Raw delta |
| --- | --- | --- |
| 1 | 3 little-endian float32, 12 bytes | implicit 1 |
| 3 | 3 float32 + u32, 16 bytes | last u32 |
| 4 | 3 u16 + u16, 8 bytes | last u16 |
| 5 | 3 u8 + u8, 4 bytes | last byte |

Quantized components are divided by 65535 or 255. If an extremes block exists,
all supported vector codecs apply `offset + scale * value`, where scale is the
first vector and offset the second. These fields are **not conventional minimum
and maximum endpoints**. Negative scales are retained. Computation uses double
precision on stored float inputs; not a bit-exact emulation of a source engine.
Other codecs, including rotations, stay opaque and are counted as unsupported.

Each key reports accumulated `frame_before_delta`, then adds its stored delta.
This is raw controller sequencing. Zero deltas are counted, not repaired.
No reference-frame insertion, loop interpretation, channel-to-transform mapping,
seconds conversion, interpolation, quaternion reconstruction or model binding.
In particular, raw key indices are not the final game timeline. Bone ID 255 is
reported as a sentinel; ordinary IDs are not presumed to be MOD record slots.

Limits: input/report 32 MiB, 4096 slots/tracks per animation, aggregate 100k track
record occurrences and 100k decoded key occurrences, raw frame sum <=1m per
track. Parse/validation completes before a fresh output directory is created.
Existing/Git-contained destinations reject. Inputs must stay stable while read;
CLI does not hash them. Source is opened read-only. Output I/O failure may leave
a partial new directory. No decryption, execution or console access.

## Validation

Twelve synthetic methods check floats, quantized rational checkpoints, negative
scale/offset distinction, cumulative raw deltas, zero delta, partial records,
nonfinite data, malformed pointers/ranges, metadata/tail overlap, shared/null
slots, unsupported codecs, empty buffers, budgets, CLI behavior, preservation
and fresh/Git destination rejection. Rejections require return code 1, not any
crash/nonzero result; subprocesses have timeouts. CI: Windows/Linux Debug/Release,
with Linux Debug ASan/UBSan.

Additional local game-derived verification stays outside Git. Coverage must
distinguish synthetic codec tests from codecs actually exercised with nonempty
real buffers. A track supported by ID but having an empty payload is not counted
as a decoded vector track. Comparison with a separate project implementation
shares format assumptions and is not independent proof of game fidelity.

## Primary declarations consulted

Independently written implementation; no external codec implementation copied or
executed. Layout and numeric-format facts consulted in RevilLib:

- [bone_track.cpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/bone_track.cpp),
  blob `b46c5bffc89bed09c0f8e85697bc7d83952fa603`: version-2 codec IDs,
  sentinel and application of scale/offset when extremes exist.
- [codecs.hpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/codecs.hpp),
  blob `6a24d7a425cb4fffdce76b565b3c0b984b5c8c0a`;
  [codecs.cpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/codecs.cpp),
  blob `7beb0d9341253e5904f5aaf6ee039aebb1fd2106`: vector records and
  controller raw frame sequencing. Runtime reference-frame/loop handling is
  deliberately excluded here.
- [animation.inl](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/animation.inl),
  blob `f119d06a2ae9a81df42daa8537f08123d3de6e92`;
  [bone_track.inl](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_lmt/bone_track.inl),
  blob `f0377484b692b8bfd664d906e18abbe8d312762c`: LE32 field offsets.

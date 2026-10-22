# Read-only TEX A5 decoder (C++17)

Standalone, dependency-free first increment. Reads a TEX file or an explicit byte
range of a larger read-only file. Writes a new directory containing `image.pam`
(PAM RGBA, lossless). Never opens the input for writing or overwrites an existing
output directory. Do not commit private inputs or decoded commercial images.

Supported: TEX A5, normal 2D/size_shift=0, one texture, BGR888 (0x11) and
ABGR8888 (0x03), power-of-two dimensions 8..4096, contiguous mip offsets
relative to the pixel data. Every declared level must remain at least 8x8;
all offsets and the exact total payload length are checked before output.
8x8 Morton tile order is converted to row-major RGBA without flipping rows.
Orientation in the game is not verified.

Explicitly unsupported: A6, cubemaps, arrays, sub-8 mips/padding, ETC1/ETC1A4,
other pixel formats, material references, model rendering and animation.
The input range is capped at 128 MiB; malformed input fails before output.
An output I/O failure can leave a partial new directory, reported as an error.

```text
cmake -S texture-decoder -B build
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
stt-tex input.tex --out new-output --mip 0
stt-tex image.3ds --offset DECIMAL_OFFSET --size DECIMAL_LENGTH --out new-output
```

Tests generate asymmetric coordinate/color/alpha patterns with multiple tiles
and mip levels; they compare every RGBA byte, check malformed inputs and ensure
input hashes and existing destinations remain unchanged. Fixtures are synthetic.

## Research and relationship to other work

Reviewed PR #7 at `98f98f93d0c49205c2279d71c20cead973047bd6`, particularly
`docs/research/stt-re-20261021/first-resource-conversion.md`. Its converter handles
A6/ETC1(A4) from MHXX; it does not establish A5 uncompressed MH4U compatibility.
This branch starts from main and does not modify that PR or reader PR #39.

Header and channel format source:
[MH4U rTexture format](https://github.com/svanheulen/mhff/wiki/MH4U-rTexture-Format).
Cross-check source inspected:
[mhff tex.py](https://github.com/svanheulen/mhff/blob/master/n3ds/tex.py),
blob `1f8f48d4d248479f76e780ffcd60e82d096c0305`. No GPL source is bundled
or copied; this decoder implements the documented byte layout directly.

Next: verify compressed formats and small mip padding against separate test
vectors before adding support, then resolve texture/material/model references.

## Local validation (23 October 2026)

Windows/MSVC Debug and Release: all seven synthetic test methods passed,
including pixel comparisons for both formats and two mip levels. A private
MH4U A5/BGR888 texture (512x512) was read directly from a bounded range of the
local image and converted to PAM/PNG outside Git. Visual inspection found a
coherent logo. Every RGBA byte matched a separately written Python coordinate
traversal (16x8 groups); this checks the same documented layout, not game fidelity.
RGBA SHA256: `9569af882b11b667d70372f7f6f375e32c871116263dc105692e0f26fa21d81c`.
The source image SHA256 remained unchanged. Real-image ABGR8888/alpha and mipmaps
have not been checked; those cases currently have synthetic coverage only.

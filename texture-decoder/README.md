# Read-only TEX A5 decoder (C++17)

Standalone, dependency-free first increment. Reads a TEX file or an explicit byte
range of a larger read-only file. Writes a new directory containing `image.pam`
(PAM RGBA, lossless). Never opens the input for writing or overwrites an existing
output directory. Do not commit private inputs or decoded commercial images.

Supported: TEX A5, normal 2D/size_shift=0, one texture, BGR888 (0x11) and
ABGR8888 (0x03), ETC1 (0x0B) and ETC1A4 (0x0C), power-of-two dimensions
8..4096, contiguous mip offsets
relative to the pixel data. Every declared level must remain at least 8x8;
all offsets and the exact total payload length are checked before output.
Uncompressed 8x8 Morton tiles and ETC 8x8 tiles (four 4x4 subblocks) are
converted to row-major RGBA without flipping rows. ETC color words are
little-endian; A4 alpha precedes each color word and expands by 17.
Both ETC1 individual/differential modes, splits, selectors and modifier tables
are supported. Invalid differential base colors fail before output; only the
selected mip's color blocks are decoded, while lengths/offsets cover all mips.
Orientation in the game is not verified.

Explicitly unsupported: A6, cubemaps, arrays, sub-8 mips/padding,
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

ETC1 color bit layout and invalid differential overflow policy follow the
[Khronos ETC1 specification](https://registry.khronos.org/OpenGL/extensions/OES/OES_compressed_ETC1_RGB8_texture.txt).
3DS subtile order and A4 coordinates were checked against
[Azahar texture decoding](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/video_core/texture/texture_decode.cpp).
No third-party decoder source is copied or linked into this implementation.

Next: verify small mip padding and cubemap layouts against separate test
vectors, then resolve texture/material/model references.

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

### ETC1/ETC1A4 extension

Twelve synthetic test methods pass locally in Debug and Release. Tests cover
all modifier tables, both modes/splits, signed deltas, selector placement,
clamping, every alpha nibble, multiple tiles, three mip levels and malformed
compressed inputs. Fixed-seed vectors (1,024 blocks per compressed format)
have golden RGBA hashes obtained with an isolated texture2ddecoder 1.0.6 RGB
backend and a separate byte/nibble alpha traversal. CI requires no backend.
Linux Debug additionally enables AddressSanitizer/UndefinedBehaviorSanitizer.

Two private MH4U samples matched every RGBA byte of that reference pipeline:
ETC1 512x256 (arena image), and ETC1A4 1024x16 (font strip, all 16 alpha values).
The reference backend validates RGB independently; A4 uses separate coordinate
code and synthetic expectations, not a second independent A4 codec.
Both were visually inspected outside Git; no commercial fixtures are included.
Real compressed mip chains have not yet been tested. A6 remains unsupported.

Reference wheel: `texture2ddecoder-1.0.6-cp311-abi3-win_amd64.whl`, SHA256
`1bad8209d9dfbfc7daf13ea2e545236ea2bbc1e423b2992b6e7563909975a47b`,
verified against [official PyPI metadata](https://pypi.org/pypi/texture2ddecoder/1.0.6/json).
This optional reference was unpacked locally, not installed globally or bundled.

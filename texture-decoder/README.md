# Read-only TEX A5 decoder (C++17)

Standalone, dependency-free decoder. Reads a TEX file or an explicit byte range
of a larger file read-only. Writes a selected face/mip as lossless RGBA PAM into
a new directory, or verifies all supported color blocks without writing output.
No existing output directory is accepted. Never commit commercial inputs/images.

## Supported layout

TEX A5, size_shift=0, normal 2D (one texture) or square cubemap (six faces);
BGR888 (0x11), ABGR8888 (0x03), ETC1 (0x0B), ETC1A4 (0x0C). Dimensions must be
powers of two from 8 to 4096. All face/mip offsets must be contiguous, start at
zero relative to pixel data and fit the exact payload length. Every declared
mip must remain at least 8x8. Cubes carry an opaque 108-byte header extension and
store each face's complete mip chain before the next face.

Uncompressed 8x8 Morton tiles and ETC tiles (four 4x4 blocks per 8x8 tile) become
row-major RGBA without row flips. ETC words are little-endian. A4 precedes each
color block and expands each nibble by 17. Both ETC modes/splits, all modifier
tables/selectors and color clamping are supported. Differential base overflow
is rejected. All selector and A4 values have defined meanings.

By default, all ranges are checked but only the selected face/mip's color blocks
are decoded. `--verify-all` additionally checks differential base validity in
**every** ETC color block before any image output. For uncompressed formats,
all stored channel values are valid once the structural checks pass. Verification
without `--out` allocates no decoded RGBA image and creates no output directory.
Opaque header fields are not given semantic meaning by this verification.

`--face 0..5` selects storage order, not spatial axes. Face and mip default to
zero. Spatial face assignment, rotations and in-game orientation are unverified.
Unsupported: A6, arrays, mip dimensions below 8, padding variants, other pixel
formats, materials, model rendering and animation. Input is capped at 128 MiB.
A source/decode error fails before creating output; output I/O failure can leave
a partial new directory and is reported as an error.

```text
cmake -S texture-decoder -B build
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
stt-tex input.tex --verify-all
stt-tex input.tex --verify-all --out new-output --mip 0
stt-tex cubemap.tex --verify-all --out new-face --face 5 --mip 1
stt-tex image.3ds --offset DECIMAL_OFFSET --size DECIMAL_LENGTH --verify-all
```

## Validation and its limits

18 synthetic test methods cover full RGBA comparisons, asymmetric tiles,
all ETC tables/modes/splits/deltas/selectors, clamping, all alpha nibbles,
6 faces x 3 mips x 4 formats, and malformed inputs. Corrupt color blocks in an
unselected face/mip are accepted by selected decoding and rejected by
`--verify-all`; tests make that distinction explicit. Input hashes and existing
destinations are preserved; verification without output creates no files.
Windows/Linux Debug/Release CI includes Linux Debug ASan/UBSan.

Fixed-seed vectors (1,024 blocks per ETC format) have golden hashes checked with
texture2ddecoder 1.0.6 for RGB, plus separate byte/nibble alpha traversal.
CI requires no reference decoder. A4 has synthetic expectations and separate
coordinate code, not a second independent A4 codec. Reference wheel
`texture2ddecoder-1.0.6-cp311-abi3-win_amd64.whl`, SHA256
`1bad8209d9dfbfc7daf13ea2e545236ea2bbc1e423b2992b6e7563909975a47b`,
was checked against [PyPI metadata](https://pypi.org/pypi/texture2ddecoder/1.0.6/json)
and unpacked locally without global installation or bundling.

Private MH4U checks (23 October 2026), with no commercial fixtures in Git:

- BGR888 512x512: every RGBA byte matched a separate coordinate traversal.
- ETC1 512x256 and ETC1A4 1024x16: every RGBA byte matched the reference pipeline;
  the A4 sample retains all 16 alpha values. Both were visually inspected.
- A prefix-only survey of 38,320 TEX headers (150 direct, 38,170 ARC19 entries)
  found 147 ETC1 cubes and no declared mip below 8. This survey is not a new
  full-stream checksum or pixel audit of all 38,320 textures.
- All 147 cubes were read in full, checking zlib where applicable. All ranges
  and lengths fit: 74 cubes at 32x32/2 mips, 49 at 64x64/3, 24 at 128x128/4.
- `--verify-all` and a separate Python field check found no invalid differential
  bases in 330,144 color blocks across all 882 faces and 2,346 face/mip ranges.
  This checks encoded validity, not pixel-by-pixel agreement or game fidelity.
- Pixel agreement with the independent RGB backend covers 198 selections:
  each cube's first face/mip, plus every face/mip of one cube per size.
  A local contact sheet was visually inspected. This is a sample, not an
  independent pixel comparison of every cube face/mip.

Original image SHA256 remains unchanged. Real ABGR8888 and cubemap BGR888/
ABGR8888/ETC1A4 currently have synthetic coverage only. Real ETC1A4 mip chains
and spatial cube orientation remain unverified. Small mip layout lacks local
samples and stays explicitly unsupported; it is not a blocker to other work.

## Sources and related work

[MH4U texture format](https://github.com/svanheulen/mhff/wiki/MH4U-rTexture-Format)
and [mhff tex.py](https://github.com/svanheulen/mhff/blob/master/n3ds/tex.py),
blob `1f8f48d4d248479f76e780ffcd60e82d096c0305`, were inspected for layout.
ETC color fields follow the [Khronos specification](https://registry.khronos.org/OpenGL/extensions/OES/OES_compressed_ETC1_RGB8_texture.txt).
3DS subtile/A4 coordinates were checked against
[Azahar](https://github.com/azahar-emu/azahar/blob/0ff3440232d6bc9226e37c41c05c5aead03f37fd/src/video_core/texture/texture_decode.cpp).
No third-party decoder source is copied or linked into this implementation.

Reviewed PR #7 at `98f98f93d0c49205c2279d71c20cead973047bd6`, including its
`first-resource-conversion.md`: A6/MHXX results do not establish A5/MH4U
compatibility. This branch starts from main and does not modify PR #7 or reader
PR #39. Next work can address texture/material/model references independently
of unsupported small mip layouts. No PS Vita access is involved.

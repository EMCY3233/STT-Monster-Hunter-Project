# MOD230 static geometry and MRL32 evidence (C++17)

Standalone first increment for MH4U, with no external library dependency.
Reads MOD230 and optional MRL32 without writing either source. Produces
`model.obj`, neutral `materials.mtl` and `report.json` in a new directory.
All conversion/validation finishes before the directory is created. Existing
outputs and destinations under a `.git` ancestor are rejected. Output I/O failure
can leave a partial new directory; inputs must remain stable while reading.
Never commit commercial resources, generated geometry or previews.

```text
cmake -S model-converter -B build
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
stt-model local.mod --mrl local.mrl --out NEW_PRIVATE_DIRECTORY
```

## Supported geometry

Only static MOD230 with zero joints/envelopes in the header; vertex format
`0x59DC400B`, stride 28, triangle-strip primitive 4 and zero weight-count field.
Positions: f32x3 at +0; normals: snorm8x3 at +12 (clamp -128 to -1);
UV: f32x2 at +16. Tangents and other attributes are not exported. Coordinates,
UV values and strip winding stay native; no axis, scale or UV flip is invented.

Checks header/table/buffer ranges and structural overlaps, material/group IDs,
mesh vertex/index windows, finite positions/UV, restart 0xFFFF and index bounds.
Strip parity advances across degenerates and resets on restart. Repeated-index
triangles and exact zero-area triangles are omitted and counted. OBJ indices
remain valid across multiple exported meshes; normals are not re-normalized.

Global index count caveat: observed MH4U sample declares one u16 more than the
file provides globally. Only shortfall 0 or exactly 2 bytes is accepted; every
mesh-declared index window must still be fully present and within its declared
global count. Shortfall is reported, not repaired; no missing bytes are invented.
This profile does **not** establish the meaning of that global counter or validate
all unknown header/tail fields. Larger/odd shortfall and unsupported layouts fail.

Budgets: 32 MiB per input, 4,096 meshes/materials/groups; declared vertices up to
1,000,000 and indices up to 4,000,000. Aggregate exported vertices <=250,000 and
processed indices <=1,000,000 (including reused windows); OBJ <=128 MiB checked
after each mesh, material report <=16 MiB checked after each material. MOD names
must be unique, nonempty NUL-terminated ASCII, up to 127 bytes.

## Material evidence, without shader guesses

MRL32 profile: 28-byte header, contiguous 76-byte resource table then 60-byte
material records. Count/ranges and nonoverlapping descriptor blocks are checked.
Unknown resource records of type zero remain opaque; typed resources expose
bounded ASCII paths as metadata only, never filesystem paths to open or write.
Descriptors are 12 bytes; count is low 12 bits at material +24, block size at +8,
pointer at +52. Other bytes/fields remain uninterpreted.

MOD's 128-byte material names are compared via complement CRC32 to record +4.
The report counts matches, without treating CRC as collision-proof identity.
Zero or multiple matches produce no selected record/slot list. For a unique
match, descriptors with low tag nibble 3 expose raw values and **candidate**
one-based resource references; zero/out-of-range values or type-zero records
give no path. This interpretation is a hypothesis, not verified shader binding.
Texture role, sampler, UV transforms, blend state and appearance remain unknown.
All MTL slots are deliberately neutral; no texture is assigned automatically.

## Tests and local evidence

13 synthetic test methods cover positions/UV/normals, strip winding, restart and
parity after degenerates, zero area, nonzero vertex start, multiple meshes,
material hash matching/ambiguity, unresolved references, malformed ranges/strings,
nonfinite attributes, index count caveat, preservation of sources/outputs and
Git destination rejection. CI: Windows/Linux Debug/Release; Linux Debug ASan/UBSan.

Private MH4U sample (23 October 2026): one mesh, 16 vertices, 6 triangles,
20 repeated-index triplets removed, one material hash matching one MRL record.
Its five nibble-3 descriptors include one typed resource path, two null values
and two indices to opaque type-zero resources. The typed path has one exact TEX
entry match in the same ARC. This establishes a reference candidate, not a
textured material or shader role. Source MOD SHA256:
`8f05ff89972cf682fad408e0f384191ac6fe100ae5a69f481f9aead2b001756f`.

Positions/UV/normals and oriented faces were compared against the project's
Python converter from PR #7; MRL fields/CRC against PR #27's Python parser.
These are separate project implementations with related format assumptions,
not independent proof of fidelity to the game. A local four-view plot was
visually inspected: simple pyramidal geometry, not a converted monster.
The global index shortfall is 2 bytes. Source image SHA256 remains unchanged.
Commercial inputs/outputs and detailed catalogs remain outside Git.

## Coordination and sources

Starts from main `f199bd07b4e05ee4f7e56ed616840518374f3300` in a separate branch.
Reviewed PR #7 at `98f98f93d0c49205c2279d71c20cead973047bd6` and PR #27 at
`9c196193c182c469b3beaf79b51328c57f1b3c22`. Their MHXX results are not presented
as MH4U validation. Neither branch is changed; reader #39/texture #40 stay separate.
Field references:
[MH4U MOD](https://github.com/svanheulen/mhff/wiki/MH4U-rModel-Format),
[MH4U MRL](https://github.com/svanheulen/mhff/wiki/MH4U-rMaterial-Format),
and the project's prior documented vertex-layout/index evidence. No third-party
parser source is copied or linked. No console access, keys or decryption.

Pending: additional vertex formats, skeleton/weights, animation, verified shader
bindings and textured rendering. Authenticity remains outside this conversion;
the prior embedded-signature mismatch is not resolved by exporting geometry.

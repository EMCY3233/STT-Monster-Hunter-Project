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

Checks header/table/buffer ranges and structural overlaps, material indices/group IDs,
mesh vertex/index windows, finite positions/UV, restart 0xFFFF and index bounds.
Strip parity advances across degenerates and resets on restart. Repeated-index
triangles and exact zero-area triangles are omitted and counted. OBJ indices
remain valid across multiple exported meshes; normals are not re-normalized.
Group references are IDs matched to the first u32 in each 32-byte group record,
not ordinal indices bounded by group count. Sparse IDs are accepted; missing
and duplicate IDs fail. Each mesh report preserves its `group_id`, `lod_mask_raw`
and `visible_bit_raw`. All meshes are exported; no runtime LOD/visibility/culling
policy is inferred or applied.

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

### Offline inspection tool

`python build_inspector.py PRIVATE_MODEL_OUTPUT --textures PRIVATE_PNG_CATALOG --out NEW_PRIVATE_DIRECTORY`

Builds one self-contained `index.html` using Python's standard library. Open it
locally in a WebGL 2 browser; no server, CDN or network connection is needed.
Filters meshes/materials, rotates and zooms geometry, shows raw mesh metadata,
and offers wire edges and detail/full bounding-box framing. Detail framing uses
coordinate percentiles 2–98; all exported triangles remain available. The camera
is an orthographic inspection projection, not the game's camera. Very distant
geometry can lie outside the inspection clipping volume at a given zoom.

Optional texture catalog: `catalog.json` with `textures` entries containing
`path` (MRL candidate identity), relative `png`, `width`, `height`, `png_sha256`.
Only candidates named by the selected material appear. No texture is assigned
automatically: each selection resets the explicit trial checkbox. A trial uses
native UVs, linear sampling/repeat, no vertical flip, blending, original lighting
or shader reconstruction. PNG alpha is retained but blending is disabled;
transparency and appearance are therefore **not** reproduced. OBJ/MTL stay neutral.

Builder accepts the converter's triangular, matching-index OBJ subset, validates
finite attributes and index/count/material agreement with the report, and rejects
existing outputs and Git destinations. Budgets: OBJ 128 MiB, report 16 MiB,
250k vertices, 1m face indices, 4096 meshes; up to 256 PNGs, 4096 pixels per axis,
16 MiB each/32 MiB aggregate, final HTML 64 MiB. PNG signature, IHDR dimensions
and supplied SHA256 are checked; this is not a general-purpose PNG validator.
Catalog paths cannot escape their directory. Embedded metadata escapes `<` and
is displayed as text; a restrictive content policy blocks network access.
Inputs must remain stable; output I/O failure can leave a partial new directory.

Four additional synthetic tests exercise preservation, overwrite/Git rejection,
nonfinite/index/report errors, PNG hash/dimension/path checks and script escaping.
Private local Edge smoke test: 189 meshes/57 materials, neutral default, explicit
texture trial on one selected mesh, no JS errors or external requests. This
browser check is local evidence, not a CI browser test or proof of game fidelity.
All 49 stage candidate textures were checked with full encoded verification;
every decoded base-level pixel matched the separate RGB backend plus separate
alpha-nibble traversal. The alpha check is not a second independent ETC1A4 codec.
Neither the catalog nor private HTML/PNGs belongs in Git.

16 synthetic test methods cover positions/UV/normals, strip winding, restart and
parity after degenerates, zero area, nonzero vertex start, multiple meshes,
material hash matching/ambiguity, unresolved references, malformed ranges/strings,
nonfinite attributes, index count caveat, preservation of sources/outputs and
Git destination rejection, sparse/missing/duplicate group IDs and preservation
of raw LOD/visibility fields without filtering. CI: Windows/Linux Debug/Release;
Linux Debug ASan/UBSan.

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

### Larger static stage and group-ID correction

A bounded survey read 10,472 local MOD230 entries: 1,991 with zero joints and
8,481 with joints. These are archive occurrences, not deduplicated assets or
models all proven convertible. It also found additional unsupported vertex
layouts. The larger checked zero-joint model uses the already supported layout.

It exposed a real rejection bug: eight group records have IDs including 62/88;
the old `group < group_count` test rejected valid references. Source evidence
and actual group records support ID lookup. The regression now accepts ID 88
in a one-record synthetic group table and rejects a missing or duplicate ID.

Private MH4U static stage: 35,272 vertices, 28,112 nondegenerate triangles across
189 meshes and 57 material names. All 57 have one hash-matching MRL record;
49 unique typed candidate paths each match one TEX A5 entry in the same ARC
(full bounded zlib streams checked). Texture roles remain unverified.
Raw LOD masks are all 255 and visible bits all 1 in this sample; this does not
establish the game's complete visibility/culling behavior.

Every exported position, UV, normal and oriented face matched a separate Python
source-data traversal exactly. Removed: 30,905 repeated-index triplets and two
exact zero-area triangles; global index shortfall remains 2 bytes. MOD SHA256:
`24e202b846de1ba76425360156483a0248ee53da51334a47c4006d641eea5ec5`.
A local wireframe plot was visually inspected. Its percentiles 2..98 frame the
detail; the full OBJ retains all vertices/meshes. No scene fidelity or shader
appearance is claimed. No commercial stage data or preview is committed.

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

Group-ID evidence additionally checked against RevilLib's
[mesh field definitions](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/mesh.hpp),
[reflection into groupId](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/common.cpp)
and [MODGroup definition](https://github.com/PredatorCZ/RevilLib/blob/master/include/revil/mod.hpp),
the latter blob `7673422cdf37412eeedd96283f2b3f10b64bf28e`.
Only the layout/identifier relation was inspected; no library code was copied.

Pending: additional vertex formats, skeleton/weights, animation, verified shader
bindings and textured rendering. Authenticity remains outside this conversion;
the prior embedded-signature mismatch is not resolved by exporting geometry.

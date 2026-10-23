# MOD230 weighted-mesh inspection (C++17)

Read-only structural inspection, without geometry, skeleton or animation export.
Standalone, no dependency on the reader/texture/static-converter PRs and no
external libraries. Never commit private inputs or their generated reports.

```text
cmake -S skin-inspector -B build
cmake --build build --config Release
ctest --test-dir build -C Release --output-on-failure
stt-skin INPUT.mod --out NEW_PRIVATE_DIRECTORY
stt-skin INPUT.mod --out ANOTHER_NEW_PRIVATE_DIRECTORY --check-rest-pose
```

## Profile and validation

Little-endian MOD230, 1..255 bones. Bone records are 24 bytes, followed by two
tables of 64-byte matrices per bone, 256 opaque global-remap bytes and 28-byte
skin-palette records (u32 count <=24, followed by byte bone-slot candidates).
Checks finite bone scalars/matrices, parent slots, roots and cycles. It does not
interpret the global remap or assert that the matrices are inverses. Bone index
and mirror fields remain uninterpreted; parents use record slots, not index IDs.

Validates nonoverlapping header/skeleton/group/material/mesh/vertex/index ranges,
sparse group IDs and material references. Header profile starts at 128 bytes;
other unknown metadata is not interpreted. The global index declaration may
overstate available bytes by exactly one u16: shortfall 0 or 2 is reported,
never repaired; every mesh window must remain within actual and declared bounds.

Weighted formats inspected:

| Format | Stride | Indices (byte offsets) | Weight bytes |
| --- | --- | --- | --- |
| `0x01B36016` | 36 | 24, 25, **32, 33** | 26, 27, **34, 35** |
| `0xF606F017` | 36 | 24, 25, **32, 33** | 26, 27, **34, 35** |
| `0xD6784014` | 28 | 24, 25 | 26, 27 |
| `0x43FB3015` | 32 | 24, 25 | 26, 27 |
| `0x7BA7401B` | 32 | 24, 25 | 26, 27 |

For the 32-byte profiles, +28..31 are respectively tangent/color storage in
the primary declaration. This weight inspector leaves those attributes opaque;
it does not export, render or validate their appearance. Format `0x866B6018`
remains unsupported: a prefix that resembles another format is insufficient to
declare its complete layout known.

Positions f32x3 at +0, UV f32x2 at +16 must be finite. Supported meshes require
triangle-strip primitive 4. Vertex start is buffer + (start + adjustment)*stride
+ stream; u16 mesh indices use `index-start`, excluding restart 65535. A record
is referenced if any index addresses it, including degenerate strip indices.

**Candidate interpretation:** mesh byte +37 selects a skin palette; each
nonzero-weight byte index addresses a palette slot, which addresses a bone-record
slot. With no skin palettes, indices address bone slots directly. Checks every
declared palette slot, all active references (including unused vertex records),
and active influence count against the mesh field. Referenced vertices must
sum to exactly 255 in raw weight bytes; no normalization or inferred weights.
Zero-weight influence indices are ignored. Unreferenced zero-weight records
are counted; other unreferenced sums are not required to equal 255.

Unknown formats are listed with `supported:false`; their declared buffer ranges,
group/material references and index windows are checked, but their attributes
and individual index values are **not** validated. They are excluded from
supported vertex/reference/influence totals. A file with no supported mesh fails.
At least one supported vertex must be referenced; empty/restart-only coverage
fails rather than reporting successful weight inspection with no used records.
JSON includes `has_unsupported_meshes` and per-mesh raw stride, vertex/index
counts, weight-count field and palette selector. Header vertex/index counts are
reported as raw declarations; no equality with summed mesh windows is inferred.
Vertex counters are **window occurrences**, not unique physical vertices: shared
windows and meshes can count the same bytes more than once.
`active_influences` counts nonzero weight slots in all supported vertex-window
records, including unreferenced records. `referenced_active_influences` counts
only those in records addressed by mesh indices. Neither count represents unique
bones or distinct physical influences across shared windows.
Success means the described partial profile passed, not that every mesh or the
whole MOD is understood. JSON explicitly keeps palette semantics, functional
skinning and matrix inverse verification false.

Budgets: 32 MiB input, 4096 meshes/materials/groups, 256 palettes, declared 1m
vertices/4m indices, aggregate 250k supported vertex records/1m processed indices.
Parse completes before creating a new output directory. Existing and Git-contained
destinations are rejected. Inputs must remain stable during the read; source is
opened read-only, but the CLI does not compute before/after hashes. Output I/O
failure can leave a partial newly created directory. No runtime/console access.

## Optional rest-pose diagnostic

`--check-rest-pose` evaluates one explicit hypothesis, not a game-verified rig:
row vectors, local matrices A from the first table, global G_i=A_i*G_parent,
effective E_i=B_i*G_i from the second table B, and root common transform C=E_root.
For each referenced supported vertex p, compares sum(w_i/255 * p*E_palette[i])
with p*C. Weights and palette ranges must first pass the structural profile.
No renormalization, inverse calculation, coordinate conversion or output mesh.

Requires exactly one root and matrices with exact affine fourth column
(0,0,0,1). Multiple roots/nonaffine tables produce explicit `unavailable_*`
status, zero compared records and **null** error values, while the ordinary
structural report remains available. Disabled by default. Nonfinite computed
arithmetic rejects the diagnostic invocation before output creation.

Reports maximum absolute xyz residual in raw transformed coordinate units and
maximum per-record relative residual, divided by max(1,max(abs(expected xyz))).
No pass/fail tolerance is imposed; `computed_under_hypothesis` means evaluated,
not verified. Unknown meshes remain excluded. Arithmetic uses double precision
on stored float inputs; these residuals do not measure original game accuracy.

**Fundamental limit:** if all effective matrices are the same common transform,
any normalized blend yields the same rest result. Permuted palettes or altered
weight distributions can therefore produce zero residual. The report explicitly
keeps palette identity and weight distribution unverified. Synthetic tests prove
this blind spot as well as checking a broken bind and noncommuting hierarchy.
This diagnostic does not validate dynamic deformation or an LMT association.

## Evidence and rectifications

Twenty-one synthetic test methods cover all five profiles, grouped latter influence
offsets, unknown-format reporting, invalid active references/weight sums/palettes,
parent cycles/ranges, nonfinite values, overlaps, index windows and shortfall,
source/output preservation, Git destinations and CLI errors, a cycle with a
separate valid root, no-palette candidate bone domain, restart-only rejection,
and simultaneous nonzero vertex start/adjustment/stream offsets. They also check
both 32-byte profiles/mismatched strides, separation of influence counters and
early rejection of an oversized sparse source before any output. CI targets
Windows/Linux Debug/Release with ASan/UBSan on Linux Debug.
Rest diagnostic cases cover a nonidentity common transform, correct row-vector
hierarchy with noncommuting transforms, broken bind residual, palette/weight
ambiguity, multiple roots/nonaffine unavailability and invalid referenced weights.

Initial two-profile local private check: 20 distinct MH4U MOD hashes, representing 18 skeleton-table
signatures, selected nonrandomly from the first 20 `/data/emNNN.arc` files.
The two profiles occur in 15 files (120 meshes); 331 meshes have other formats.
Five files are correctly rejected as unsupported-only. For the two profiles,
25,432 vertex records include 17,296 referenced records, all with raw weight sum
255 and active indices within the candidate palettes. The remaining 8,136 zero
weight records are unreferenced. C++ counters match the separate project Python
probe; shared format assumptions mean this is not independent game validation.
Original image SHA256 was checked before/after the Python audit and stayed equal.

Expanded check with `0xF606F017`: the same 20 files now all contain supported
meshes, 449 in total; two meshes remain unsupported (`0x866B6018`, stride 44).
109,720 supported vertex-window occurrences include 96,472 referenced records,
all with exact raw sum 255 and candidate active references in range. The 13,248
zero-weight records are unreferenced. C++ counters match the expanded Python
probe on all 20 files. This is the same selected corpus, not an independent
holdout or proof of game behavior. The additional profile shares the primary
declaration's layout; no offset inference was made from its format hash.

The initial local four-influence probe incorrectly interleaved its last two
index/weight pairs. Those results are superseded. The grouped offsets above
match the primary format declaration and eliminate the observed anomalous sums
and active out-of-range references. No malformed samples were silently normalized.

Separately, 40 matrix-product hypotheses were tested locally. None gives identity
for all bones; four give a common root product, with maximum normalized residual
5.850722e-8 over 736 bone-record occurrences. Requiring identity alone cannot
discard an otherwise coherent structural reading. A common product still does
not establish its meaning, coordinate convention or a usable rig. Parent-first
and child-first alternatives remain indistinguishable in this sample. These
matrix-hypothesis sweep remains research evidence; the CLI optionally evaluates
only the explicitly documented row-vector rest-pose hypothesis above.

Remaining: independently validate palette semantics, unknown formats, coordinate
and model-space transforms, actual deformation, LMT associations and animation.
This tool does not modify the static converter or claim a converted monster.

## Primary format references

Independently written inspection code; no external library code copied or run.

- [RevilLib common.cpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/common.cpp),
  blob `5435277ef757c0f6c7bdeae7efd0837fe44df8f1`: attribute layouts, XE5 mesh
  palette selector and distinction between Transforms/InverseBinds.
- [bones.hpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/bones.hpp),
  blob `742e88d2f7eaaa31a9ccdcf3581d86d948ca8fb3`;
  [traits.hpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/traits.hpp),
  blob `61f901ad82bd674592682aaed26ab2d4e59eeb3d`;
  [serialize.cpp](https://github.com/PredatorCZ/RevilLib/blob/master/src/mtf_mod/serialize.cpp),
  blob `b599dc118442471c6e2cc00c161dadd0e61cb432`: tables and XE6 using XE5 reader.
- [Historical MH4U Blender importer](https://github.com/svanheulen/mhff/blob/master/n3ds/io_import_scene_mod.py),
  blob `0da950c275caf78bfcfa310f6a45c488e890d94b`: its latter influence pairs
  are interleaved differently; it does not construct the skeleton. That code
  is therefore not an oracle for these offsets or proof of functional skinning.

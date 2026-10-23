# A32 integer leaf → native C++17 experiment

The current user goal is to bring the original MH4U program to PC using C++,
rather than replace its behavior with an original recreation. This supersedes
the earlier recreation direction recorded in PR #43. The original native arena
in PR #44 remains an independent renderer/input experiment; it does not execute
the original game. Reader branches stay separate; no PR is merged here.

This module is a deliberately small translation/equivalence experiment. A Python
generator emits a C++17 function from a bounded raw A32 instruction fragment;
the actual translated computation runs as native compiled C++. There is no ARM
interpreter/JIT in that generated function. Unicorn is a separate test oracle,
not the game's runtime or a dependency of the generated function.

## Supported contract

- Little-endian A32, 1..65 instructions, final unconditional `BX LR`.
- Integer AND/EOR/SUB/RSB/ADD/ORR/MOV/BIC/MVN, unconditional and without S.
- Sources/destinations R0..R12; rotated 8-bit immediates or unshifted registers.
- Unsigned 32-bit wrapping arithmetic; flags unaffected except BX's T bit.
- Entry is user-mode A32 with only NZCV/Q/GE flags optionally set. No IT/Jazelle,
  exception state, privilege, big-endian mode, memory accesses or interrupts.
- LR must be an aligned ARM address or a Thumb address with its low bit set.
  Unsupported entry state rejects atomically before executing any statement.
- Return updates PC and the Thumb state bit. Thumb *entry/instructions* are not
  translated. PC/SP/LR are excluded from arithmetic source/destination fields.

Everything outside this subset is rejected, including memory, calls, branches,
conditional instructions, shifts, flag-setting arithmetic, VFP, SVC and Thumb.
This is not a general recompiler. A byte sequence that fits the contract is not
proof of a function boundary, original-game reachability or gameplay semantics.

## Local use

```sh
python arm-leaf-lab/translate.py PRIVATE_FRAGMENT.bin --out NEW_PRIVATE_DIR
cmake -S arm-leaf-lab -B build/leaf -DSTT_LEAF_INCLUDE=/absolute/NEW_PRIVATE_DIR
cmake --build build/leaf --config Release
```

The CLI opens its input for reading and validates before creating output.
It rejects existing destinations and destinations in Git checkouts. It emits
`translated.hpp` and a SHA-256/scope report. Keep any game-derived inputs,
generated C++, builds, disassembly and reports private, outside Git. The generic
runner consumes decimal CPSR followed by R0..R15; it returns acceptance, CPSR
and R0..R15. No original-game code or derived code is committed here.

## Verification

Use Python 3.12 with isolated development dependency `unicorn==2.1.4`, a C++17
compiler and CMake:

```sh
cmake -S arm-leaf-lab -B build/leaf-tests
ctest --test-dir build/leaf-tests -C Release --output-on-failure
```

Seven synthetic test methods compile 21 original fixtures as C++17, then compare
all registers, CPSR and ARM/Thumb return PC against Unicorn for 5,376 seeded
states, including edge values and unsigned wrapping. They also cover atomic
entry rejection, unsupported encodings, input/output preservation, output
containment and validation before output creation. CMake invokes another
temporary build that also compiles and checks the generic runner. The
temporary CMake builds' outputs are removed after
the tests. Unicorn is required: missing dependencies fail, not silently skip.

Unicorn's project documents GPLv2; it is used only as a separate development
oracle and is not bundled or linked into generated C++. Capstone, when used in
private analysis, is also not part of this module. No external implementation
has been copied into the generator. Repository-wide licensing remains a
separate decision.

## Port investigation and next gates

ExeFS `.code` may use reverse-LZSS compression; segment addresses, page counts
and meaningful sizes come from the exheader. Compressed and decompressed bytes
must not be confused, nor should padding/rodata be blindly disassembled as code.
A public format reference is https://docs.mikage.app/NCCH/Extended_Header/ and
https://docs.mikage.app/ExeFS/ . A loader implementation used as a format
cross-check is Project_CTR `ctrtool/src/lzss.c` (blob
69868c3eb96229730bf35a9a11fe54048c30f979).

The external 3dsrecomp project is worth evaluating, but its `port` command emits
C and links it into the Rust Zakuro runtime, which supplies kernel/services,
graphics and sound; it is not a complete C++ port solution for this target.
See https://github.com/fearkov/3dsrecomp/blob/main/docs/port.md (blob
6018e39eb380a50736e18303e9009b30bd0ec22f).

Before claiming original-game execution, we still need confirmed routine
boundaries/callers, memory-bearing routines, ABI and relocation handling,
ARM/Thumb/VFP and control-flow coverage, kernel/service replacements, graphics
and audio integration, and end-to-end behavior checks. Static call-pattern
matches are candidates; direct-control-flow traversal also has incomplete
indirect targets. Neither is a coverage percentage or a runtime trace.

Windows 10 x64 remains the minimum target, pending direct OS testing. No keys,
decryption or Vita access. Private results must state exactly what executed;
arithmetic-fragment equivalence does not mean the game boots or is playable.

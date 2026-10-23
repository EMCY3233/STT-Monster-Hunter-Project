# Decoder contract follow-up to PR #45

This branch depends on PR #45 at d91eb729647cea45dbd099a3fd03e4bded75796d.
It is a separate review branch; no existing branch or PR is merged or rewritten.
PR #47 (Claude Code) changes the monitor simulator and host agent tests.
This follow-up touches only the A32 laboratory and this note, avoiding those files.
GitHub comments are the coordination record; no private Claude session was accessed.

## Verification and limits

Five Python-only synthetic test methods cover all 4,096 rotated-immediate
encodings using a bit-at-a-time rotation oracle, all condition/opcode pairs,
SP/LR/PC register exclusions, reserved MOV/MVN source fields, all 255 nonzero
register shift fields, and minimum/maximum fragment lengths and terminators.
They run as a separate CTest test alongside the existing native/Unicorn suite.
No translator behavior or supported instruction set changes.

Local Python 3.12: five tests passed. A local C++ compiler and CMake were not
found on PATH; the native differential suite was not rerun locally.
The PR #45 head has successful Windows/Linux Debug/Release synthetic checks:
https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/39888706214
The PR #47 head has successful monitor checks:
https://github.com/EMCY3233/STT-Monster-Hunter-Project/actions/runs/40026992104
New-branch CI must be checked separately; old checks do not validate new commits.

This tests the documented decoder contract, not every A32 encoding or native
execution semantics. It is not a proof of ARM architectural correctness.
The existing differential tests remain the execution oracle.
No game bytes, commercial resources, disassembly, keys or private reports are used.
No console, FTP or decryption operations were performed.

## Backlog / next gates

The reviewed repository plan (docs/areas/01.md), master changelog and PR #45
README still do not establish game execution. The next investigation gates
remain confirmed routine boundaries, memory and ABI/relocation handling,
control flow and ARM/Thumb/VFP coverage, then services, graphics and sound.
Do not infer percentage coverage, bootability or gameplay from these tests.

OpenCode was not found on PATH in this environment, so no task was dispatched.
To enable it later, make its executable available to this workspace and configure
a provider through its normal authentication flow, without posting credentials.
Check its version/help locally before granting a bounded task. A useful independent
assignment is read-only review of decoder rejection tests in a separate checkout,
with findings returned through GitHub; do not share write ownership of this branch.

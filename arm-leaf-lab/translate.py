"""Strict experimental A32 integer-leaf to C++17 translation, not a game port."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

RETURN = 0xE12FFF1E
OPS = {0: "and", 1: "eor", 2: "sub", 3: "rsb", 4: "add",
       12: "orr", 13: "mov", 14: "bic", 15: "mvn"}


def decode(data):
    if not data or len(data) % 4 or len(data) > 260:
        raise ValueError("expected 1..65 complete A32 instructions")
    words = struct.unpack("<" + "I" * (len(data) // 4), data)
    if words[-1] != RETURN:
        raise ValueError("leaf must end with unconditional BX LR")
    result = []
    for word in words[:-1]:
        if word >> 28 != 14 or word & 0x0C000000 or word & (1 << 20):
            raise ValueError("only unconditional no-S data processing is supported")
        op, rn, rd = (word >> 21) & 15, (word >> 16) & 15, (word >> 12) & 15
        if op not in OPS or rd > 12:
            raise ValueError("unsupported operation or destination")
        if (op in (13, 15) and rn != 0) or (op not in (13, 15) and rn > 12):
            raise ValueError("invalid/unsupported source register")
        if word & (1 << 25):
            shift = ((word >> 8) & 15) * 2
            imm = word & 255
            value = ((imm >> shift) | (imm << ((32 - shift) % 32))) & 0xFFFFFFFF
            rhs = f"std::uint32_t{{{value}u}}"
        else:
            if word & 0xFF0 or (word & 15) > 12:
                raise ValueError("shifted/register-controlled operands are unsupported")
            rhs = f"s.r[{word & 15}]"
        lhs = f"s.r[{rn}]"
        expressions = {0: f"{lhs} & {rhs}", 1: f"{lhs} ^ {rhs}",
                       2: f"{lhs} - {rhs}", 3: f"{rhs} - {lhs}",
                       4: f"{lhs} + {rhs}", 12: f"{lhs} | {rhs}",
                       13: rhs, 14: f"{lhs} & ~{rhs}", 15: f"~{rhs}"}
        result.append({"operation": OPS[op], "destination": rd,
                       "statement": f"    s.r[{rd}] = {expressions[op]};"})
    return result


def emit(data):
    operations = decode(data)
    return """#pragma once
#include <array>
#include <cstdint>
struct ArmState { std::array<std::uint32_t, 16> r{}; std::uint32_t cpsr = 0x10u; };
// Experimental A32 user-mode, integer-only leaf. No memory or platform services.
inline bool translated_leaf(ArmState& s) noexcept {
    // Accept only user mode and NZCV/Q/GE flags, with ARM state and no IT block.
    // Reject an unaligned ARM return address before any state mutation.
    if ((s.cpsr & ~0xf80f0010u) != 0 || (s.cpsr & 31u) != 0x10u ||
        (s.r[14] & 3u) == 2u) return false;
""" + "\n".join(op["statement"] for op in operations) + """
    const std::uint32_t target = s.r[14];
    s.r[15] = target & ((target & 1u) ? ~1u : ~3u);
    s.cpsr = (s.cpsr & ~32u) | ((target & 1u) << 5u);
    return true;
}
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        target = args.out.resolve()
        if target.exists() or any((p / ".git").exists() for p in (target, *target.parents)):
            raise ValueError("output must be a new directory outside a Git checkout")
        with args.input.open("rb") as source:
            data = source.read(261)
        code = emit(data)  # Validate everything before creating output.
        report = {"input_sha256": hashlib.sha256(data).hexdigest(),
                  "instruction_count": len(data) // 4,
                  "arithmetic_operations": len(decode(data)),
                  "language": "C++17", "game_function_identity_verified": False,
                  "whole_game_execution_verified": False}
        target.mkdir(parents=True, exist_ok=False)
        (target / "translated.hpp").write_text(code, encoding="utf-8")
        (target / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        return 0
    except (OSError, ValueError) as error:
        print(error, file=__import__("sys").stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

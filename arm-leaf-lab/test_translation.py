import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest

import translate

parser = argparse.ArgumentParser()
parser.add_argument("--cmake", default="cmake")
parser.add_argument("--config", default="Release")
parser.add_argument("--cases", type=int, default=256)
options, remaining = parser.parse_known_args()
if not 8 <= options.cases <= 4096:
    parser.error("--cases must be between 8 and 4096 per fragment")
sys.argv = [sys.argv[0], *remaining]
HERE = Path(__file__).resolve().parent


def binary(*words):
    return struct.pack("<" + "I" * len(words), *words)


def instruction(op, immediate, operand, rn=1, rd=0):
    return 0xE0000000 | (immediate << 25) | (op << 21) | (rn << 16) | (rd << 12) | operand


def fixtures():
    result = []
    for op in translate.OPS:
        for immediate in (False, True):
            result.append(binary(instruction(op, immediate, 2 if not immediate else 0x480,
                                             rn=0 if op in (13, 15) else 1), translate.RETURN))
    # Aliasing, unsigned wrapping and a rotated-immediate sequence.
    result.append(binary(instruction(4, False, 1, rn=0),
                         instruction(2, True, 1, rn=0), translate.RETURN))
    result.append(binary(instruction(13, True, 0x102, rn=0), translate.RETURN))
    result.append(binary(translate.RETURN))
    return result


class TranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="stt-leaf-")
        cls.root = Path(cls.temp.name)
        cls.samples = fixtures()
        parts = []
        for index, sample in enumerate(cls.samples):
            source = translate.emit(sample).replace("translated_leaf(", f"leaf_{index}(")
            if index:
                source = "inline bool " + source.split("inline bool ", 1)[1]
            parts.append(source)
        (cls.root / "bank.hpp").write_text("\n".join(parts))
        (cls.root / "translated.hpp").write_text(translate.emit(cls.samples[0]))
        functions = ",".join(f"leaf_{i}" for i in range(len(cls.samples)))
        (cls.root / "main.cpp").write_text('''#include "bank.hpp"
#include <iostream>
int main() {
    using Fn=bool(*)(ArmState&); const Fn bank[]={''' + functions + '''};
    unsigned index; ArmState s;
    while(std::cin>>index>>s.cpsr) {
        if(index>=sizeof(bank)/sizeof(bank[0])) return 1;
        for(auto& r:s.r) if(!(std::cin>>r)) return 1;
        const bool ok=bank[index](s);
        std::cout<<ok<<' '<<s.cpsr;
        for(auto r:s.r) std::cout<<' '<<r;
        std::cout<<'\\n';
    }
    return std::cin.eof()?0:1;
}
''')
        (cls.root / "CMakeLists.txt").write_text('''cmake_minimum_required(VERSION 3.16)
project(synthetic_leaf_bank LANGUAGES CXX)
add_executable(bank main.cpp)
target_compile_features(bank PRIVATE cxx_std_17)
if(MSVC)
target_compile_options(bank PRIVATE /W4 /WX /permissive-)
else()
target_compile_options(bank PRIVATE -Wall -Wextra -Wpedantic -Werror)
endif()
''')
        with (cls.root / "CMakeLists.txt").open("a") as out:
            out.write(f'add_executable(single_runner "{(HERE / "runner.cpp").as_posix()}")\n'
                      'target_include_directories(single_runner PRIVATE "${CMAKE_CURRENT_SOURCE_DIR}")\n'
                      'target_compile_features(single_runner PRIVATE cxx_std_17)\n')
        subprocess.run([options.cmake, "-S", str(cls.root), "-B", str(cls.root / "build"),
                        f"-DCMAKE_BUILD_TYPE={options.config or 'Release'}"],
                       check=True, capture_output=True, text=True, timeout=60)
        subprocess.run([options.cmake, "--build", str(cls.root / "build"), "--config",
                        options.config or "Release"], check=True, capture_output=True,
                       text=True, timeout=90)
        name = "bank.exe" if os.name == "nt" else "bank"
        cls.exe = cls.root / "build" / (options.config or "Release") / name
        if not cls.exe.exists():
            cls.exe = cls.root / "build" / name

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def execute(self, inputs):
        rows = [" ".join(map(str, [index, flags, *regs])) for index, flags, regs in inputs]
        done = subprocess.run([str(self.exe)], input="\n".join(rows)+"\n",
                              capture_output=True, text=True, check=True, timeout=30)
        return [list(map(int, line.split())) for line in done.stdout.splitlines()]

    def test_unicorn_differential(self):
        import unicorn
        from unicorn import arm_const as arm
        register_ids = [getattr(arm, f"UC_ARM_REG_R{i}") for i in range(13)] + [
            arm.UC_ARM_REG_SP, arm.UC_ARM_REG_LR, arm.UC_ARM_REG_PC]
        rng = random.Random(0xA32C17)
        inputs, expected = [], []
        for index, sample in enumerate(self.samples):
            cpu = unicorn.Uc(unicorn.UC_ARCH_ARM, unicorn.UC_MODE_ARM)
            cpu.mem_map(0x100000, 4096)
            cpu.mem_map(0x200000, 4096)
            cpu.mem_write(0x100000, sample)
            for case in range(options.cases):
                flags = 0x10 | (rng.getrandbits(32) & 0xF80F0000)
                regs = [rng.getrandbits(32) for _ in range(16)]
                if case < 8:
                    regs[0] = (0, 1, 0x7FFFFFFF, 0x80000000,
                               0xFFFFFFFF, 0xFFFFFFFE, 0xAAAAAAAA, 0x55555555)[case]
                    regs[1] = regs[0]
                regs[14], regs[15] = 0x200000 | (case % 2), 0x100000
                cpu.reg_write(arm.UC_ARM_REG_CPSR, flags)
                for reg, value in zip(register_ids, regs):
                    cpu.reg_write(reg, value)
                # The instruction-count bound includes the return, without a
                # per-state watchdog thread. CTest bounds the whole process.
                cpu.emu_start(0x100000, 0x200000, count=len(sample)//4+1)
                after = [cpu.reg_read(reg) for reg in register_ids]
                self.assertEqual(after[15], 0x200000, "ARM leaf must reach return sentinel")
                inputs.append((index, flags, regs))
                expected.append([1, cpu.reg_read(arm.UC_ARM_REG_CPSR), *after])
        self.assertEqual(self.execute(inputs), expected)
        print(f"C++17/Unicorn {unicorn.__version__}: {len(expected)} input states matched")

    def test_entry_contract_rejection_is_atomic(self):
        regs = list(range(16))
        regs[14] = 0x200002
        rows = [(0, 0x10, regs)]
        for cpsr in (0, 0x13, 0x30, 0x01000010, 0x210):
            clean = regs.copy()
            clean[14] = 0x200000
            rows.append((0, cpsr, clean))
        self.assertEqual(self.execute(rows), [[0, flags, *state] for _, flags, state in rows])

    def test_generic_runner(self):
        name = "single_runner.exe" if os.name == "nt" else "single_runner"
        exe = self.exe.parent / name
        regs = list(range(16))
        regs[14] = 0x200001
        values = [0xF80F0010, *regs]
        result = subprocess.run([str(exe)], input=" ".join(map(str, values))+"\n",
                                capture_output=True, text=True, check=True, timeout=10)
        self.assertEqual([list(map(int, result.stdout.split()))],
                         self.execute([(0, values[0], regs)]))

    def test_decode_rejects_unsupported_instructions(self):
        bad = [b"", b"x", binary(0xE3A00000), binary(0x112FFF1E),
               binary(translate.RETURN, translate.RETURN),
               binary(0xE2900001, translate.RETURN),  # ADDS
               binary(0xE5900000, translate.RETURN),  # LDR
               binary(0xEF000001, translate.RETURN),  # SVC
               binary(0xE1A00081, translate.RETURN),  # shifted MOV
               binary(0xE1A0D000, translate.RETURN),  # write SP
               binary(0xE080000F, translate.RETURN),  # read PC
               binary(0xE3A10000, translate.RETURN),  # reserved MOV Rn
               binary(*([0xE1A00000] * 65), translate.RETURN)]
        for value in bad:
            with self.subTest(value=value[:8].hex()), self.assertRaises(ValueError):
                translate.emit(value)

    def test_cli_preserves_input_and_existing_output(self):
        with tempfile.TemporaryDirectory(prefix="stt-leaf-cli-") as folder:
            root = Path(folder)
            source, target = root / "synthetic.bin", root / "result"
            source.write_bytes(self.samples[0])
            before = hashlib.sha256(source.read_bytes()).hexdigest()
            command = [sys.executable, str(HERE / "translate.py"), str(source), "--out", str(target)]
            self.assertEqual(subprocess.run(command, capture_output=True, timeout=10).returncode, 0)
            report = (target / "report.json").read_bytes()
            self.assertFalse(json.loads(report)["whole_game_execution_verified"])
            self.assertEqual(subprocess.run(command, capture_output=True, timeout=10).returncode, 1)
            self.assertEqual((target / "report.json").read_bytes(), report)
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)

    def test_invalid_input_creates_no_output(self):
        with tempfile.TemporaryDirectory(prefix="stt-leaf-invalid-") as folder:
            root = Path(folder)
            source, target = root / "bad.bin", root / "result"
            source.write_bytes(binary(0xEF000001, translate.RETURN))
            result = subprocess.run([sys.executable, str(HERE / "translate.py"), str(source),
                                     "--out", str(target)], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(target.exists())

    def test_git_output_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix="stt-leaf-git-") as folder:
            root = Path(folder)
            (root / ".git").write_text("gitdir: synthetic-marker")
            source = root / "synthetic.bin"
            source.write_bytes(self.samples[0])
            target = root / "private"
            result = subprocess.run([sys.executable, str(HERE / "translate.py"), str(source),
                                     "--out", str(target)], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()

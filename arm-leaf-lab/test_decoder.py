"""Synthetic decoder contract checks; no game inputs or native execution."""
import struct
import unittest
import translate

def fragment(word):
    return struct.pack("<II", word, 0xE12FFF1E)

class DecoderContractTests(unittest.TestCase):
    def test_all_rotated_immediates(self):
        # Independent bit-at-a-time rotation, rather than the generator formula.
        for rotation in range(16):
            for immediate in range(256):
                expected = immediate
                for _ in range(rotation * 2):
                    expected = (expected // 2) + ((expected % 2) * 0x80000000)
                word = 0xE3A00000 | (rotation << 8) | immediate
                self.assertEqual(translate.decode(fragment(word))[0]["statement"],
                                 f"    s.r[0] = std::uint32_t{{{expected}u}};")

    def test_condition_and_opcode_gates(self):
        allowed = {0, 1, 2, 3, 4, 12, 13, 14, 15}
        for condition in range(16):
            for opcode in range(16):
                word = (condition << 28) | (opcode << 21) | 2
                if condition == 14 and opcode in allowed:
                    self.assertEqual(len(translate.decode(fragment(word))), 1)
                else:
                    with self.assertRaises(ValueError):
                        translate.decode(fragment(word))
        for bit in (20, 26, 27):
            with self.assertRaises(ValueError):
                translate.decode(fragment(0xE0800002 | (1 << bit)))

    def test_register_boundaries_and_reserved_unary_source(self):
        for register in range(16):
            for word in (0xE0800002 | (register << 12),
                         0xE0800002 | (register << 16),
                         0xE0800000 | register):
                if register <= 12:
                    translate.decode(fragment(word))
                else:
                    with self.assertRaises(ValueError):
                        translate.decode(fragment(word))
            for base in (0xE1A00002, 0xE1E00002):
                word = base | (register << 16)
                if register == 0:
                    translate.decode(fragment(word))
                else:
                    with self.assertRaises(ValueError):
                        translate.decode(fragment(word))

    def test_every_nonzero_register_shift_field_rejects(self):
        # Bits 11..4 must all be zero, including register-controlled shifts.
        for field in range(1, 256):
            with self.assertRaises(ValueError):
                translate.decode(fragment(0xE0800002 | (field << 4)))

    def test_fragment_length_and_terminator_boundaries(self):
        ret = struct.pack("<I", 0xE12FFF1E)
        mov = struct.pack("<I", 0xE1A00000)
        self.assertEqual(translate.decode(ret), [])
        self.assertEqual(len(translate.decode(mov * 64 + ret)), 64)
        for data in (b"", ret[:3], mov, mov * 65 + ret,
                     ret + ret, mov + struct.pack("<I", 0x112FFF1E)):
            with self.assertRaises(ValueError):
                translate.decode(data)

if __name__ == "__main__":
    unittest.main()

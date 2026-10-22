"""Synthetic fixtures only: no commercial bytes or external keys."""
import importlib.util
import io
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

spec = importlib.util.spec_from_file_location('inventory_games', Path(__file__).parents[1] / 'tools' / 'inventory_games.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InventoryTests(unittest.TestCase):
    def test_bounded_read_rejects_truncation(self):
        with self.assertRaises(ValueError):
            module.read_at(io.BytesIO(b'x'), 0, 2)

    def test_cia_outside_file_not_accepted(self):
        header = struct.pack('<IHHIIIIQ', 0x2020, 0, 0, 0, 0, 0, 0, 1024)
        result = module.cia_probe(io.BytesIO(header), len(header))
        self.assertFalse(result['sections_within_file'])

    def test_cia_public_metadata(self):
        tmd_size = 0x140 + 0x9C4 + 48
        tmd_off = 0x2040
        content_off = module.align64(tmd_off + tmd_size)
        data = bytearray(content_off + 512)
        struct.pack_into('<IHHIIIIQ', data, 0, 0x2020, 0, 0, 0, 0, tmd_size, 0, 512)
        struct.pack_into('>I', data, tmd_off, 0x10004)
        body = tmd_off + 0x140
        data[body + 0x4C:body + 0x54] = bytes.fromhex('0004000000000001')
        struct.pack_into('>HH', data, body + 0x9C, 1041, 1)
        struct.pack_into('>IHHQ', data, body + 0x9C4, 1, 0, 1, 512)
        result = module.cia_probe(io.BytesIO(data), len(data))
        self.assertEqual(result['title_version_components'], [1, 1, 1])
        self.assertTrue(result['contents_metadata'][0]['encrypted_flag'])

    def test_invalid_sfo_rejected(self):
        with self.assertRaises(ValueError):
            module.sfo_fields(b'not a sfo')

    def test_iso_extension_does_not_establish_format(self):
        data = bytes(17 * 2048)
        self.assertEqual(module.iso_probe(io.BytesIO(data), len(data))['format'], 'unconfirmed_ISO_extension')

    def test_split_crc_crosses_part_boundary_and_detects_damage(self):
        payload = b'fixture-payload'
        next_header = b'fixture-header'
        rest = struct.pack('<QQI', len(payload), len(next_header), zlib.crc32(next_header))
        head = b'7z\xbc\xaf\x27\x1c\x00\x04' + struct.pack('<I', zlib.crc32(rest)) + rest
        combined = head + payload + next_header
        with tempfile.TemporaryDirectory(dir=Path(__file__).parents[1]) as directory:
            first = Path(directory) / 'fixture.7z.001'
            second = Path(directory) / 'fixture.7z.002'
            cut = len(head) + len(payload) + 3
            first.write_bytes(combined[:cut])
            second.write_bytes(combined[cut:])
            self.assertTrue(module.split_probe(first)['next_header_crc_ok'])
            second.write_bytes(b'X' + combined[cut + 1:])
            self.assertFalse(module.split_probe(first)['next_header_crc_ok'])


if __name__ == '__main__':
    unittest.main()

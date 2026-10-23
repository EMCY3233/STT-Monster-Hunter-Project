import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('builder', pathlib.Path(__file__).with_name('build_inspector.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class Inspector(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.obj = ('o mesh_0\nusemtl material_0\n'
                    'v 0 0 0\nv 1 0 0\nv 0 1 0\n'
                    'vt 0 0\nvt 1 0\nvt 0 1\n'
                    'vn 0 0 1\nvn 0 0 1\nvn 0 0 1\nf 1/1/1 2/2/2 3/3/3\n')
        self.report = {'vertices': 3, 'triangles': 1, 'meshes': [
            {'mesh': 0, 'material_index': 0, 'triangles': 1}],
            'materials': [{'name': '</script><script>bad()</script>', 'candidate_resource_slots': []}]}
        self.save()

    def save(self):
        (self.source / 'model.obj').write_text(self.obj)
        (self.source / 'report.json').write_text(json.dumps(self.report))

    def test_output_and_source_preservation(self):
        before = (self.source / 'model.obj').read_bytes()
        builder.build(self.source, self.root / 'out')
        html = (self.root / 'out/index.html').read_text(encoding='utf-8')
        self.assertNotIn('</script><script>bad()', html)
        self.assertIn('connect-src', html)
        self.assertEqual(before, (self.source / 'model.obj').read_bytes())
        with self.assertRaises(ValueError):
            builder.build(self.source, self.root / 'out')

    def test_invalid_geometry(self):
        for replacement in ('nan', 'inf', '1e100'):
            with self.subTest(replacement=replacement):
                self.obj = self.obj.replace('v 0 0 0', 'v ' + replacement + ' 0 0')
                self.save()
                with self.assertRaises(ValueError):
                    builder.build(self.source, self.root / 'out')
                self.obj = self.obj.replace('v ' + replacement + ' 0 0', 'v 0 0 0')
        self.obj = self.obj.replace('3/3/3', '4/4/4')
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.source, self.root / 'out')

    def test_report_and_git_rejection(self):
        self.report['triangles'] = 2
        self.save()
        with self.assertRaises(ValueError):
            builder.build(self.source, self.root / 'out')
        (self.root / '.git').mkdir()
        with self.assertRaises(ValueError):
            builder.build(self.source, self.root / 'other')

    def test_texture_validation(self):
        # Small valid RGBA PNG, generated without dependencies.
        import struct
        import zlib
        def chunk(tag, data):
            return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data))
        png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 6, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\0\xff\0\0\xff')) + chunk(b'IEND', b'')
        (self.source / 'image.png').write_bytes(png)
        entry = {'path': 'candidate', 'png': 'image.png', 'width': 1, 'height': 1, 'png_sha256': hashlib.sha256(png).hexdigest()}
        def catalog():
            (self.source / 'catalog.json').write_text(json.dumps({'textures': [entry]}))
        catalog()
        builder.build(self.source, self.root / 'valid', self.source)
        for field, value in [('png', '../image.png'), ('png_sha256', '0' * 64), ('width', 2)]:
            old = entry[field]
            entry[field] = value
            catalog()
            with self.assertRaises(ValueError):
                builder.build(self.source, self.root / 'invalid', self.source)
            entry[field] = old


if __name__ == '__main__':
    unittest.main()

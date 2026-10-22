"""Bounded structural package inspection, never executes or installs a VPK."""
import hashlib
from pathlib import Path
import struct
import sys
import zipfile


def sfo_strings(data):
    if len(data) < 20 or data[:4] != b'\0PSF':
        raise ValueError('Invalid SFO header')
    _, _, keys, values, count = struct.unpack_from('<5I', data)
    if count > 64 or 20 + count * 16 > len(data):
        raise ValueError('Invalid SFO index')
    result = {}
    for i in range(count):
        key, kind, length, capacity, offset = struct.unpack_from('<HHIII', data, 20 + 16 * i)
        if length > capacity or values + offset + length > len(data):
            raise ValueError('Invalid SFO value range')
        start = keys + key
        end = data.find(b'\0', start, values)
        if not (keys <= start < values) or end < start:
            raise ValueError('Invalid SFO key')
        name = data[start:end].decode('ascii')
        if name in result:
            raise ValueError('Duplicate SFO key')
        if kind == 0x0204:
            result[name] = data[values + offset:values + offset + length].rstrip(b'\0').decode('utf-8')
    return result


def inspect(folder):
    package = folder / 'stt_vita_prototype.vpk'
    expected = (folder / 'SHA256SUMS').read_text().split()[0]
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError('VPK checksum mismatch')
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != {'eboot.bin', 'sce_sys/param.sfo', 'assets/hunter-body.pose.json', 'assets/quaternius-sword.pose.json', 'assets/QUATERNIUS-NOTICE.txt'}:
            raise ValueError('Unexpected package contents')
        if sum(entry.file_size for entry in archive.infolist()) > 4 * 1024 * 1024:
            raise ValueError('Unexpected uncompressed size')
        if not archive.read('eboot.bin').startswith(b'SCE\0'):
            raise ValueError('Invalid SELF header')
        sfo = sfo_strings(archive.read('sce_sys/param.sfo'))
        if sfo.get('TITLE_ID') != 'STTP00001' or sfo.get('TITLE') != 'STT Vita Prototype' or sfo.get('APP_VER') != '00.15':
            raise ValueError('Application identity mismatch; do not install')
        for path, digest in {
            'assets/hunter-body.pose.json': '9881699bf7f3de544038755f9b8251877593ecde60c4927d00406f9be170c861',
            'assets/quaternius-sword.pose.json': 'da8c1a437b2d090acda2f3f3b7fbe61bd548c665537b72a9134c994da6c09dd8',
        }.items():
            if hashlib.sha256(archive.read(path)).hexdigest() != digest:
                raise ValueError('Body or third-party sword sample mismatch')
        notice=archive.read('assets/QUATERNIUS-NOTICE.txt').decode('utf-8')
        if 'Quaternius' not in notice or 'CC0' not in notice or 'https://quaternius.itch.io/lowpoly-medieval-weapons' not in notice:
            raise ValueError('Missing third-party author/license notice')
    print('PASS structural VPK / SELF / SFO identity inspection: STTP00001')
    print('SHA256:', actual)


if __name__ == '__main__':
    inspect(Path(sys.argv[1]))

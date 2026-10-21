"""Inspect the generated developer VPK; does not install or execute it."""
import hashlib
from pathlib import Path
import sys
import zipfile


def inspect(folder):
    package = folder / 'stt_vita_monitor.vpk'
    expected = (folder / 'SHA256SUMS').read_text().split()[0]
    actual = hashlib.sha256(package.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError('VPK checksum mismatch')
    with zipfile.ZipFile(package) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != {'eboot.bin', 'sce_sys/param.sfo'}:
            raise ValueError('unexpected package contents: ' + repr(names))
        if sum(entry.file_size for entry in archive.infolist()) > 4 * 1024 * 1024:
            raise ValueError('unexpected package size')
        if not archive.read('eboot.bin').startswith(b'SCE\x00'):
            raise ValueError('invalid SELF header')
        if not archive.read('sce_sys/param.sfo').startswith(b'\x00PSF'):
            raise ValueError('invalid SFO header')
    print('PASS: VPK checksum, expected contents and SELF/SFO headers')
    print('VPK SHA256:', actual)


if __name__ == '__main__':
    inspect(Path(sys.argv[1]))

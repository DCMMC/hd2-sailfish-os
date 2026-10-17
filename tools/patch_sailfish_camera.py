#!/usr/bin/env python3
"""Apply the HD2 camera/PMEM compatibility patches with byte guards."""
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


PATCHES = {
    Path('system/lib/libmemalloc.so'): {
        'input': 'ec16da8907b72e251e5f70cf16b3e323d9b313416a7eacc2c77eb86091056118',
        'output': '868b2332a8e3f771dbea290cd9e6a5bca23fbda10170bec60577ba4071625ee5',
        'edits': [(0x26e2, '12d4', '00bf'), (0x2f16, '03', '07')],
    },
    Path('usr/libexec/droid-hybris/system/lib/libmemalloc.so'): {
        'input': 'ec16da8907b72e251e5f70cf16b3e323d9b313416a7eacc2c77eb86091056118',
        'output': '868b2332a8e3f771dbea290cd9e6a5bca23fbda10170bec60577ba4071625ee5',
        'edits': [(0x26e2, '12d4', '00bf'), (0x2f16, '03', '07')],
    },
    Path('system/lib/hw/camera.qsd8k.so'): {
        'input': '3ceb3be0f5d9b11689a130fa5908de13504ce4ac07f500a99bb6e7d3e3d7ce5d',
        'output': 'a260b71ba571df3903032c9b4574b004a13c5c938da1c97e4a1dda0ffe4fb26b',
        'edits': [(0x2f48, '36d1', '00bf')],
    },
    Path('usr/libexec/droid-hybris/system/lib/libgui.so'): {
        'input': 'd89b5621bee2464d2c820085e73278cdcba00a6cf4ff7a05e4df66772c14e092',
        'output': '40b728cd154e5288c4b900296d9b66d9f8e87d73b0e66d27fb1f9bd9ff921e30',
        'edits': [
            (0x26560, '72b9', '0ee0'),
            (0x26a44, '4bb9', '09e0'),
            (0x26a5a, 'b9f1030f0dd9', '4ff000090de0'),
            (0x26b56, '1a9bdbf80010ddf80cc0', '0df1580bddf80cc08ae0'),
        ],
    },
    Path('usr/lib/gstreamer-1.0/libgstdroid.so'): {
        'input': 'd062c11fef9f1b4c38d41842caa73b2e8c320c49822b474eaac1146903a0f22f',
        'output': '552869c938e1bc75530ef672bae051701a5be13dc16f3ffc8ca110b9da92b553',
        'edits': [
            (0xccb2, '70', '37'),
            (0x121bc, '85fb0356069dd117', '1d46934607e000bf'),
            (0x12b52, 'c1ebac11', '294600bf'),
            (0x12b5a, 'c3ebae13', '234600bf'),
            (0x12bbe, 'c3ebae13', '234600bf'),
            (0x12c06, 'c3eba413', '434600bf'),
            (0x12d06, 'c1ebac11', '294600bf'),
            (0x12d0e, 'c3ebae13', '234600bf'),
            (0x12d72, 'c3ebae13', '234600bf'),
            (0x12dba, 'c3eba413', '434600bf'),
        ],
    },
    Path('usr/lib/libqgsttools_p.so.1.0.0'): {
        'input': '6b4ac9b6b1e32c0a142a4034f41fb3855d13a86279417c8d84ca7533092a84fd',
        'output': '6a67a0c9324d8937e1b1fab7e3f8a572d5f73f6ed2ed3b1a05a51ba3d0608730',
        # xvimagesink needs an XVideo overlay and another contiguous PMEM
        # buffer. This Wayland/fbdev adaptation provides glimagesink instead.
        'edits': [(0x1d68c, '7876', '676c')],
    },
}

OLD_CAPS = (b'video/x-raw(memory:DroidVideoMetaData), format = (string) {YV12}, '
            b'width = (int) [ 1, max ], height = (int) [ 1, max ], '
            b'framerate = (fraction) [ 0, max ], metadata = (boolean) { FALSE, TRUE }')
NEW_CAPS = (b'video/x-raw, format = (string) {YV12}, width = (int) [ 1, max ], '
            b'height = (int) [ 1, max ], framerate = (fraction) [ 0, max ], '
            b'metadata = (boolean) { FALSE, TRUE }')


def digest(data):
    return sha256(data).hexdigest()


def patch_file(path, spec):
    original = path.read_bytes()
    current = digest(original)
    if current == spec['output']:
        return False
    if current != spec['input']:
        raise ValueError(f'{path}: unexpected SHA-256 {current}')

    data = bytearray(original)
    for offset, before_hex, after_hex in spec['edits']:
        before = bytes.fromhex(before_hex)
        after = bytes.fromhex(after_hex)
        if len(before) != len(after):
            raise ValueError(f'{path}: length-changing edit at 0x{offset:x}')
        if data[offset:offset + len(before)] != before:
            raise ValueError(f'{path}: byte guard failed at 0x{offset:x}')
        data[offset:offset + len(before)] = after

    if path.name == 'libgstdroid.so':
        offset = original.find(OLD_CAPS)
        if offset != 0x23698:
            raise ValueError(f'{path}: droid video caps found at {offset:#x}')
        replacement = NEW_CAPS.ljust(len(OLD_CAPS), b'\0')
        data[offset:offset + len(OLD_CAPS)] = replacement

    result = bytes(data)
    actual = digest(result)
    if actual != spec['output']:
        raise ValueError(f'{path}: patched SHA-256 {actual}, expected {spec["output"]}')
    path.write_bytes(result)
    return True


def patch_stage(stage):
    changed = []
    for relative, spec in PATCHES.items():
        if patch_file(stage / relative, spec):
            changed.append(relative)
    return changed


def main():
    for relative in patch_stage(ROOT / 'work/sailfish-stage'):
        print(relative)


if __name__ == '__main__':
    main()

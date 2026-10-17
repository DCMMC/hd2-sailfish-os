#!/usr/bin/env python3
"""Offline verification for the rebuilt Sailfish alpha4 ext4 image."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / 'out/sailfish-alpha4/HD2-SF'
IMAGE = FOLDER / 'rootfs.ext4'
MANIFEST = ROOT / 'logs/sailfish-alpha4-patch-manifest.json'
RESULT = ROOT / 'logs/sailfish-alpha4-verification.json'


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def main():
    if IMAGE.stat().st_size != 2048 * 1024 * 1024:
        raise ValueError('rootfs is not exactly 2 GiB')
    fsck = subprocess.run(['e2fsck', '-fn', str(IMAGE)], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if fsck.returncode not in (0, 1):
        raise RuntimeError(fsck.stdout)

    manifest = json.loads(MANIFEST.read_text())
    kernel_sha256 = sha(FOLDER / 'zImage')
    if kernel_sha256 != manifest['kernel_sha256']:
        raise ValueError('zImage hash does not match the patch manifest')
    verified = 0
    with tempfile.TemporaryDirectory() as temporary:
        temporary = Path(temporary)
        for index, item in enumerate(manifest['files']):
            relative = item['path']
            if 'symlink' in item:
                stat = subprocess.run(
                    ['debugfs', '-R', f'stat /{relative}', str(IMAGE)], text=True,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True).stdout
                match = re.search(r'Fast link dest: "(.*)"', stat)
                if not match or match.group(1) != item['symlink']:
                    raise ValueError(f'symlink mismatch: {relative}')
            else:
                output = temporary / str(index)
                subprocess.run(['debugfs', '-R', f'dump /{relative} {output}', str(IMAGE)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
                if sha(output) != item['sha256']:
                    raise ValueError(f'hash mismatch: {relative}')
            item['image_verified'] = True
            verified += 1

    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    result = {
        'release': manifest['release'],
        'image': str(IMAGE.relative_to(ROOT)),
        'bytes': IMAGE.stat().st_size,
        'sha256': sha(IMAGE),
        'e2fsck_returncode': fsck.returncode,
        'e2fsck_summary': fsck.stdout.strip().splitlines()[-1],
        'manifest_files_read_back': verified,
        'all_manifest_files_verified': True,
        'kernel_sha256': kernel_sha256,
        'kernel_matches_manifest': True,
        'kernel_boot_tested_from_magldr_sd': True,
        'power_key_boot_evidence': 'kernel #5 reports KEY_POWER; injected event3 KEY_POWER entered visible tklock; HD2 protocol-A edge swipe returned to unlocked with Lipstick PID stable',
        'power_key_compatibility': 'MCE display remains logically on because this framebuffer has no fb_blank; long press still displays the stock power menu',
        'cold_boot_tested': False,
    }
    RESULT.write_text(json.dumps(result, indent=2) + '\n')
    (IMAGE.parent / 'PATCH-MANIFEST.json').write_bytes(MANIFEST.read_bytes())
    (IMAGE.parent / 'VERIFICATION.json').write_bytes(RESULT.read_bytes())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

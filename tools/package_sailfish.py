#!/usr/bin/env python3
"""Package the alpha4 SD image with matching MAGLDR files and source records."""
import hashlib
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT.parent / 'hd2-sailfish-os'
if not (PUBLIC / 'README.md').is_file():
    PUBLIC = ROOT
FOLDER = ROOT / 'out/sailfish-alpha4/HD2-SF'
IMAGE = FOLDER / 'rootfs.ext4'
OUTPUT = ROOT / 'out/hd2-sailfish-2.0.1.11-alpha4-SD.zip'


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def main():
    if not IMAGE.is_file() or IMAGE.stat().st_size != 2048 * 1024 * 1024:
        raise SystemExit('Expected the verified 2 GiB Sailfish alpha4 image')
    for name in ('zImage', 'initrd.gz', 'BUILD-STATUS.json',
                 'PATCH-MANIFEST.json', 'VERIFICATION.json'):
        if not (FOLDER / name).is_file():
            raise SystemExit(f'Missing {name}; run preparation, image build and verification first')

    (FOLDER / 'INSTALL.en.txt').write_text(
        'Sailfish OS 2.0.1.11 / HTC HD2 SD alpha4 (experimental)\n\n'
        'Extract and copy the complete HD2-SF directory to the root of the first FAT32 SD partition.\n'
        'In MAGLDR choose Services > BootSettings > AD SD Dir > HD2-SF, then Boot AD SD.\n'
        'For automatic startup select Boot source > Android from SD and set AlwaysMenu to NO.\n'
        'This is an SD image, not a recovery-flashable ZIP. Do not flash it to NAND.\n'
        'Back up an existing rootfs.ext4 before replacement; it contains user settings and data.\n'
        'Working on the test device: display, touch/unlock, speaker, vibration, Wi-Fi, camera capture and Gallery pinch zoom.\n'
        'Alpha4 revision 2 adds the HD2 GPIO power-key fix for lock/wake and the long-press power menu.\n'
        'Calls/data, GPS, Bluetooth, sensors, suspend and non-speaker audio routes remain unverified.\n'
        'USB ADB and the USB RNDIS root rescue shell at 192.168.2.15:2323 start automatically.\n'
        'Official OTA updates are unsupported. Read BUILD-STATUS.json and VERIFICATION.json.\n')
    (FOLDER / 'INSTALL-zh.txt').write_text(
        'Sailfish OS 2.0.1.11 / HTC HD2 SD alpha4（实验版）\n\n'
        '解压后把完整 HD2-SF 目录复制到 SD 第一分区 FAT32 根目录。\n'
        'MAGLDR 选择 Services > BootSettings > AD SD Dir > HD2-SF，然后 Boot AD SD。\n'
        '自动启动请选择 Boot source > Android from SD，并把 AlwaysMenu 设为 NO。\n'
        '这是 SD 镜像包，不是 Recovery 卡刷包，不要刷入 NAND。\n'
        '覆盖前请备份原 rootfs.ext4，其中包含用户设置和数据。\n'
        '实机已确认：显示、触摸/解锁、扬声器、振动、Wi-Fi、相机拍照和相册双指缩放。\n'
        'alpha4 第二版加入 HD2 GPIO 电源键修复，用于锁屏/唤醒和长按电源菜单。\n'
        '通话/数据、GPS、蓝牙、传感器、休眠和非扬声器音频路由仍未验证。\n'
        'USB ADB 与 USB RNDIS 192.168.2.15:2323 root 救援终端默认开启。\n'
        '不支持官方 OTA；完整范围见 BUILD-STATUS.json 与 VERIFICATION.json。\n')
    names = ['zImage', 'initrd.gz', 'rootfs.ext4', 'BUILD-STATUS.json',
             'PATCH-MANIFEST.json', 'VERIFICATION.json']
    (FOLDER / 'SHA256SUMS').write_text(''.join(
        f'{sha(FOLDER / name)}  {name}\n' for name in names))

    temporary = OUTPUT.with_suffix('.zip.tmp')
    if temporary.exists():
        temporary.unlink()
    with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for path in sorted(FOLDER.iterdir()):
            archive.write(path, 'HD2-SF/' + path.name)
        archive.write(ROOT / 'sources.lock.json', 'SOURCES.json')
        for name in ('README.md', 'README.zh-CN.md', 'NOTICES.md'):
            if (PUBLIC / name).is_file():
                archive.write(PUBLIC / name, name)
        archive.write(ROOT / 'out/sailfish-native-abi.json', 'STATIC-DEPENDENCIES.json')
        for path in sorted((ROOT / 'tools').glob('*sailfish*.py')):
            archive.write(path, 'patch-sources/tools/' + path.name)
        for path in sorted((ROOT / 'configs').glob('sailfish-*')):
            archive.write(path, 'patch-sources/configs/' + path.name)
        for name in ('configure_debug.py', 'build_kernel.py', 'firmware.py',
                     'hd2_usb_root.py'):
            archive.write(ROOT / 'tools' / name, 'patch-sources/tools/' + name)
        archive.write(ROOT / 'native/hd2-audio-unmute.S',
                      'patch-sources/native/hd2-audio-unmute.S')
        archive.write(ROOT / 'prebuilt/hd2-audio-unmute',
                      'patch-sources/prebuilt/hd2-audio-unmute')
        archive.write(ROOT / 'configs/hd2-unpack.sh',
                      'patch-sources/configs/hd2-unpack.sh')
    temporary.replace(OUTPUT)
    OUTPUT.with_suffix('.zip.sha256').write_text(f'{sha(OUTPUT)}  {OUTPUT.name}\n')
    print(OUTPUT, OUTPUT.stat().st_size)


if __name__ == '__main__':
    main()

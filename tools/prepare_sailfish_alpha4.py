#!/usr/bin/env python3
"""Freeze the live-tested post-alpha3 fixes into the clean alpha4 stage."""
import hashlib
import json
from pathlib import Path
import re
import shutil

from configure_sailfish_hardware import configure_hardware
from configure_sailfish_legacy import configure_legacy
from configure_sailfish_camera_booster import configure as configure_camera_booster
from optimize_sailfish_camera_qml import optimize as optimize_camera_qml
from patch_sailfish_camera import PATCHES as CAMERA_PATCHES, patch_stage as patch_camera


ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / 'work/sailfish-stage'
FOLDER = ROOT / 'out/sailfish-alpha4/HD2-SF'
MANIFEST = ROOT / 'logs/sailfish-alpha4-patch-manifest.json'


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def main():
    if not STAGE.is_dir():
        raise SystemExit('Missing work/sailfish-stage')

    configure_legacy(STAGE)
    configure_hardware(STAGE)
    patch_camera(STAGE)
    optimize_camera_qml(STAGE)
    configure_camera_booster(STAGE)

    (STAGE / 'etc/hw-release').write_text(
        'NAME="HTC HD2"\nID=leo\nMER_HA_DEVICE=leo\nMER_HA_VENDOR=htc\n'
        'VERSION_ID=alpha4\nPRETTY_NAME="HTC HD2 SD alpha4"\n')
    build_prop = STAGE / 'system/build.prop'
    text = re.sub(r'(?m)^ro\.hd2\.port\.status=.*$',
                  'ro.hd2.port.status=alpha4-experimental', build_prop.read_text())
    build_prop.write_text(text)

    limitations = [
        'Calls, cellular data, GPS, Bluetooth, sensors, suspend and power consumption are not validated',
        'Earpiece, wired-headset, Bluetooth and telephony audio routes are not validated',
        'Gallery zoom intentionally scales one display-sized texture and does not reveal full-resolution pixels',
        'Camera cold start remains slow on the single-core CPU; measured tap-to-HAL-open time was about 6.9 seconds',
        'Whole-process cgroup migration through the legacy tasks interface remains unverified',
        'Donor RPM metadata remains; official OTA updates are unsupported',
        'Post-alpha3 rootfs patches were tested incrementally on the phone; the clean image has offline verification but no separate cold-boot test',
    ]
    status = {
        'status': 'alpha4 revision 2: power-key kernel fix plus the live-tested post-alpha3 rootfs fixes',
        'sailfish': '2.0.1.11',
        'android': 'NexusHD2 CM11 V4.0 / Android 4.4.1',
        'hybris_donor': 'anzu 2.0.1.11 alpha4 / CM11',
        'kernel': 'tytung 2.6.32 kitkat #5; HD2 GPIO power key reports Linux KEY_POWER',
        'user_confirmed': [
            'normal 480x800 display', 'touch taps', 'swipe/unlock',
            'built-in speaker sound', 'vibration', 'Wi-Fi connection',
            'camera preview and capture', 'Gallery image open and pinch zoom',
        ],
        'verified': [
            'MAGLDR default SD boot on the development installation',
            'systemd, Android HAL, USB ADB and USB root rescue shell',
            'Wayland server-side allocation fix with physical swipe/unlock',
            'Wi-Fi connection confirmed by the owner',
            'Camera preview/capture confirmed by the owner; tap-to-HAL-open measured at about 6.9 seconds',
            'Gallery PID stable across repeated pinch gestures',
            'QDSP speaker device gain changed from controlled -1500 to +500 by PulseAudio ExecStartPost',
            'Ringtone acoustic loopback rose from about -42 dBFS to about -14 dBFS; owner confirmed sound',
            'Kernel #5 booted from MAGLDR SD; htcleo-keypad advertises KEY_POWER and mce opened its evdev node',
        ],
        'hardware_notes': {
            'display_touch_unlock': 'working and user-confirmed',
            'audio': '44.1 kHz PulseAudio plus post-start QDSP RX unmute/device gain; built-in speaker user-confirmed',
            'vibration': 'ngfd media.vibra uses droid-vibrator; user-confirmed',
            'wifi': 'bcm4329 WEXT scan/runtime fixes; connection user-confirmed',
            'camera': 'preview and capture user-confirmed; HD2 allocator/droidmedia/GStreamer patches and camera-only booster included',
            'gallery': 'display-sized single texture avoids Adreno 200 PMEM exhaustion during open and pinch zoom',
            'power_key': 'dedicated GPIO key reports KEY_POWER instead of KEY_END; short-press lock/wake and long-press menu are handled by mce',
        },
        'usb_debug': {
            'adb': 'always on, including early boot',
            'adb_authentication': False,
            'root_rescue': 'USB RNDIS 192.168.2.15:2323 always on; systemd rescue also uses port 23',
            'early_adb_uid': 'may be 2000 before Android properties are initialized',
        },
        'clean_image_cold_boot_tested': False,
        'known_unresolved': limitations,
        'unresolved_risks': limitations,
    }
    status_text = json.dumps(status, ensure_ascii=False, indent=2) + '\n'
    (STAGE / 'etc/hd2-build-status.json').write_text(status_text)
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / 'BUILD-STATUS.json').write_text(status_text)
    shutil.copy2(ROOT / 'out/sailfish-kernel-experimental/zImage', FOLDER / 'zImage')
    shutil.copy2(ROOT / 'out/sailfish-bringup/HD2-SF/initrd.gz', FOLDER / 'initrd.gz')

    old = json.loads((ROOT / 'logs/sailfish-patch-manifest.json').read_text())
    paths = {item['path'] for item in old['files']}
    paths.update(str(path) for path in CAMERA_PATCHES)
    paths.update({
        'etc/hd2-build-status.json', 'etc/hw-release', 'system/build.prop',
        'etc/systemd/user/pulseaudio.service.d/hd2-device-volume.conf',
        'usr/local/sbin/hd2-audio-unmute',
        'etc/systemd/system/droid-hal-init.service.d/hd2-memlock.conf',
        'etc/systemd/user/lipstick.service.d/hd2-start-timeout.conf',
        'etc/systemd/user/osupdate-check.service',
        'etc/systemd/user/osupdate-check.timer',
        'var/lib/environment/nemo/60-multimedia.conf',
        'usr/share/jolla-camera/pages/capture/CaptureView.qml',
        'usr/share/booster-silica-qt5/preload.qml',
        'usr/share/booster-camera-qt5/preload.qml',
        'usr/share/booster-camera-qt5/preload-camera.qml',
        'usr/libexec/mapplauncherd/booster-camera-qt5',
        'usr/lib/systemd/user/booster-camera-qt5.service',
        'usr/lib/systemd/user/user-session.target.wants/booster-camera-qt5.service',
        'usr/local/sbin/hd2-camera-booster-preload',
        'etc/systemd/system/hd2-camera-booster-preload.service',
        'etc/systemd/system/basic.target.wants/hd2-camera-booster-preload.service',
        'usr/share/applications/jolla-camera.desktop',
        'usr/lib/qt5/qml/Sailfish/Gallery/ImageViewer.qml',
        'usr/lib/qt5/qml/Sailfish/Gallery/private/ZoomableImage.qml',
    })
    files = []
    for relative in sorted(paths):
        path = STAGE / relative
        if path.is_symlink():
            files.append({'path': relative, 'symlink': str(path.readlink()), 'image_verified': False})
        elif path.is_file():
            files.append({'path': relative, 'sha256': sha(path), 'image_verified': False})
        else:
            raise FileNotFoundError(relative)

    manifest = {
        'release': 'Sailfish 2.0.1.11 HTC HD2 SD alpha4',
        'files': files,
        'binary_patches': old['binary_patches'],
        'camera_binary_patches': {
            str(path): {key: value for key, value in spec.items() if key in ('input', 'output', 'edits')}
            for path, spec in CAMERA_PATCHES.items()
        },
        'kernel_patches': list(dict.fromkeys(old['kernel_patches'] + [
            'configs/sailfish-hd2-power-key.patch',
        ])),
        'kernel_sha256': sha(FOLDER / 'zImage'),
        'initrd_sha256': sha(FOLDER / 'initrd.gz'),
        'runtime_evidence': status['verified'],
        'limitations': limitations,
        'hardware': status['hardware_notes'],
        'source_commit_before_release': 'f15b9d90daa5c0fbd85d05f7777cf10c1ee2ee9a',
        'alpha4_asset_revision': 2,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(FOLDER)
    print(MANIFEST)


if __name__ == '__main__':
    main()

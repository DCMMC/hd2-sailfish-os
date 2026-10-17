#!/usr/bin/env python3
"""Create a camera-only, one-shot QML preload for the single-core HTC HD2."""
from hashlib import sha256
from pathlib import Path

from optimize_sailfish_camera_qml import (
    PRELOAD_INPUT,
    PRELOAD_OUTPUT,
    digest,
    optimize_preload,
)


ROOT = Path(__file__).resolve().parents[1]
SHARED_PRELOAD = Path('usr/share/booster-silica-qt5/preload.qml')
CAMERA_PRELOAD_DIR = Path('usr/share/booster-camera-qt5')
BOOSTER_SOURCE = Path('usr/libexec/mapplauncherd/booster-silica-qt5')
BOOSTER_TARGET = Path('usr/libexec/mapplauncherd/booster-camera-qt5')
BOOSTER_INPUT = '387313e0fbdf494e349801c0aa3ad9d0f8f44770dc01440f4fd55881d19bc7cb'
BOOSTER_OUTPUT = 'b281708f4bba089dea758247ae9017f5d1bde66b32cb9c952e9b15380a3f59b8'
DESKTOP = Path('usr/share/applications/jolla-camera.desktop')


def undigest(data):
    return sha256(data).hexdigest()


def restore_generic_preload(text):
    """Reverse an older build which put the camera graph in the shared booster."""
    current = digest(text)
    if current == PRELOAD_INPUT:
        return text
    if current != PRELOAD_OUTPUT:
        raise ValueError(f'{SHARED_PRELOAD}: unexpected SHA-256 {current}')

    text = text.replace(
        'import Sailfish.Silica 1.0\n'
        'import "../jolla-camera/pages" as JollaCameraPages\n'
        'import "../jolla-camera/pages/capture" as JollaCameraCapture\n',
        'import Sailfish.Silica 1.0\n', 1)
    text = text.replace(
        '    // Compile the exact top-level URL in the booster\'s QQmlEngine. Invoking the\n'
        '    // camera later reuses this component cache without creating camera hardware.\n'
        '    property var hd2CameraComponent\n'
        '    Component.onCompleted: {\n'
        '        hd2CameraComponent = Qt.createComponent(\n'
        '                    "file:///usr/share/jolla-camera/camera.qml",\n'
        '                    Component.Asynchronous)\n'
        '    }\n\n', '', 1)
    text = text.replace(
        '            FirstTimeUseCounter {}\n\n'
        '            // HD2: compile the camera\'s large QML graph while the Silica\n'
        '            // booster is idle, instead of after the user taps the icon.\n'
        '            JollaCameraPages.CameraPage { }\n'
        '            JollaCameraCapture.CaptureView { }\n',
        '            FirstTimeUseCounter {}\n', 1)
    if digest(text) != PRELOAD_INPUT:
        raise ValueError(f'{SHARED_PRELOAD}: failed to restore generic preload')
    return text


def write(stage, relative, content, mode=0o644):
    path = stage / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    path.chmod(mode)
    return relative


def link(stage, relative, target):
    path = stage / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        path.unlink()
    path.symlink_to(target)
    return relative


def configure(stage):
    changed = []

    shared = stage / SHARED_PRELOAD
    generic = restore_generic_preload(shared.read_text())
    shared.write_text(generic)
    changed.append(SHARED_PRELOAD)
    camera = optimize_preload(generic)
    changed.append(write(stage, CAMERA_PRELOAD_DIR / 'preload-camera.qml', camera))
    # The root preparation service installs the heavy copy before the user
    # session. It later restores this file to the generic graph so replacement
    # camera boosters stay cheap while the camera is open.
    changed.append(write(stage, CAMERA_PRELOAD_DIR / 'preload.qml', generic))

    source = (stage / BOOSTER_SOURCE).read_bytes()
    target = stage / BOOSTER_TARGET
    if target.exists() and undigest(target.read_bytes()) == BOOSTER_OUTPUT:
        patched = target.read_bytes()
    else:
        if undigest(source) != BOOSTER_INPUT:
            raise ValueError(f'{BOOSTER_SOURCE}: unexpected SHA-256 {undigest(source)}')
        if source.count(b'silica-qt5') != 2:
            raise ValueError(f'{BOOSTER_SOURCE}: expected two type strings')
        patched = source.replace(b'silica-qt5', b'camera-qt5')
        if undigest(patched) != BOOSTER_OUTPUT:
            raise ValueError(f'{BOOSTER_TARGET}: output SHA-256 {undigest(patched)}')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(patched)
    target.chmod((stage / BOOSTER_SOURCE).stat().st_mode & 0o7777)
    changed.append(BOOSTER_TARGET)

    desktop = stage / DESKTOP
    text = desktop.read_text()
    if '--type=camera-qt5' not in text:
        if text.count('--type=silica-qt5') != 1:
            raise ValueError(f'{DESKTOP}: expected one silica launcher')
        text = text.replace('--type=silica-qt5', '--type=camera-qt5', 1)
        desktop.write_text(text)
    changed.append(DESKTOP)

    user_unit = Path('usr/lib/systemd/user/booster-camera-qt5.service')
    changed.append(write(stage, user_unit, '''[Unit]
Description=HD2 camera QML launch booster
After=lipstick.service
Requires=dbus.socket lipstick.service

[Service]
Type=notify
ExecStart=/usr/libexec/mapplauncherd/booster-camera-qt5 --systemd
Restart=always
RestartSec=1

[Install]
WantedBy=user-session.target
'''))
    changed.append(link(stage,
        Path('usr/lib/systemd/user/user-session.target.wants/booster-camera-qt5.service'),
        '../booster-camera-qt5.service'))

    # Remove the early live-test copy. /usr/lib is where this Sailfish release
    # installs and enables all other mapplauncherd booster units.
    for relative in (Path('etc/systemd/user/booster-camera-qt5.service'),
                     Path('etc/systemd/user/user-session.target.wants/booster-camera-qt5.service')):
        path = stage / relative
        if path.exists() or path.is_symlink():
            path.unlink()

    changed.append(write(stage, Path('usr/local/sbin/hd2-camera-booster-preload'), '''#!/bin/sh
# Load the expensive camera graph once, then make replacement boosters light.
set -eu
camera_dir=/usr/share/booster-camera-qt5
generic=/usr/share/booster-silica-qt5/preload.qml
cp -f "$camera_dir/preload-camera.qml" "$camera_dir/preload.qml"
count=0
while ! pgrep -f '^/usr/libexec/mapplauncherd/booster-camera-qt5' >/dev/null 2>&1; do
    count=$((count + 1))
    [ "$count" -lt 120 ] || exit 0
    sleep 1
done
sleep 60
cp -f "$generic" "$camera_dir/preload.qml"
''', 0o755))
    changed.append(write(stage, Path('etc/systemd/system/hd2-camera-booster-preload.service'), '''[Unit]
Description=Prepare one-shot HD2 camera QML preload
After=local-fs.target
Before=user@100000.service

[Service]
Type=simple
ExecStart=/usr/local/sbin/hd2-camera-booster-preload

[Install]
WantedBy=basic.target
'''))
    changed.append(link(stage,
        Path('etc/systemd/system/basic.target.wants/hd2-camera-booster-preload.service'),
        '../hd2-camera-booster-preload.service'))
    return changed


def main():
    for relative in configure(ROOT / 'work/sailfish-stage'):
        print(relative)


if __name__ == '__main__':
    main()

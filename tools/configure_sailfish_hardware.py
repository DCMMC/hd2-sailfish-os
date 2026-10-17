#!/usr/bin/env python3
"""HD2 audio, haptic and camera settings for the CM11/Sailfish adaptation."""
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]


def configure_hardware(stage):
    changed = []
    relative = Path('etc/pulse/arm_droid_default.pa')
    target = stage/relative
    text = target.read_text()
    # HD2's primary output accepts 44100 Hz; the Xperia 48000 Hz request
    # makes audio.primary.qsd8k return -EINVAL and PulseAudio exit.
    text = re.sub(r'(?m)^(load-module module-droid-card .*\brate=)48000\b',
                  r'\g<1>44100', text)
    target.write_text(text)
    changed.append(relative)

    # Android's AudioFlinger initializes the QDSP receive-device gain through
    # /dev/msm_audio_ctl. module-droid-card controls only the PCM stream gain,
    # leaving the HD2 speaker path silent even though every PCM write succeeds.
    # Apply the missing unmute and 100% device-volume ioctls after PulseAudio has
    # opened and routed the legacy QSD8K HAL.
    relative = Path('usr/local/sbin/hd2-audio-unmute')
    target = stage/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/'prebuilt/hd2-audio-unmute', target)
    target.chmod(0o755)
    changed.append(relative)

    relative = Path('etc/systemd/user/pulseaudio.service.d/hd2-device-volume.conf')
    target = stage/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('[Service]\nExecStartPost=/usr/local/sbin/hd2-audio-unmute\n')
    changed.append(relative)

    relative = Path('usr/share/ngfd/plugins.d/resource.ini')
    target = stage/relative
    text = re.sub(r'(?m)^(media\.vibra\s*=\s*)ffmemless\s*$',
                  r'\g<1>droid-vibrator', target.read_text())
    target.write_text(text)
    changed.append(relative)

    relative = Path('system/build.prop')
    target = stage/relative
    text = re.sub(r'(?m)^(?:persist.camera.shutter.disable=.*|# Sailfish owns camera sound feedback\.)\n?', '', target.read_text())
    # CameraService otherwise waits forever for AudioFlinger while loading
    # Android shutter samples. Native Sailfish feedback uses PulseAudio.
    text = text.rstrip()+'\n\n# Sailfish owns camera sound feedback.\npersist.camera.shutter.disable=1\n'
    target.write_text(text)
    changed.append(relative)

    # QtMultimedia's autovideosrc assumes a single pad named "src". The
    # droidcamsrc element exposes vfsrc/imgsrc/vidsrc instead, so auto-detection
    # selects a fake source and repeatedly fails negotiation. Select it directly.
    relative = Path('var/lib/environment/nemo/60-multimedia.conf')
    target = stage/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('QT_GSTREAMER_CAMERABIN_SRC=droidcamsrc\n'
                      'QT_GSTREAMER_CAMERABIN_VIDEOSRC=droidcamsrc\n'
                      'QT_GSTREAMER_PLAYBIN_FLAGS=0\n'
                      'QT_GSTREAMER_CAMERABIN_FLAGS=15\n')
    changed.append(relative)

    relative = Path('etc/profile.d/developer-profile.sh')
    target = stage/relative
    text = target.read_text()
    marker = 'QT_GSTREAMER_CAMERABIN_SRC\n'
    additions = ('QT_GSTREAMER_CAMERABIN_VIDEOSRC\n'
                 'QT_GSTREAMER_CAMERABIN_FLAGS\n'
                 'QT_GSTREAMER_PLAYBIN_FLAGS\n')
    if 'QT_GSTREAMER_CAMERABIN_VIDEOSRC\n' not in text:
        if marker not in text:
            raise ValueError(f'{relative}: Qt GStreamer whitelist marker missing')
        text = text.replace(marker, marker + additions, 1)
    target.write_text(text)
    changed.append(relative)

    # The gallery's stock 3264-square textures exceed Adreno 200's contiguous
    # PMEM budget. Pinch zoom also allocates a second copy and dereferences the
    # failed native buffer. Keep one display-sized texture and scale that item.
    relative = Path('usr/lib/qt5/qml/Sailfish/Gallery/ImageViewer.qml')
    target = stage/relative
    text = target.read_text()
    text = text.replace(
        '''        if (largePhoto.source != photo.source) {\n'''
        '''            largePhoto.source = photo.source\n'''
        '''        }\n''',
        '''        // HD2: reuse the display-sized texture while zooming. Loading a second\n'''
        '''        // full image here exhausts the Adreno 200 contiguous PMEM pool and crashes.\n'''
        '''        // Scaling the existing texture keeps pinch/pan responsive and stable.\n''', 1)
    text = text.replace('            sourceSize.width: Screen.height\n',
                        '            // HD2: fit the initial texture to the physical display to avoid PMEM exhaustion.\n'
                        '            sourceSize.width: Screen.width\n', 1)
    text = text.replace(
        '''        Image {\n'''
        '''            id: largePhoto\n'''
        '''            sourceSize {\n'''
        '''                width: 3264\n'''
        '''                height: 3264\n'''
        '''            }\n''',
        '''        Image {\n'''
        '''            id: largePhoto\n'''
        '''            // Disabled on HD2: a second zoom texture cannot be allocated reliably.\n'''
        '''            visible: false\n'''
        '''            source: ""\n'''
        '''            sourceSize {\n'''
        '''                width: Screen.width\n'''
        '''                height: Screen.height\n'''
        '''            }\n''', 1)
    required = ['reuse the display-sized texture', 'sourceSize.width: Screen.width',
                'visible: false', 'source: ""']
    if not all(value in text for value in required):
        raise ValueError(f'{relative}: gallery compatibility transformation failed')
    target.write_text(text)
    changed.append(relative)

    relative = Path('usr/lib/qt5/qml/Sailfish/Gallery/private/ZoomableImage.qml')
    target = stage/relative
    text = target.read_text()
    old = '''            sourceSize {\n                width: 3264\n                height: 3264\n            }\n'''
    new = '''            // HD2: keep edit-preview textures within the Adreno 200 PMEM budget.\n            sourceSize {\n                width: Screen.width\n                height: Screen.height\n            }\n'''
    if old in text:
        text = text.replace(old, new, 1)
    else:
        text = text.replace('''            // HD2: keep edit-preview textures within the Adreno 200 PMEM budget.\n            sourceSize {\n                width: 800\n                height: 800\n            }\n''', new, 1)
    if new not in text:
        raise ValueError(f'{relative}: edit-preview texture transformation failed')
    target.write_text(text)
    changed.append(relative)

    # This archived unofficial adaptation has no supported OTA feed. Its update
    # timer wakes Store and PackageKit every eight hours, consuming scarce RAM
    # and I/O while applications launch. Manual Store use remains available.
    for name in ('osupdate-check.timer', 'osupdate-check.service'):
        relative = Path('etc/systemd/user')/name
        target = stage/relative
        if target.exists() or target.is_symlink():
            target.unlink()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to('/dev/null')
        changed.append(relative)

    # Android's mini SurfaceFlinger locks shared graphics memory. This Android
    # init predates the per-service "rlimit" option, so set resource 8
    # (RLIMIT_MEMLOCK) in the boot action and also raise the parent systemd
    # service limit. All Android graphics/media children then inherit infinity.
    relative = Path('init.rc')
    target = stage/relative
    text = target.read_text()
    text = text.replace('    rlimit memlock 4294967295 4294967295\n', '')
    nice_limit = '    setrlimit 13 40 40\n'
    memlock_limit = '    setrlimit 8 4294967295 4294967295\n'
    if memlock_limit not in text:
        if nice_limit not in text:
            raise ValueError(f'{relative}: boot setrlimit marker missing')
        text = text.replace(nice_limit, nice_limit + memlock_limit, 1)
    target.write_text(text)
    changed.append(relative)

    relative = Path('etc/systemd/system/droid-hal-init.service.d/hd2-memlock.conf')
    target = stage/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('[Service]\nLimitMEMLOCK=infinity\n')
    changed.append(relative)

    # Lipstick needs around 35-45 seconds for its first QML/GL initialization
    # on this CPU. The image-wide 30 second default kills it once and doubles
    # boot time before Silica application boosters can start.
    relative = Path('etc/systemd/user/lipstick.service.d/hd2-start-timeout.conf')
    target = stage/relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('[Service]\nTimeoutStartSec=90\n')
    changed.append(relative)
    return changed


if __name__ == '__main__':
    for relative in configure_hardware(ROOT/'work/sailfish-stage'):
        print(relative)

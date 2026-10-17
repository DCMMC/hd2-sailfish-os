#!/usr/bin/env python3
"""Reduce Jolla Camera cold-start work on the single-core HD2."""
from hashlib import sha256
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CAPTURE = Path('usr/share/jolla-camera/pages/capture/CaptureView.qml')
PRELOAD = Path('usr/share/booster-silica-qt5/preload.qml')
CAPTURE_INPUT = 'f1e5266e8cb35f9d6aedf7948684ac09ec360eb9a9fc91931d5534dbcd7af853'
CAPTURE_OUTPUT = 'b37535e6e067f47a1899c3f2baf3f1f6a0d0a901bfcd9f150b7738468057838b'
PRELOAD_INPUT = '79c6413730da6435071e69e8c518b2928cc2f3324849e25a1b886e3e541a7db7'
PRELOAD_OUTPUT = '6bbba835d8b06592c4d9da1e610b3e8e34cdfda0a042489fd8142a3730a66eb3'


def digest(text):
    return sha256(text.encode()).hexdigest()


def optimize_capture(text):
    current = digest(text)
    if current == CAPTURE_OUTPUT:
        return text
    if current != CAPTURE_INPUT:
        raise ValueError(f'{CAPTURE}: unexpected SHA-256 {current}')

    text = text.replace(
        '    property alias inButtonLayout: settingsOverlay.inButtonLayout\n',
        '    readonly property bool inButtonLayout: settingsOverlayLoader.item\n'
        '                                           ? settingsOverlayLoader.item.inButtonLayout\n'
        '                                           : false\n', 1)
    text = text.replace(
        '                || volumeDown.pressed\n'
        '                || captureButton.pressed\n',
        '                || volumeDown.pressed\n', 1)
    text = text.replace(
        '        if (!effectiveActive) {\n'
        '            settingsOverlay.open = false\n'
        '            settingsOverlay.inButtonLayout = false\n'
        '        }\n',
        '        if (!effectiveActive && settingsOverlayLoader.item) {\n'
        '            settingsOverlayLoader.item.open = false\n'
        '            settingsOverlayLoader.item.inButtonLayout = false\n'
        '        }\n', 1)
    text = text.replace(
        '        function autoFocus() {\n'
        '            settingsOverlay.close()\n',
        '        function autoFocus() {\n'
        '            if (settingsOverlayLoader.item)\n'
        '                settingsOverlayLoader.item.close()\n', 1)
    text = text.replace(
        '                    && camera.captureMode == Camera.CaptureStillImage\n'
        '                    && !captureButton.pressed\n'
        '                    && !captureView._captureOnFocus\n',
        '                    && camera.captureMode == Camera.CaptureStillImage\n'
        '                    && !captureView._captureOnFocus\n', 1)

    start = text.index('    SettingsOverlay {\n')
    marker = '\n    }\n\n    MediaKey {\n        id: volumeUp'
    end = text.index(marker, start) + len('\n    }')
    block = text[start:end]
    clock = (
        '        WallClock {\n'
        '            id: clock\n'
        '            updateFrequency: WallClock.Second\n'
        '            enabled: camera.videoRecorder.recorderState == CameraRecorder.RecordingState\n'
        '            onEnabledChanged: {\n'
        '                if (enabled) {\n'
        '                    captureView._startTime = clock.time\n'
        '                    captureView._endTime = captureView._startTime\n'
        '                } else {\n'
        '                    captureView._endTime = captureView._startTime\n'
        '                }\n'
        '            }\n'
        '        }\n')
    if '\n' + clock not in block:
        raise ValueError(f'{CAPTURE}: WallClock block missing')
    block = block.replace('\n' + clock, '', 1)
    indented = '\n'.join(('    ' + line if line else line)
                         for line in block.splitlines())
    replacement = '''    // Start the Camera object as soon as the page is ready. The stock settings
    // overlay creates hundreds of menu delegates and delays HD2 preview startup.
    // Build that overlay asynchronously while a small shutter control is usable.
    Loader {
        id: settingsOverlayLoader
        anchors.fill: parent
        asynchronous: true
        active: captureView._complete
        sourceComponent: settingsOverlayComponent
    }

    MouseArea {
        id: startupCaptureButton
        z: 10
        visible: settingsOverlayLoader.status != Loader.Ready
        enabled: captureView._canCapture && !captureView._captureOnFocus
        width: Theme.itemSizeExtraLarge
        height: Theme.itemSizeExtraLarge
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: Theme.paddingLarge
        onPressed: camera.autoFocus()
        onClicked: captureView._triggerCapture()

        Rectangle {
            anchors.centerIn: parent
            width: Theme.itemSizeSmall
            height: width
            radius: width / 2
            opacity: 0.6
            color: Theme.highlightDimmerColor
        }
        Image {
            anchors.centerIn: parent
            source: "image://theme/icon-camera-shutter-release?" +
                    (startupCaptureButton.enabled ? Theme.highlightColor : Theme.highlightDimmerColor)
        }
    }

    WallClock {
        id: clock
        updateFrequency: WallClock.Second
        enabled: camera.videoRecorder.recorderState == CameraRecorder.RecordingState
        onEnabledChanged: {
            if (enabled) {
                captureView._startTime = clock.time
                captureView._endTime = captureView._startTime
            } else {
                captureView._endTime = captureView._startTime
            }
        }
    }

    Component {
        id: settingsOverlayComponent
''' + indented + '\n    }'
    text = text[:start] + replacement + text[end:]
    if digest(text) != CAPTURE_OUTPUT:
        raise ValueError(f'{CAPTURE}: output SHA-256 {digest(text)}')
    return text


def optimize_preload(text):
    current = digest(text)
    if current == PRELOAD_OUTPUT:
        return text
    if current != PRELOAD_INPUT:
        raise ValueError(f'{PRELOAD}: unexpected SHA-256 {current}')

    text = text.replace(
        'import Sailfish.Silica 1.0\n',
        'import Sailfish.Silica 1.0\n'
        'import "../jolla-camera/pages" as JollaCameraPages\n'
        'import "../jolla-camera/pages/capture" as JollaCameraCapture\n', 1)
    text = text.replace(
        'ApplicationWindow {\n'
        '    cover: null  // don\'t create a cover - the switcher will try to show it\n',
        'ApplicationWindow {\n'
        '    // Compile the exact top-level URL in the booster\'s QQmlEngine. Invoking the\n'
        '    // camera later reuses this component cache without creating camera hardware.\n'
        '    property var hd2CameraComponent\n'
        '    Component.onCompleted: {\n'
        '        hd2CameraComponent = Qt.createComponent(\n'
        '                    "file:///usr/share/jolla-camera/camera.qml",\n'
        '                    Component.Asynchronous)\n'
        '    }\n\n'
        '    cover: null  // don\'t create a cover - the switcher will try to show it\n', 1)
    text = text.replace(
        '            FirstTimeUseCounter {}\n',
        '            FirstTimeUseCounter {}\n\n'
        '            // HD2: compile the camera\'s large QML graph while the Silica\n'
        '            // booster is idle, instead of after the user taps the icon.\n'
        '            JollaCameraPages.CameraPage { }\n'
        '            JollaCameraCapture.CaptureView { }\n', 1)
    if digest(text) != PRELOAD_OUTPUT:
        raise ValueError(f'{PRELOAD}: output SHA-256 {digest(text)}')
    return text


def optimize(stage):
    """Make the capture page lazy; camera preloading is configured separately.

    The common silica-qt5 booster is shared by every native application.  It
    must remain small, otherwise every replacement booster recompiles the
    camera QML graph and slows Gallery, Settings and other applications.
    """
    path = stage / CAPTURE
    old = path.read_text()
    new = optimize_capture(old)
    if new == old:
        return []
    path.write_text(new)
    return [CAPTURE]


def main():
    for relative in optimize(ROOT / 'work/sailfish-stage'):
        print(relative)


if __name__ == '__main__':
    main()

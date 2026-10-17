# Sailfish OS 2.0.1.11 for HTC HD2

**English** | [简体中文](README.zh-CN.md)

An unofficial SD-card port for HTC HD2 / Leo, developed on a device with 576 MB RAM and 1024 MB ROM using MAGLDR. It combines the NexusHD2 CM11 / Android 4.4.1 hardware layer, tytung's Linux 2.6.32 kernel and the archived Xperia anzu Sailfish userspace.

**[Download alpha4](https://github.com/DCMMC/hd2-sailfish-os/releases/tag/v2.0.1.11-hd2-alpha4)** · [Engineering notes (Chinese)](docs/ENGINEERING.md) · [Build notes (Chinese)](docs/BUILD.md) · [XDA post draft](docs/XDA-POST.en.md) · [Smartisan companion project](https://github.com/DCMMC/hd2-smartisan-os)

**Display, touch, swipe-to-unlock, the power button, built-in speaker sound, vibration, Wi-Fi connection, camera preview/capture and stable Gallery pinch zoom work on the test phone.** Alpha4 revision 3 keeps the corrected HD2 key mapping and adds a safe visible-lock fallback for its legacy framebuffer.

## Real-device screenshots

<img src="screenshots/applications.png" width="220" alt="Sailfish application launcher on HTC HD2"> <img src="screenshots/home.png" width="220" alt="Sailfish multitasking home screen on HTC HD2"> <img src="screenshots/camera-working.png" width="220" alt="Working Sailfish camera preview on HTC HD2">

All three are direct framebuffer captures from the running phone. The last image shows the camera patch set included in alpha4. See [screenshot provenance](screenshots/README.md).

## Status

| Feature | Status |
| --- | --- |
| MAGLDR SD boot, systemd and Android HAL | Tested on the device, including reboot |
| 480×800 display, taps and swipe-to-unlock | Confirmed by the owner |
| Power button | Kernel #5 reports the dedicated GPIO as `KEY_POWER`; short press opens a visible, swipeable lockscreen and long press opens the stock power menu. The panel/backlight stays on while locked because this framebuffer has no blank callback |
| Sound and vibration | Speaker output and vibration confirmed by the owner; speaker startup also has measured acoustic-loopback evidence. Earpiece, headset and Bluetooth audio remain untested |
| USB ADB and root rescue shell | Automatically enabled and tested |
| Wi-Fi | Connection works; confirmed by the owner after the WEXT and runtime fixes |
| Camera | Preview and capture work; HAL reaches its frame device about 6.9 seconds after a cold icon tap in the measured run |
| Gallery | Opens images and survives repeated pinch zoom; zoom uses a display-sized texture to fit Adreno 200 PMEM |
| Calls, data, GPS, Bluetooth, sensors, suspend | Not fully tested |

The fixes were tested incrementally on the phone. The alpha4 clean image passed read-back checks for 67 critical files, ZIP CRC validation and a read-only filesystem check, but it has not had a separate cold-boot cycle. Donor RPM metadata remains, and official OTA updates are not supported.

## Installation

1. Download `hd2-sailfish-2.0.1.11-alpha4-SD.zip` and its `.sha256` file. Verify the checksum.
2. Extract the ZIP and place the entire `HD2-SF` directory at the root of the SD card's first FAT32 partition. Allow at least 2.1 GiB. `rootfs.ext4` is a 2 GiB file.
3. In MAGLDR, select **Services → BootSettings → AD SD Dir → HD2-SF**, then **Boot AD SD**.
4. For automatic startup, set **Boot source → Android from SD** and **AlwaysMenu → NO**.

**This is an SD image ZIP, not a recovery-flashable ZIP. Do not flash it to NAND.** No repartitioning or changes to existing ext4/WP7 partitions are required. Save an existing rootfs before replacing it: the image also contains that installation's settings and data.

## Always-on debugging

```sh
adb devices
adb shell
adb pull /run/hd2-logs
```

ADB may run as uid 2000 during early boot. For the root rescue shell, configure the host USB RNDIS interface as `192.168.2.14/24`, then run:

```sh
telnet -b 192.168.2.14 192.168.2.15 2323
```

These endpoints start automatically without UI authorization. Runtime logs are in RAM under `/run/hd2-logs` and disappear on reboot. Early logs are in `HD2-SF/early-boot.log` on FAT32. An empty `SYSTEMD_DEBUG` file enables detailed startup logging; `DIAGNOSTIC_ONLY` stops in the initramfs diagnostic environment.

## Included fixes

- Early boot/ADB, cgroup sysfs, SECUREBITS and the ARM accept4 syscall entry.
- systemd 208 compatibility, correct bionic library paths and an active local user session.
- RGBX8888 EGL configuration, gralloc callbacks, double buffering and theme scaling.
- The Wayland server-side allocation crash that prevented reliable unlocking.
- The HD2 GPIO power button reports Linux `KEY_POWER` instead of the legacy `KEY_END`; the three-key reset combination was updated with it. MCE uses a visible-lock compatibility profile so a short press cannot leave a stale frame with touch disabled.
- 44.1 kHz PulseAudio output, automatic QDSP receive-device unmute/gain initialization, and the Android vibrator backend configuration.
- WEXT scanning/connection support and removal of a camera shutter-sound wait on absent AudioFlinger.
- HD2 camera allocator, droidmedia/GStreamer compatibility and unlimited HAL memlock fallback.
- Asynchronous camera controls plus a camera-only one-shot QML booster; the measured HAL-open delay fell from about 16.6 to 6.9 seconds without burdening every Silica application.
- Display-sized Gallery textures that prevent 3264×3264 native-buffer exhaustion during open and pinch zoom.
- Longer Lipstick startup allowance and disabled unsupported OTA polling, reducing boot-time restart and background I/O pressure.

The alpha4 release manifests include the current power-key, audio, camera, Gallery and Wi-Fi patch set. Implementations are in `build_kernel.py`, `configure_sailfish_hardware.py`, `patch_sailfish_camera.py`, `optimize_sailfish_camera_qml.py` and `configure_sailfish_camera_booster.py`; device evidence is under `logs/`.

## Source and debugging archive

`tools/`, `configs/`, `logs/` and `docs/` contain the actual scripts, probes, redacted evidence, disassembly, root causes and solutions. `sources.lock.json` pins upstream inputs. The repository includes the kernel configuration, complete local diff and compiler references; the Release also attaches the exact modified #5 kernel source. The power-key change is `configs/sailfish-hd2-power-key.patch`.

The shared archive includes companion Smartisan utilities and historical records. Earlier logs can describe superseded states. This is a binary-based adaptation, not a complete Sailfish source distribution. See [NOTICES.md](NOTICES.md) for attribution.

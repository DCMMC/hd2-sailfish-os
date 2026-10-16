# Sailfish OS 2.0.1.11 for HTC HD2

**English** | [简体中文](README.zh-CN.md)

An unofficial SD-card port for HTC HD2 / Leo, developed on a device with 576 MB RAM and 1024 MB ROM using MAGLDR. It combines the NexusHD2 CM11 / Android 4.4.1 hardware layer, tytung's Linux 2.6.32 kernel and the archived Xperia anzu Sailfish userspace.

**[Download alpha3, checksums and kernel source](https://github.com/DCMMC/hd2-sailfish-os/releases/tag/v2.0.1.11-hd2-alpha3)** · [Engineering notes (Chinese)](docs/ENGINEERING.md) · [Build notes (Chinese)](docs/BUILD.md) · [XDA post draft](docs/XDA-POST.en.md) · [Smartisan companion project](https://github.com/DCMMC/hd2-smartisan-os)

**The device owner confirmed working display, touch, swipe-to-unlock, sound and vibration. Wi-Fi and the camera remain unusable.** Further repairs were paused at the owner's request. Alpha3 is the final snapshot of this session, not a claim that the port is feature-complete.

## Real-device screenshots

<img src="screenshots/applications.png" width="240" alt="Sailfish application launcher on HTC HD2"> <img src="screenshots/home.png" width="240" alt="Sailfish multitasking home screen on HTC HD2">

Captured from the running phone immediately before publication. The black camera preview and failed browser connection are real unresolved issues. These are framebuffer captures, not mockups. See [screenshot provenance](screenshots/README.md).

## Status

| Feature | Status |
| --- | --- |
| MAGLDR SD boot, systemd and Android HAL | Tested on the device, including reboot |
| 480×800 display, taps and swipe-to-unlock | Confirmed by the owner |
| Sound and vibration | Confirmed by the owner; not every route or notification scenario was tested |
| USB ADB and root rescue shell | Automatically enabled and tested |
| Wi-Fi | Scanning partially restored; the owner still cannot use Wi-Fi |
| Camera | Sensor starts; preview allocation fails and the preview stays black |
| Calls, data, GPS, Bluetooth, sensors, suspend | Not fully tested |

The clean image includes patches tested incrementally on the phone; the repackaged image itself has not been cold-boot tested again. Donor RPM metadata remains, and official OTA updates are not supported.

## Installation

1. Download `hd2-sailfish-2.0.1.11-alpha3-SD.zip` and its `.sha256` file. Verify the checksum.
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
- 44.1 kHz PulseAudio output and the Android vibrator backend configuration.
- Partial WEXT scanning support and removal of a camera shutter-sound wait on absent AudioFlinger.

The partial Wi-Fi and camera fixes do **not** make those features usable. No final camera allocator patch was implemented. Exact changes and limitations are in [PATCH-MANIFEST.json](release/PATCH-MANIFEST.json) and [BUILD-STATUS.json](release/BUILD-STATUS.json).

## Source and debugging archive

`tools/`, `configs/`, `logs/` and `docs/` contain the actual scripts, probes, redacted evidence, disassembly, root causes and solutions. `sources.lock.json` pins upstream inputs. The release includes modified kernel source, configuration, the complete local diff and compiler references. The ROM retains the boot-tested #4 zImage, with bcm4329 rebuilt separately using the same configuration.

The shared archive includes companion Smartisan utilities and historical records. Earlier logs can describe superseded states. This is a binary-based adaptation, not a complete Sailfish source distribution. See [NOTICES.md](NOTICES.md) for attribution.

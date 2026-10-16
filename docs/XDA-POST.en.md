# [ROM][SD][MAGLDR][ALPHA] Sailfish OS 2.0.1.11 for HTC HD2

I have been working on an unofficial SD port of Sailfish OS 2.0.1.11 for the HTC HD2 / Leo. The test device has 576 MB RAM and 1024 MB ROM. This is the current experimental snapshot; hardware support is incomplete.

Display, taps, swipe-to-unlock, sound, vibration, USB ADB and the USB root rescue shell work on the test device. Wi-Fi and the camera remain unusable. Calls, mobile data, GPS, Bluetooth, sensors and suspend are not fully tested. Official OTA updates are not supported.

Download: https://github.com/DCMMC/hd2-sailfish-os/releases/tag/v2.0.1.11-hd2-alpha3

Code, English/Chinese README, real-device screenshots, debugging logs and engineering notes: https://github.com/DCMMC/hd2-sailfish-os

Verify the SHA-256, extract the ROM ZIP and copy `HD2-SF` to the root of the first FAT32 SD partition. In MAGLDR, select Services → BootSettings → AD SD Dir → HD2-SF, then Boot AD SD. The rootfs is a 2 GiB ext4 image file; allow at least 2.1 GiB free space. This is **not a recovery-flashable ZIP** and must not be flashed to NAND. No repartitioning is required. Back up an existing image before replacing it.

ADB is enabled automatically. The patches were tested incrementally on the running phone; the final clean image has not had a separate cold-boot validation cycle. Full limitations and debugging access are documented in the repository.

The release also includes the modified tytung kernel source, configuration and complete local diff. The camera sensor starts, but preview buffer allocation still fails; scanning progress does not imply working Wi-Fi connectivity.

![Real HTC HD2 screenshot](https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/main/screenshots/applications.png)

![Real HTC HD2 screenshot](https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/main/screenshots/home.png)

Credits and pinned upstream sources are recorded in the repository. Original authors retain their rights; this is an unofficial adaptation.

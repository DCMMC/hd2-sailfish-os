English: **Sailfish OS 2.0.1.11 for HTC HD2 — experimental alpha4 SD release**

Alpha4 brings the post-alpha3 hardware and application fixes into a newly rebuilt clean image. The owner confirmed display, touch, swipe-to-unlock, built-in speaker sound, vibration, Wi-Fi connection, camera preview/capture, Gallery image opening and pinch zoom on the test phone. USB ADB and the USB root rescue shell remain enabled automatically.

Changes since alpha3:

- Working Wi-Fi connection through the bcm4329 WEXT/runtime fixes.
- Working camera preview and capture through guarded HD2 allocator, droidmedia, GStreamer and Qt patches.
- A camera-only QML booster reduces measured tap-to-HAL-open time from about 16.6 to 6.9 seconds.
- Gallery uses one display-sized texture so image opening and pinch zoom fit the Adreno 200 PMEM limit.
- PulseAudio starts at 44.1 kHz and now initializes the QDSP receive-device gain; the owner confirmed speaker output.
- Unsupported OTA polling is disabled, and Lipstick receives a realistic startup timeout for the single-core CPU.

The clean alpha4 image passed a read-only ext4 check, read-back verification of 66 critical files, and ZIP CRC validation. It has not had a separate clean-image cold-boot test. Calls, mobile data, GPS, Bluetooth, sensors, suspend, power consumption and non-speaker audio routes remain unverified. Official OTA updates are unsupported.

Download `hd2-sailfish-2.0.1.11-alpha4-SD.zip` and its `.sha256` file. Extract and copy the complete `HD2-SF` folder to the first FAT32 SD partition. In MAGLDR select **Services → BootSettings → AD SD Dir → HD2-SF**, then **Boot AD SD**. This is an SD image ZIP, not a recovery-flashable ZIP. Back up an existing `rootfs.ext4` before replacing it.

[English README](https://github.com/DCMMC/hd2-sailfish-os/blob/v2.0.1.11-hd2-alpha4/README.md) · [简体中文](https://github.com/DCMMC/hd2-sailfish-os/blob/v2.0.1.11-hd2-alpha4/README.zh-CN.md) · [Engineering notes](https://github.com/DCMMC/hd2-sailfish-os/blob/v2.0.1.11-hd2-alpha4/docs/ENGINEERING.md) · [Unchanged alpha3 kernel source](https://github.com/DCMMC/hd2-sailfish-os/releases/tag/v2.0.1.11-hd2-alpha3)

---

中文：**HTC HD2 Sailfish OS 2.0.1.11 alpha4 实验版 SD ROM**

alpha4 把 alpha3 之后的实机修复装入重新生成的干净镜像。用户已确认显示、点击、滑动解锁、内置扬声器、振动、Wi-Fi 连接、相机预览/拍照，以及相册图片打开和双指缩放正常；USB ADB 与 USB root 救援入口仍默认开启。

相对 alpha3 的主要变化：

- bcm4329 WEXT 与运行时修复后 Wi-Fi 可以连接。
- HD2 allocator、droidmedia、GStreamer 与 Qt 兼容补丁恢复相机预览和拍照。
- 相机专用 QML booster 把点击到 HAL 打开的实测时间从约 16.6 秒缩短到约 6.9 秒。
- 相册改用一份屏幕尺寸纹理，避免打开图片和双指缩放时耗尽 Adreno 200 PMEM。
- PulseAudio 使用 44100 Hz，并在启动后初始化 QDSP 接收设备增益；用户已确认扬声器有声。
- 屏蔽不支持的 OTA 后台轮询，并延长 Lipstick 在单核 CPU 上的启动超时。

alpha4 干净镜像已通过只读 ext4 检查、66 个关键文件逐项回读和 ZIP CRC 检查，但尚未单独进行干净镜像冷启动。通话、蜂窝数据、GPS、蓝牙、传感器、休眠、耗电及非扬声器音频路由仍未验证；不支持官方 OTA。

下载 `hd2-sailfish-2.0.1.11-alpha4-SD.zip` 和同名 `.sha256`。解压后把完整 `HD2-SF` 目录放到 SD 第一分区 FAT32 根目录。MAGLDR 选择 **Services → BootSettings → AD SD Dir → HD2-SF**，然后 **Boot AD SD**。这是 SD 镜像包，不是 Recovery 卡刷包；覆盖前请备份原 `rootfs.ext4`。

<img src="https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/v2.0.1.11-hd2-alpha4/screenshots/applications.png" width="220" alt="HD2 Sailfish applications"> <img src="https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/v2.0.1.11-hd2-alpha4/screenshots/home.png" width="220" alt="HD2 Sailfish home"> <img src="https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/v2.0.1.11-hd2-alpha4/screenshots/camera-working.png" width="220" alt="HD2 Sailfish camera"> <img src="https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/v2.0.1.11-hd2-alpha4/screenshots/gallery-pinch-zoom.png" width="220" alt="HD2 Sailfish Gallery pinch zoom">

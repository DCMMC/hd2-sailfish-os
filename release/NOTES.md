本阶段最终实验版 alpha3，适用于 HTC HD2 / Leo + MAGLDR，FAT32 内 2 GiB ext4 镜像启动。按用户要求暂停继续修复，发布当前成果。

- 用户确认显示、点击、滑动解锁、声音和振动正常；USB ADB 与 root 救援入口默认开启。
- **Wi-Fi 和相机仍不可用。** Wi-Fi 扫描曾返回网络，但用户仍无法使用；相机绕过 AudioFlinger 等待后仍在预览缓冲分配处失败。
- 包含启动/ADB、cgroup、SECUREBITS、accept4、systemd 208、bionic 路径、用户会话、RGBX/gralloc、44100 Hz 音频与 Android 振动配置补丁；保留 WEXT 扫描及相机等待的部分修复。
- 通话、数据、GPS、蓝牙、传感器、休眠和耗电未完成验证；不支持官方 OTA。补丁在运行手机上增量测试，重新打包的干净镜像没有再次冷启动。

下载 `hd2-sailfish-2.0.1.11-alpha3-SD.zip` 和同名 `.sha256`。解压后把整个 `HD2-SF` 放在 SD 第一分区 FAT32 根目录，MAGLDR 的 `AD SD Dir` 选择 `HD2-SF`，然后 `Boot AD SD`。这不是 Recovery 卡刷包，不刷 NAND。覆盖旧 rootfs 会覆盖原用户设置，请先保存旧镜像。

内核源码附件包含本次修改后的完整 tytung 内核、.config、完整 diff、补丁和工具链来源。ROM 中 zImage 保持已启动验证的 #4，bcm4329 模块在同配置上单独重编。

[安装、调试与源码](https://github.com/DCMMC/hd2-sailfish-os/tree/v2.0.1.11-hd2-alpha3) · [根因、解决方案及未完成项](https://github.com/DCMMC/hd2-sailfish-os/blob/v2.0.1.11-hd2-alpha3/docs/ENGINEERING.md)

<img src="https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/v2.0.1.11-hd2-alpha3/screenshots/applications.png" width="240" alt="HD2 Sailfish applications"> <img src="https://raw.githubusercontent.com/DCMMC/hd2-sailfish-os/v2.0.1.11-hd2-alpha3/screenshots/home.png" width="240" alt="HD2 Sailfish home">

截图在发布前从真实 HD2 framebuffer 采集。代码、补丁、探针、脱敏调试记录、来源锁定、校验和及解决方案均已归档。

# 调试经过与解决方案

alpha3 于 2026-10-17 冻结；用户随后要求继续修复。本页前半部分保留 alpha3 当时的调查记录，文末“alpha3 之后的实机修复”记录当前结果。这些后续补丁已收入 alpha4。

## 早期启动与 systemd

| 故障 | 已采用的处理 | 证据/实现 |
| --- | --- | --- |
| BusyBox applet 指向尚不存在的 /proc/self/exe | 先挂载 proc 再安装 applet 链接 | `configs/sailfish-init`、早期启动日志 |
| 静态 adbd 在属性区未初始化时崩溃 | 给 bionic property trie 的空指针增加保护 | `tools/patch_sailfish_adbd.py`、`logs/sailfish-adbd-patch.json` |
| cgroup 挂载点缺失 | 回移 cgroup sysfs kobject 初始化 | `configs/sailfish-cgroup-sysfs.patch` |
| systemd 208 写 cgroup.procs 失败 | cg_attach 改写旧内核 tasks；不声称实现完整的多线程进程迁移 | `tools/patch_sailfish_systemd.py` |
| SECUREBITS 不可用 | 内核启用 CONFIG_SECURITY_FILE_CAPABILITIES | `configs/sailfish-built.config` |
| journald 不能 accept4 | 为 ARM EABI syscall 366 接入内核已有 accept4 实现 | `configs/sailfish-arm-accept4.patch`、`tools/hd2-accept4-probe.c` |
| 服务退出 206/OOM_ADJUST | systemd 208 无法通过 drop-in 清除设置标志；生成移除 OOMScoreAdjust 的完整 unit override | `tools/configure_sailfish_legacy.py` |
| Android init/libc 崩溃 | Android 可执行程序使用 base bionic；仅日志 libcutils/liblog 从 lib-dev-alog 取用 | `usr/bin/droid/droid-hal-startup.sh` 的生成逻辑 |
| 用户会话/DBus 权限异常 | 创建 /run/user/100000；用 console 注册 active nemo/seat0 会话 | 同上；旧内核没有 tty0/active，不能按 donor VT7 启动 |

主机修复只针对 2.6.32 与 systemd 208 的组合。`tasks` 方案主要用于 exec 前的服务子进程，移动已存在的多线程进程仍未验证。

## 图形与滑动解锁

Qt HWC 插件请求 alpha=8，但 HD2 framebuffer 是 RGBX8888。将插件 `0xecea` 的 `0821` 改为 `0021`，即 alpha size 8→0。使用双 framebuffer 缓冲、1.0 倍主题资源及竖屏默认值。

HD2 的 alloc/free 回调偏移是 64/68，donor 使用 68/72。具体修改见 `tools/patch_sailfish_gralloc.py` 和 `logs/sailfish-gralloc-patch.json`。这包括 fbdev、HWC window、普通 native buffer 和 Wayland 服务端分配路径。

锁屏不能滑动的关键故障由 GDB 捕获：Wayland 客户端申请缓冲时，`libhybris-eglplatformcommon.so + 0x5f62` 使用错误的回调偏移，宽度 234 被传入 gralloc_free 当成指针。PC 在 `gralloc.qsd8k.so + 0x1520`，调用者为 common 库 `+0x5f72`。将 `d0f844c0` 改为 `d0f840c0` 后，注入滑动可解锁且 Lipstick PID 不变，随后用户确认真实手指滑动恢复。

证据：`logs/sailfish-first-boot/lipstick-lock-crash-gdb.txt`、`logs/sailfish-wayland-allocation-fix.json`。没有修改 SIM PIN 或设备锁验证；最初的 SIM 等待判断没有作为最终根因。

## 声音与振动

PulseAudio 的 donor 配置要求 48000 Hz，但 HD2 primary 输出只接受 44100 Hz，导致打开输出流返回 -EINVAL 并退出。将 `module-droid-card` 的 rate 改为 44100 后，primary sink 能正常创建，但后续实机复测发现扬声器仍然无声。

最终诊断确认 PulseAudio 已把非零 PCM 数据连续写入 `/dev/msm_pcm_out`：`AUDIO_GET_CONFIG`、`AUDIO_SET_CONFIG`、`AUDIO_START`、`AUDIO_SET_VOLUME` 和 3072 字节写入均返回成功，内核也加载扬声器 ACDB 607 并调用 `htcleo_speaker_enable(1)`。缺失的是 Android AudioFlinger 通常执行、而 `module-droid-card` 没有执行的 QDSP 接收设备增益初始化。PCM 流音量与 QDSP 设备音量是两层独立控制；前者为 100% 时，后者仍可停在最低增益。

`native/hd2-audio-unmute.S` 是一个不依赖 libc 的 ARM EABI 小程序，对 `/dev/msm_audio_ctl` 执行 `AUDIO_SET_RX_MUTE(0)` 和 `AUDIO_SET_VOLUME(100)`。`pulseaudio.service` 的 systemd user drop-in 在每次 PulseAudio 启动后调用该程序。验证时先把设备增益强制设为 -1500，再重启 PulseAudio；`ExecStartPost` 返回 0，内核记录增益恢复为 +500。没有再次手工执行 ioctl 的铃声回录从静音基线约 -42 dBFS 上升到约 -14 dBFS，用户随后确认有声音。

振动 sysfs 权限和 Android HAL 调用本身可用；直接 250 ms 测试及 test_vibrator 返回成功。NGFD 的 `media.vibra` 资源映射由 ffmemless 改为 droid-vibrator，原有 Qt Android 振动插件保留。用户确认振动恢复；这不等于已验证每一种通知/触觉事件。最终配置与手机内容比对后合入镜像。

代码：`tools/configure_sailfish_hardware.py`、`native/hd2-audio-unmute.S`；可重复构建所用的小型预编译程序为 `prebuilt/hd2-audio-unmute`。集成和回读记录：`logs/sailfish-alpha3-hardware.json`、`sailfish-alpha3-image.log`、`logs/sailfish-audio-device-volume-fix.json`。

## Wi-Fi：部分进展，功能仍不可用

bcm4329 初始加载缺少正确固件参数；延后加载并传入 firmware_path、nvram_path 后出现 wlan0。随后发现 Android CSCAN 编译分支直接拒绝标准 WEXT SIOCSIWSCAN，日志为 `Scan from SIOCGIWSCAN not supported`。

移除 wl_iw_set_scan / wl_iw_iscan_set_scan 中两个明确拒绝分支，保留 Android 私有扫描实现，重编 bcm4329.ko 并在手机重新加载。ConnMan scan 调用成功，GetServices 当次枚举 7 项，但用户明确反馈 Wi-Fi 仍不能使用。**不能把“扫描返回网络”写成“Wi-Fi 已修好”。**

补丁：`configs/sailfish-bcm4329-wext-scan.patch`，构建入口 `tools/build_kernel.py`。alpha3 的 zImage 保持已启动验证的 #4；模块是在相同内核配置上单独重编的。内核源码归档含全部本地变更和 .config。

## 相机：解除一个阻塞，预览仍失败

GDB 栈确认相机打开时阻塞于：

```text
CameraService::loadSound
  -> CameraService::newMediaPlayer
  -> MediaPlayer::MediaPlayer
  -> AudioSystem::newAudioSessionId
  -> AudioSystem::get_audio_flinger
  -> 等待不存在的 media.audio_flinger
```

Sailfish 使用 PulseAudio。设置已有 CM 属性 `persist.camera.shutter.disable=1` 后，相机传感器和 HAL 能启动；Sailfish 自己的相机音效仍走 native feedback。没有启动额外 AudioFlinger 与 PulseAudio 争用设备。

此后失败点为 minisf 的 `GraphicBufferAllocator::alloc(768,432,2,0x103)` 返回 -ENOMEM，随后 BufferQueue 报无法再次 dequeue，预览黑屏。调查到 HD2 PMEM/allocator 路径，但尚未证明具体分配失败的最终根因；不要把“PMEM 池被桌面占满”的推测当成定论。

临时 `debug.composition.type=gpu` 没有解决问题，**未合入发布镜像**。未实施新的 allocator 二进制补丁。相机分辨率仍有 Xperia donor 默认值，后续应先查询 HAL 支持范围再适配；本次按用户要求停在这里。

证据：`logs/sailfish-first-boot/minimedia-audio-wait-gdb.txt`、`minisf-allocator.txt`、`release-android.log`、`logs/minisf-disassembly.txt`；黑屏截图在 `screenshots/camera-known-issue.png`。

## 调试入口和证据边界

USB ADB 与 2323 root 救援口早于 systemd 图形会话启动。`tools/hd2_usb_root.py` 绑定主机 USB 地址，避免主机代理误把远端同名 IP 的连接当成手机。

截图使用真实 fb0 字节及 pan 页面；单纯 screencap 或旧缓冲不能作为当前画面证据。手机时钟未设置，日志中的 2014 日期不是真实调试日期。

未验证项目包括通话、蜂窝数据、GPS、蓝牙、传感器、休眠和耗电。alpha3 打包时没有再次做干净镜像冷启动。

## alpha3 之后的实机修复（2026-10-18）

用户继续测试后确认 Wi-Fi 已能连接。相机的最终阻塞不是单一的分辨率设置，而是旧 qsd8k HAL、droidmedia、GStreamer caps、Qt camerabin 和 HD2 PMEM 回退之间的一组 ABI/运行时问题。当前修复包括：

- `QT_GSTREAMER_CAMERABIN_VIDEOSRC=droidcamsrc`，避免 camerabin 按普通 `src` pad 使用多 pad 的 droidcamsrc。
- 对 `libmemalloc.so`、`camera.qsd8k.so`、hybris `libgui.so`、`libgstdroid.so` 和 `libqgsttools_p.so.1.0.0` 做带输入/输出 SHA-256 与偏移校验的二进制修改。
- 在 Android init 全局设置 memlock rlimit，并给 `droid-hal-init` 设置无限 memlock。HD2 的 32 MiB 连续 PMEM 映射仍可能失败，但 ashmem 回退不再因 `EAGAIN` 失败。
- `CaptureView.qml` 异步创建大型设置面板，先启动 Camera 对象并提供临时快门按钮。
- 新建 `camera-qt5` 专用 mapplauncherd booster。开机只预编译一次相机 QML，60 秒后把替补 booster 的 preload 恢复为轻量 Silica 图；普通相册、设置等应用不再承担相机预编译开销。

基准冷启动从点击到 HAL 打开约 16.6 秒；预编译测量中点击 uptime 889.60，frame0 在 896.49 打开，约 6.9 秒。`screenshots/camera-working.png` 确认预览和控制按钮正常，用户确认可以拍照。证据见 `logs/sailfish-camera-preload-timing.log` 与 `logs/sailfish-camera-current-regression.log`。

相册点击图片时的崩溃与双指缩放崩溃有同一根因：stock QML 申请 3264×3264 原图纹理，缩放时又申请第二份纹理，超过 Adreno 200 可用的连续 PMEM，随后 EGL native buffer 失败并触发 SIGSEGV。当前 QML 只保留一份 480×800 显示纹理，缩放时变换现有纹理，不再载入第二份原图。两次协议 A 双指注入后 `jolla-gallery` PID 均保持 3472；截图为 `screenshots/gallery-pinch-zoom.png`，记录为 `logs/sailfish-gallery-pinch-regression.log`。限制是放大后不会获得原图像素级细节。

此外，Lipstick 启动超时放宽至 90 秒；不受支持的 OTA 检查 service/timer 被屏蔽，以减少 576 MB 设备上的 Store/PackageKit 后台 I/O。所有变化已固化在构建脚本中并收入 alpha4 ROM ZIP。

## alpha4 第二版：电源键修复（2026-10-18）

HD2 板级文件原先让独立 GPIO 电源键上报 Linux `KEY_END`（107）。Android 可以通过 `.kl` 把 107 别名为 POWER，但 Sailfish 的 MCE 直接读取 evdev，只处理 `KEY_POWER`（116），所以按键不会锁屏、唤醒或弹出长按菜单。

`configs/sailfish-hd2-power-key.patch` 只把独立 GPIO 电源键改为 `KEY_POWER`；底部矩阵中的挂断键继续保持 `KEY_END`。三键强制重启组合也同步改用 `KEY_POWER`。新 #5 zImage 已从 MAGLDR SD 启动，`htcleo-keypad` 的能力位同时保留 107 并新增 116，MCE 启动时打开了 `/dev/input/event3`。内核、输入能力和 MCE 文件描述符证据见 `logs/sailfish-power-key-alpha4-r2.log`。

# 调试经过、解决方案与停止点

冻结日期：2026-10-17。用户最后确认声音、振动恢复，并要求暂停其余修复、归档并发布。此后只进行截图、已有补丁集成和发布准备。

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

PulseAudio 的 donor 配置要求 48000 Hz，但 HD2 primary 输出只接受 44100 Hz，导致打开输出流返回 -EINVAL 并退出。将 `module-droid-card` 的 rate 改为 44100 后，primary sink 正常创建，低音量测试音 paplay 返回 0，用户确认有声音。

振动 sysfs 权限和 Android HAL 调用本身可用；直接 250 ms 测试及 test_vibrator 返回成功。NGFD 的 `media.vibra` 资源映射由 ffmemless 改为 droid-vibrator，原有 Qt Android 振动插件保留。用户确认振动恢复；这不等于已验证每一种通知/触觉事件。最终配置与手机内容比对后合入镜像。

代码：`tools/configure_sailfish_hardware.py`。集成和回读记录：`logs/sailfish-alpha3-hardware.json`、`sailfish-alpha3-image.log`。

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

未验证项目包括通话、蜂窝数据、GPS、蓝牙、传感器、休眠和耗电。此次最终打包在干净镜像中集成现有补丁；没有再覆盖用户正在使用的完整 rootfs，也没有再次做干净镜像冷启动。

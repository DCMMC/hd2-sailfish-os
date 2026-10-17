# 构建与复现

本仓库是历史二进制用户空间的移植与调试归档，不是完整 Sailfish 系统源码树。`sources.lock.json` 锁定 NexusHD2、anzu donor、内核、工具链及参考代码。

## 输入布局

先核对下载哈希，再准备：

| 路径 | 内容 |
| --- | --- |
| `work/hd2-base/system/` | NexusHD2 V4.0 的 system |
| `work/base-boot/` | NexusHD2 boot 和 META-INF |
| `work/base-ramdisk/` | NexusHD2 NativeSD initrd 解包目录 |
| `work/base-permissions.txt` | NexusHD2 updater-script 权限规则 |
| `work/sailfish-anzu-rootfs/` | anzu alpha4 2.0.1.11 rootfs |
| `work/sailfish-anzu-metadata.json` | extract_rootfs.py 保留的数字 UID/GID/mode |
| `sources/kernel-tytung/`、`sources/toolchain-4.4.3/` | 锁定提交的内核与 ARM 工具链 |
| `sources/device-leo/` | 锁定设备树；包含早期启动使用的静态 BusyBox |

主机工具：Python 3、requirements.txt 依赖、make/GCC/binutils、Perl、e2fsprogs/debugfs、fakeroot、cpio/gzip/zip、dconf 和 adb。内核交叉工具链使用 ARM GCC 4.4.3。

## 入口

```sh
python3 tools/build_kernel.py
python3 tools/build_sailfish_boot.py
python3 tools/assemble_sailfish.py
python3 tools/prepare_sailfish_alpha4.py
fakeroot -- python3 tools/make_ext4.py work/sailfish-stage \
  out/sailfish-alpha4/HD2-SF/rootfs.ext4 \
  --metadata work/sailfish-anzu-metadata.json \
  --permissions work/base-permissions.txt \
  --size-mib 2048 --label HD2-SF
python3 tools/verify_sailfish_alpha4.py
python3 tools/package_sailfish.py
```

注意保留 Linux 用户空间的数字权限，不能套用全 Android 的权限模板。stage/image 已存在时脚本会拒绝覆盖。alpha4 使用 `out/sailfish-alpha4/HD2-SF`，`package_sailfish.py` 输出 alpha4 ZIP。

图形、adbd、systemd 和相机补丁脚本从指定 donor 文件及预期字节生成产物；不能替换输入版本后跳过断言。`configure_sailfish_hardware.py` 持久化音频、振动、相册显存、memlock、Lipstick 超时与 OTA 后台任务修复；其中 QDSP 设备音量辅助程序的源码和构建产物分别为 `native/hd2-audio-unmute.S` 与 `prebuilt/hd2-audio-unmute`。`patch_sailfish_camera.py` 处理相机 HAL/droidmedia/GStreamer 二进制；`optimize_sailfish_camera_qml.py` 和 `configure_sailfish_camera_booster.py` 负责异步相机界面及专用一次性预编译。`finalize_sailfish_release.py` 只对应旧 alpha3 冻结镜像，不应再用于当前 post-alpha3 构建。

QDSP 辅助程序是无 libc 依赖的 ARM EABI 静态文件，可用锁定工具链逐字节重建：

```sh
sources/toolchain-4.4.3/bin/arm-eabi-gcc -nostdlib -static \
  -Wl,--build-id=none -o prebuilt/hd2-audio-unmute native/hd2-audio-unmute.S
sources/toolchain-4.4.3/bin/arm-eabi-strip prebuilt/hd2-audio-unmute
sha256sum prebuilt/hd2-audio-unmute
# 2804757d73048e86b0d7af5d1a289f658bdb19ef48f57b2d7c52db54ce74317d
```

`sailfish_abi_report.py` 只检查明显缺库/缺符号，不能证明 HAL 私有结构、Binder 或 GPU 缓冲协议兼容。最终内核配置为 `configs/sailfish-built.config`；`sailfish-all-kernel-changes.patch` 是相对锁定内核提交的完整本地 diff，含现代 Perl 兼容处理。

## 内核源码 Release 附件

alpha3 Release 的 `hd2-sailfish-alpha3-kernel-source.tar.gz` 是旧 #4 内核归档。alpha4 第二版附件 `hd2-sailfish-alpha4-kernel-source.tar.gz` 对应当前 #5。它加入 `configs/sailfish-hd2-power-key.patch`，把独立 GPIO 电源键从 `KEY_END` 改为 `KEY_POWER`，并同步三键重启组合。`configs/sailfish-all-kernel-changes.patch`、`configs/sailfish-built.config` 和 `tools/build_kernel.py` 也已对应 #5 内核。建议 out-of-tree 编译，使用 `ARCH=arm`、相应 `CROSS_COMPILE` 和 `HOSTCFLAGS='-O2 -fcommon'`。

发布的 zImage 是已从 MAGLDR SD 启动验证的 #5。启动后 `htcleo-keypad` 能力位包含 `KEY_POWER=116`，MCE 已打开对应 `/dev/input/event3`；记录见 `logs/sailfish-power-key-alpha4-r2.log`。重建整个内核会改变构建时间/编号，不保证与发布二进制逐字节一致。

发布 ZIP 内是展开的 2 GiB ext4 镜像。仓库只保留 Sailfish 移植的构建、调试和验证工具；一般安装按 README 复制目录，不执行分区或格式化。

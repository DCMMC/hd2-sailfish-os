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
fakeroot -- python3 tools/make_ext4.py work/sailfish-stage \
  out/sailfish-alpha0/HD2-SF/rootfs.ext4 \
  --metadata work/sailfish-anzu-metadata.json \
  --permissions work/base-permissions.txt \
  --size-mib 2048 --label HD2-SF
python3 tools/package_sailfish.py
```

注意保留 Linux 用户空间的数字权限，不能套用全 Android 的权限模板。stage/image 已存在时脚本会拒绝覆盖。`sailfish-alpha0` 是历史目录名，当前 package_sailfish.py 输出 alpha3 ZIP。

图形、adbd、systemd 补丁脚本从指定 donor 文件和预期字节生成产物；不能替换输入版本后跳过断言。`configure_sailfish_hardware.py` 持久化当前音频、振动和相机等待修复。`finalize_sailfish_release.py` 是本次现有镜像的冻结集成入口，依赖归档中的 manifest/BUILD-STATUS，使用 debugfs 写入并回读五个改动文件；不是全新构建必需的通用步骤。

`sailfish_abi_report.py` 只检查明显缺库/缺符号，不能证明 HAL 私有结构、Binder 或 GPU 缓冲协议兼容。最终内核配置为 `configs/sailfish-built.config`；`sailfish-all-kernel-changes.patch` 是相对锁定内核提交的完整本地 diff，含现代 Perl 兼容处理。

## 内核源码 Release 附件

`hd2-sailfish-alpha3-kernel-source.tar.gz` 包含带本地变更的完整内核源码、COPYING、.config、各项补丁、完整 diff、构建脚本及工具链来源。修改已应用，不要重复打同一补丁。建议 out-of-tree 编译，使用 `ARCH=arm`、相应 `CROSS_COMPILE` 和 `HOSTCFLAGS='-O2 -fcommon'`。

发布的 zImage 是已实机验证的 #4；WEXT 修改仅影响外部 bcm4329 模块，后续单独重编并装入 alpha3。重建整个内核会改变构建时间/编号，不保证与发布二进制逐字节一致。

## 压缩传输

Release ZIP 内是展开的 2 GiB ext4 镜像。向手机传输时也可通过 package_transfer.py 的 `prepare('sailfish-alpha0/HD2-SF')` 生成 gzip，使用 Recovery ADB 上传并在手机解压。只调用该函数即可准备一个系统；脚本 main 默认同时准备两个系统。

仓库中 install_sd/recovery_sd 等脚本保留了本次特定 SD 卡的维护前提，不是通用安装器。一般安装按 README 复制目录，不执行分区或格式化。

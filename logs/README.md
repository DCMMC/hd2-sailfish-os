# Debug evidence archive

These records are a chronological engineering archive from the shared HD2 workspace. Earlier records can say UNTESTED/pending or describe failed experiments; current results are in README and release/BUILD-STATUS.json. archive-index.json identifies each archived log and its public SHA-256.

Network/device identifiers and credential-bearing lines have been redacted in public copies. Raw framebuffer buffers, device backups, user home directories, keys and network databases are not included. Local originals remain untouched. The phone clock was unset and reports 2014-05-20 in many logs; host capture names and monotonic times establish sequence.

Post-alpha3 regression evidence is in `sailfish-gallery-pinch-regression.log`, `sailfish-camera-preload-timing.log`, `sailfish-camera-current-regression.log` and `sailfish-audio-device-volume-fix.json`. The Gallery record keeps a stable PID across two pinch gestures. The timing record places camera HAL frame open at uptime 896.49 after a tap at 889.60, and the current record proves that the heavy camera preload is isolated from the shared Silica booster. The audio record separates successful PCM writes from the missing QDSP device gain and preserves the controlled -1500 to +500 startup test plus the acoustic-loopback measurements.

Alpha4 packaging evidence is in `sailfish-alpha4-patch-manifest.json`, `sailfish-alpha4-verification.json` and `sailfish-alpha4-package-verification.json`. These record 66 critical-file read-backs, the ext4 check, embedded-rootfs and embedded-kernel hash comparisons, and the complete ZIP CRC result. `sailfish-power-key-alpha4-r2.log` records the booted #5 kernel, the `KEY_POWER` input bitmap and MCE's open evdev descriptor. The rebuilt clean rootfs has not had a separate cold-boot test.

Smartisan records use smartisan-/hd2- prefixes and the 024341 boot capture. Sailfish records use sailfish-/minisf- and later captures. Shared recovery records preserve FAT32/iOS investigation history; they are not instructions to repartition another card.

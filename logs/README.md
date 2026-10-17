# Debug evidence archive

These records are a chronological engineering archive from the shared HD2 workspace. Earlier records can say UNTESTED/pending or describe failed experiments; current results are in README and release/BUILD-STATUS.json. archive-index.json identifies each archived log and its public SHA-256.

Network/device identifiers and credential-bearing lines have been redacted in public copies. Raw framebuffer buffers, device backups, user home directories, keys and network databases are not included. Local originals remain untouched. The phone clock was unset and reports 2014-05-20 in many logs; host capture names and monotonic times establish sequence.

Post-alpha3 regression evidence is in `sailfish-gallery-pinch-regression.log`, `sailfish-camera-preload-timing.log` and `sailfish-camera-current-regression.log`. The Gallery record keeps a stable PID across two pinch gestures. The timing record places camera HAL frame open at uptime 896.49 after a tap at 889.60, and the current record proves that the heavy camera preload is isolated from the shared Silica booster.

Smartisan records use smartisan-/hd2- prefixes and the 024341 boot capture. Sailfish records use sailfish-/minisf- and later captures. Shared recovery records preserve FAT32/iOS investigation history; they are not instructions to repartition another card.

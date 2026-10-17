#!/usr/bin/env python3
"""Install always-on ADB and the USB rescue shell in the Sailfish stage."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def configure_sailfish(stage):
    def write(name, text, mode=0o644):
        p=stage/name
        if p.is_symlink():p.unlink()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        p.chmod(mode)
    def link(name, target):
        p=stage/name
        if p.exists() or p.is_symlink():p.unlink()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.symlink_to(target)
    from patch_sailfish_adbd import main as patch_adbd
    patch_adbd()
    adbd=(ROOT/'out/sailfish-debug-tools/hd2-adbd').read_bytes()
    binary=stage/'usr/local/sbin/hd2-adbd'
    binary.write_bytes(adbd)
    binary.chmod(0o755)
    link('sbin/sh','/bin/sh')
    # BusyBox 1.17 recognizes a "busybox" basename, not "hd2-busybox".
    link('usr/local/sbin/busybox','hd2-busybox')
    write('default.prop','ro.hardware=htcleo\nro.secure=0\nro.debuggable=1\n'
          'ro.adb.secure=0\npersist.sys.usb.config=adb\npersist.service.adb.enable=1\n'
          'persist.sys.root_access=3\nservice.adb.root=1\npersist.sys.adb.shell=/bin/sh\n')
    write('usr/local/sbin/hd2-usb-setup',(ROOT/'configs/sailfish-usb-setup').read_text(),0o755)
    for name in ['adbd.service','adbd-prepare.service']:
        link('etc/systemd/system/'+name,'/dev/null')
    write('etc/systemd/system/hd2-adbd.service', '''[Unit]
Description=Always-on HD2 USB ADB
DefaultDependencies=no
After=systemd-udevd.service
Before=basic.target
Conflicts=shutdown.target
Before=shutdown.target

[Service]
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/system/bin
ExecStartPre=/usr/local/sbin/hd2-usb-setup
ExecStart=/usr/local/sbin/hd2-adbd
Restart=always
RestartSec=3
''')
    link('etc/systemd/system/basic.target.wants/hd2-adbd.service','../hd2-adbd.service')
    write('usr/local/sbin/hd2-usb-debug', '''#!/bin/sh
/usr/local/sbin/hd2-usb-setup
/usr/local/sbin/busybox ifconfig usb0 192.168.2.15 netmask 255.255.255.0 up || exit 1
exec /usr/local/sbin/busybox telnetd -F -b 192.168.2.15:23 -l /bin/sh
''',0o755)
    write('etc/systemd/system/hd2-usb-debug.service', '''[Unit]
Description=Always-on HD2 USB root rescue shell
DefaultDependencies=no
After=systemd-udevd.service
Before=basic.target
Conflicts=shutdown.target
Before=shutdown.target

[Service]
ExecStart=/usr/local/sbin/hd2-usb-debug
Restart=always
RestartSec=3
''')
    link('etc/systemd/system/basic.target.wants/hd2-usb-debug.service','../hd2-usb-debug.service')


if __name__ == '__main__':
    configure_sailfish(ROOT/'work/sailfish-stage')
    print('Updated Sailfish stage for always-on USB debugging.')

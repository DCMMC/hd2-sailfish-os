# Screenshot provenance

Captured from the running HTC HD2 on host date 2026-10-17, after the user confirmed sound and vibration and asked to stop further repairs.

| File | Original capture | Active framebuffer pan |
| --- | --- | --- |
| `applications.png` | release-apps.raw | 0,0 |
| `home.png` | release-home.raw | 0,0 |
| `camera-known-issue.png` | release-screenshot.raw | 0,800 |
| `welcome.png` | earlier sailfish-reboot-frame.png | recorded during boot debugging |

The screen is 480×800, RGBX8888; each slot is 1,536,000 bytes. Two slots were read from /dev/graphics/fb0 and the active pan was checked before and after capture. The selected slot was converted losslessly to PNG using Pillow. No image generation, layout reconstruction, or cosmetic alteration was used. The phone clock is unset and does not show the host capture date.

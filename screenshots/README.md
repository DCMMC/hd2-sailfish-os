# Screenshot provenance

Captured from the running HTC HD2 on host dates 2026-10-17 and 2026-10-18. Development continued after the published alpha3 snapshot.

| File | Original capture | Active framebuffer pan |
| --- | --- | --- |
| `applications.png` | release-apps.raw | 0,0 |
| `home.png` | release-home.raw | 0,0 |
| `camera-known-issue.png` | release-screenshot.raw | 0,800 |
| `welcome.png` | earlier sailfish-reboot-frame.png | recorded during boot debugging |
| `camera-working.png` | camera-custom.raw | 0,800 |
| `gallery-pinch-zoom.png` | gallery-final-pinch.raw | 0,800 |

The screen is 480×800, RGBX8888; each slot is 1,536,000 bytes. Two slots were read from `/dev/graphics/fb0`. The selected slot was converted losslessly to PNG using Pillow. No image generation, layout reconstruction, or cosmetic alteration was used. `camera-known-issue.png` records the historical alpha3 failure; `camera-working.png` records the later fix. The phone clock is unset and does not show the host capture date.

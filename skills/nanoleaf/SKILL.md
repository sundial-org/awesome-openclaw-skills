---
name: nanoleaf
description: Control Nanoleaf light panels via the Picoleaf CLI. Use for turning Nanoleaf on/off, adjusting brightness, setting colors (RGB/HSL), changing color temperature, or any Nanoleaf lighting control.
homepage: https://github.com/tessro/picoleaf
metadata: {"clawdbot":{"emoji":"🌈","requires":{"bins":["picoleaf"]},"install":[{"id":"brew","kind":"brew","tap":"paulrosania/command-home","formula":"paulrosania/command-home/picoleaf","bins":["picoleaf"],"label":"Install Picoleaf CLI (brew)"},{"id":"binary","kind":"shell","command":"curl -sL https://github.com/tessro/picoleaf/releases/latest/download/picoleaf_1.4.0_linux_amd64.tar.gz | tar xz -C ~/.local/bin","bins":["picoleaf"],"label":"Install Picoleaf (binary)"}]}}
---

# Picoleaf CLI

Use `picoleaf` to control Nanoleaf light panels.

Setup
1. Find Nanoleaf IP: Check router or use mDNS: `dns-sd -Z _nanoleafapi`
2. Generate token: Hold power button 5-7 sec until LED flashes, then within 30 sec run:
   `curl -iLX POST http://<ip>:16021/api/v1/new`
3. Create config file `~/.picoleafrc`:
   ```ini
   host=<ip>:16021
   access_token=<token>
   ```

Power
- `picoleaf on` - Turn on
- `picoleaf off` - Turn off

Brightness
- `picoleaf brightness <0-100>` - Set brightness percentage

Colors
- `picoleaf rgb <r> <g> <b>` - Set RGB color (0-255 each)
- `picoleaf hsl <hue> <sat> <light>` - Set HSL color
- `picoleaf temp <1200-6500>` - Set color temperature in Kelvin

Examples
- Warm dim light: `picoleaf on && picoleaf brightness 30 && picoleaf temp 2700`
- Bright blue: `picoleaf on && picoleaf brightness 100 && picoleaf rgb 0 100 255`
- Turn off: `picoleaf off`

Notes
- Default port is 16021
- Token generation requires physical access to the Nanoleaf controller
- Multiple commands can be chained with `&&`

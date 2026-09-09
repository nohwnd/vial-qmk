"""Read the live keymap out of the keyboard and write it back as keymap.c.

The board is the source of truth: whatever was tweaked in Vial lives in EEPROM
and nowhere else, so a flash would silently discard it. Reading the keymap back
and regenerating keymap.c makes the repo match the hardware before reflashing.

    python capture-keymap.py            # show the generated layers
    python capture-keymap.py --write    # update keymap.c in the repo
"""

import argparse
import re
import subprocess
import time
from pathlib import Path

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61
CMD_GET_KEYCODE = 0x04

LAYERS, ROWS, COLS = 4, 10, 7
KEYMAP_WSL = "/home/nohwnd/p/fiddly/keyboards/fiddly/keymaps/vial/keymap.c"

LAYER_NAMES = {0: "BASE", 1: "NAV / FUNKCE", 2: "VRSTVA 2", 3: "VRSTVA 3"}

# Custom keycodes, in the order the enum in keymap.c declares them.
CUSTOM_BASE = 0x7E00
CUSTOM = ["ALT_TAB", "ALT_SHIFT_TAB", "CTRL_TAB", "CTRL_SHIFT_TAB", "GRV_DICT"]

BASIC = {
    0x28: "KC_ENT", 0x29: "KC_ESC", 0x2A: "KC_BSPC", 0x2B: "KC_TAB", 0x2C: "KC_SPACE",
    0x2D: "KC_MINS", 0x2E: "KC_EQL", 0x2F: "KC_LBRC", 0x30: "KC_RBRC", 0x31: "KC_BSLS",
    0x33: "KC_SCLN", 0x34: "KC_QUOT", 0x35: "KC_GRV", 0x36: "KC_COMM", 0x37: "KC_DOT",
    0x38: "KC_SLSH", 0x39: "KC_CAPS", 0x49: "KC_INS", 0x4A: "KC_HOME", 0x4B: "KC_PGUP",
    0x4C: "KC_DEL", 0x4D: "KC_END", 0x4E: "KC_PGDN", 0x4F: "KC_RIGHT", 0x50: "KC_LEFT",
    0x51: "KC_DOWN", 0x52: "KC_UP",
    0xE0: "KC_LCTL", 0xE1: "KC_LSFT", 0xE2: "KC_LALT", 0xE3: "KC_LGUI",
    0xE4: "KC_RCTL", 0xE5: "KC_RSFT", 0xE6: "KC_RALT", 0xE7: "KC_RGUI",
}
for _i in range(26):
    BASIC[0x04 + _i] = f"KC_{chr(ord('A') + _i)}"
for _i, _d in enumerate("1234567890"):
    BASIC[0x1E + _i] = f"KC_{_d}"
for _i in range(12):
    BASIC[0x3A + _i] = f"KC_F{_i + 1}"

MOD_ORDER = [(0x01, "LCTL"), (0x02, "LSFT"), (0x04, "LALT"), (0x08, "LGUI")]


def to_source(code):
    """Render one keycode as the C expression that produces it."""
    if code == 0x0000:
        return "XXXXXXX"
    if code == 0x0001:
        return "_______"
    if code == 0x7C00:
        return "QK_BOOT"
    if CUSTOM_BASE <= code < CUSTOM_BASE + len(CUSTOM):
        return CUSTOM[code - CUSTOM_BASE]
    if code in BASIC:
        return BASIC[code]
    if 0x4000 <= code < 0x5000:                      # layer tap
        layer = (code >> 8) & 0x0F
        return f"LT({layer}, {to_source(code & 0xFF)})"
    if 0x0100 <= code < 0x2000:                      # modified keycode
        mods = (code >> 8) & 0x0F
        inner = to_source(code & 0xFF)
        for bit, tag in MOD_ORDER:
            if mods == bit:
                return f"{tag}({inner})"
        wrapped = inner
        for bit, tag in reversed(MOD_ORDER):
            if mods & bit:
                wrapped = f"{tag}({wrapped})"
        return wrapped
    return f"0x{code:04X}"


class Link:
    def __enter__(self):
        for device in hid.HidDeviceFilter(vendor_id=VENDOR_ID).get_devices():
            device.open()
            caps = device.hid_caps
            if caps.usage_page == RAW_USAGE_PAGE and caps.usage == RAW_USAGE_ID:
                self.device, self.length = device, caps.output_report_byte_length
                self.replies = []
                device.set_raw_data_handler(self.replies.append)
                return self
            device.close()
        raise SystemExit("No raw-HID interface found. Is the keyboard plugged in?")

    def __exit__(self, *_):
        self.device.close()

    def keycode(self, layer, row, col):
        self.replies.clear()
        buf = [0x00] * self.length
        buf[1], buf[2], buf[3], buf[4] = CMD_GET_KEYCODE, layer, row, col
        self.device.send_output_report(bytes(buf))
        for _ in range(30):
            time.sleep(0.01)
            if self.replies:
                reply = list(self.replies[0])
                return (reply[5] << 8) | reply[6]
        raise SystemExit(f"No reply reading layer {layer} row {row} col {col}.")


def render(grid):
    blocks = []
    for layer in range(LAYERS):
        cells = [[to_source(grid[layer][r][c]) for c in range(COLS)] for r in range(ROWS)]
        width = max(len(x) for row in cells for x in row)
        lines = [f"    /* {layer}: {LAYER_NAMES[layer]} */",
                 f"    [{layer}] = LAYOUT_split_3x6_3("]
        for half, rows in (("leva pulka", range(0, 5)), ("prava pulka", range(5, 10))):
            lines.append(f"        // {half}")
            for r in rows:
                row_text = ", ".join(x.ljust(width) for x in cells[r]).rstrip()
                last = (r == ROWS - 1)
                lines.append(f"        {row_text}" + ("" if last else ","))
            if half == "leva pulka":
                lines.append("")
        lines.append("    )" + ("," if layer < LAYERS - 1 else ""))
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="replace the keymaps block inside keymap.c")
    args = parser.parse_args()

    with Link() as link:
        grid = [[[link.keycode(l, r, c) for c in range(COLS)]
                 for r in range(ROWS)] for l in range(LAYERS)]

    body = render(grid)
    if not args.write:
        print(body)
        return

    source = subprocess.run(["wsl", "-d", "Ubuntu-24.04", "--", "cat", KEYMAP_WSL],
                            capture_output=True, text=True).stdout
    pattern = re.compile(
        r"(const uint16_t PROGMEM keymaps\[\]\[MATRIX_ROWS\]\[MATRIX_COLS\] = \{\n).*?(\n\};)",
        re.S)
    if not pattern.search(source):
        raise SystemExit("Could not find the keymaps block in keymap.c.")

    updated = pattern.sub(lambda m: m.group(1) + body + m.group(2), source)
    Path("captured-keymap.c").write_text(updated, encoding="utf-8", newline="\n")
    subprocess.run(["wsl", "-d", "Ubuntu-24.04", "--", "cp",
                    "/mnt/q/p/fiddly-firmware/captured-keymap.c", KEYMAP_WSL], check=True)
    print(f"keymap.c updated from the live keymap ({len(updated.splitlines())} lines).")


if __name__ == "__main__":
    main()

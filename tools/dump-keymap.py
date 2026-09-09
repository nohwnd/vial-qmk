"""Dump the whole keymap the keyboard is actually running, straight from EEPROM.

Reads every layer through the VIA dynamic keymap commands, which address keys
as (layer, row, column) and are resolved firmware-side, so the dump reflects
what the board really does rather than what any JSON file claims.

Rows 0-4 are the left half, rows 5-9 the right half.
"""

import time

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61
CMD_GET_KEYCODE = 0x04

LAYERS, ROWS, COLS = 4, 10, 7

BASIC = {
    0x00: "----", 0x01: "TRNS?", 0x29: "ESC", 0x2A: "BSPC", 0x2B: "TAB",
    0x2C: "SPC", 0x2D: "-", 0x2E: "=", 0x2F: "[", 0x30: "]", 0x31: "\\",
    0x33: ";", 0x34: "'", 0x35: "`", 0x36: ",", 0x37: ".", 0x38: "/",
    0x28: "ENT", 0x4C: "DEL", 0x4A: "HOME", 0x4D: "END", 0x4B: "PGUP",
    0x4E: "PGDN", 0x4F: "RIGHT", 0x50: "LEFT", 0x51: "DOWN", 0x52: "UP",
    0xE0: "LCTL", 0xE1: "LSFT", 0xE2: "LALT", 0xE3: "LGUI",
    0xE4: "RCTL", 0xE5: "RSFT", 0xE6: "RALT", 0xE7: "RGUI",
    0x01: "XXXX",
}
for i in range(26):
    BASIC[0x04 + i] = chr(ord("A") + i)
for i, digit in enumerate("1234567890"):
    BASIC[0x1E + i] = digit
for i in range(12):
    BASIC[0x3A + i] = f"F{i + 1}"

MOD_NAMES = [(0x01, "C"), (0x02, "S"), (0x04, "A"), (0x08, "G")]
CUSTOM = {0: "ALTTAB", 1: "ASHTAB", 2: "CTLTAB", 3: "CSHTAB", 4: "DICT"}


def name(code):
    if code is None:
        return "?"
    if code == 0x0000:
        return "----"
    if code == 0x0001:
        return "vvvv"          # KC_TRANSPARENT
    if code == 0x7C00:
        return "BOOT"
    if code in BASIC:
        return BASIC[code]
    if 0x7E00 <= code <= 0x7E0F:      # QK_KB_0 and friends
        return CUSTOM.get(code - 0x7E00, f"KB{code - 0x7E00}")
    if 0x5F00 <= code <= 0x5F1F:
        return CUSTOM.get(code - 0x5F00, f"KB{code - 0x5F00}")
    if 0x4000 <= code < 0x5000:       # layer tap
        return f"L{(code >> 8) & 0x0F}/{name(code & 0xFF)}"
    if 0x0100 <= code < 0x2000:       # modified keycode
        mods = "".join(tag for bit, tag in MOD_NAMES if ((code >> 8) & 0x0F) & bit)
        return f"{mods}-{name(code & 0xFF)}"
    return f"{code:04X}"


def main():
    target = None
    for device in hid.HidDeviceFilter(vendor_id=VENDOR_ID).get_devices():
        device.open()
        caps = device.hid_caps
        if caps.usage_page == RAW_USAGE_PAGE and caps.usage == RAW_USAGE_ID:
            target = device
            length = caps.output_report_byte_length
            break
        device.close()
    if target is None:
        raise SystemExit("No raw-HID interface found.")

    replies = []
    target.set_raw_data_handler(lambda data: replies.append(list(data)))

    def keycode(layer, row, col):
        replies.clear()
        buf = [0x00] * length
        buf[1], buf[2], buf[3], buf[4] = CMD_GET_KEYCODE, layer, row, col
        target.send_output_report(bytes(buf))
        for _ in range(20):
            time.sleep(0.01)
            if replies:
                return (replies[0][5] << 8) | replies[0][6]
        return None

    try:
        for layer in range(LAYERS):
            print(f"\n{'=' * 62}\nLAYER {layer}\n{'=' * 62}")
            for half, rows in (("LEFT ", range(0, 5)), ("RIGHT", range(5, 10))):
                print(f"-- {half} half --")
                for row in rows:
                    cells = [name(keycode(layer, row, col)) for col in range(COLS)]
                    print(f"  r{row}  " + " ".join(c.center(7) for c in cells))
    finally:
        target.close()


if __name__ == "__main__":
    main()

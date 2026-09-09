"""Read and write single keys in the keyboard's live EEPROM keymap over raw HID.

Uses the VIA dynamic keymap commands, which address keys as
(layer, row, column) and are computed firmware-side, so they are unaffected
by the row/column count declared in vial.json.

    python keymap-poke.py --read            # dump the right-hand thumb row
    python keymap-poke.py --set-boot        # put QK_BOOT on the right Alt key
    python keymap-poke.py --restore         # put the original keycode back
"""

import argparse
import sys
import time

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61

CMD_GET_KEYCODE = 0x04
CMD_SET_KEYCODE = 0x05

QK_BOOT = 0x7C00

# Right-half thumb key that the layout leaves on Alt, and that I never press.
BOOT_LAYER, BOOT_ROW, BOOT_COL = 0, 9, 3
ORIGINAL_KEYCODE = 0xE2  # KC_LALT

KNOWN = {
    0x00: "KC_NO", 0x2C: "KC_SPACE", 0xE0: "KC_LCTL", 0xE1: "KC_LSFT",
    0xE2: "KC_LALT", 0xE3: "KC_LGUI", 0xE6: "KC_RALT", 0x412C: "LT(1, KC_SPACE)",
    0x7C00: "QK_BOOT",
}


class RawHid:
    def __init__(self):
        self.device = None
        self.replies = []

    def __enter__(self):
        for device in hid.HidDeviceFilter(vendor_id=VENDOR_ID).get_devices():
            device.open()
            caps = device.hid_caps
            if caps.usage_page == RAW_USAGE_PAGE and caps.usage == RAW_USAGE_ID:
                self.device = device
                self.length = caps.output_report_byte_length
                device.set_raw_data_handler(self._on_data)
                return self
            device.close()
        raise SystemExit("No raw-HID interface found. Is the keyboard plugged in?")

    def __exit__(self, *_):
        if self.device:
            self.device.close()

    def _on_data(self, data):
        self.replies.append(list(data))

    def transact(self, payload):
        self.replies.clear()
        buf = [0x00] * self.length
        for i, value in enumerate(payload):
            buf[1 + i] = value
        if not self.device.send_output_report(bytes(buf)):
            raise SystemExit("Write to the keyboard failed.")
        for _ in range(20):
            time.sleep(0.05)
            if self.replies:
                return self.replies[0]
        return None

    def get_keycode(self, layer, row, col):
        reply = self.transact([CMD_GET_KEYCODE, layer, row, col])
        if reply is None:
            return None
        # reply[0] is the report id, then the echoed command and arguments
        return (reply[5] << 8) | reply[6]

    def set_keycode(self, layer, row, col, keycode):
        self.transact([CMD_SET_KEYCODE, layer, row, col,
                       (keycode >> 8) & 0xFF, keycode & 0xFF])


def describe(keycode):
    if keycode is None:
        return "no reply"
    return f"0x{keycode:04X}  {KNOWN.get(keycode, '')}".rstrip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--read", action="store_true", help="read only, change nothing")
    group.add_argument("--set-boot", action="store_true", help="put QK_BOOT on the chosen key")
    group.add_argument("--restore", action="store_true", help="put the original keycode back")
    args = parser.parse_args()

    with RawHid() as link:
        if args.read:
            print("Right-half thumb row, layer 0 (firmware rows 5-9 are the right half):")
            for col in range(7):
                print(f"  row 9 col {col}: {describe(link.get_keycode(0, 9, col))}")
            print("\nExpected from new.vil: col1 LT(1, KC_SPACE), col2 KC_LCTL, col3 KC_LALT")
            return

        current = link.get_keycode(BOOT_LAYER, BOOT_ROW, BOOT_COL)
        print(f"before: {describe(current)}")

        target = QK_BOOT if args.set_boot else ORIGINAL_KEYCODE
        link.set_keycode(BOOT_LAYER, BOOT_ROW, BOOT_COL, target)
        time.sleep(0.2)

        after = link.get_keycode(BOOT_LAYER, BOOT_ROW, BOOT_COL)
        print(f"after : {describe(after)}")

        if after != target:
            sys.exit("Write did not take effect.")
        if args.set_boot:
            print("\nPress that right thumb key to enter the bootloader.")


if __name__ == "__main__":
    main()

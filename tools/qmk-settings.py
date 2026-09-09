"""Read and write Vial's QMK Settings, the tap-hold tuning stored in EEPROM.

These are the settings Vial exposes in its QMK Settings tab. They live in
EEPROM rather than in the firmware, so flashing resets them and any tuning
done through Vial is lost without a reflash being able to bring it back.

    python qmk-settings.py                 # read the tap-hold settings
    python qmk-settings.py --classic       # restore pre-2025 tap-hold behaviour
    python qmk-settings.py --set 7=200     # set one setting by id
"""

import argparse
import time

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61

VIAL_PREFIX = 0xFE
SETTINGS_GET = 0x0A
SETTINGS_SET = 0x0B

# qsid -> (label, byte width). Widths follow the field types in qmk_settings.h.
SETTINGS = {
    1:  ("grave_esc_override", 1),
    2:  ("combo_term", 2),
    3:  ("auto_shift", 1),
    4:  ("auto_shift_timeout", 2),
    5:  ("osk_tap_toggle", 1),
    6:  ("osk_timeout", 2),
    7:  ("tapping_term", 2),
    18: ("tap_code_delay", 2),
    19: ("tap_hold_caps_delay", 2),
    20: ("tapping_toggle", 1),
    22: ("permissive_hold", 1),
    23: ("hold_on_other_key_press", 1),
    24: ("retro_tapping", 1),
    25: ("quick_tap_term", 2),
    26: ("chordal_hold", 1),
    27: ("flow_tap_term", 2),
}

# Settings that affect how a held layer-tap behaves; the rest is mouse keys.
TAP_HOLD = (7, 20, 22, 23, 24, 25, 26, 27)

# What the board behaved like before these two features existed: both off.
CLASSIC = {26: 0, 27: 0}


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

    def _send(self, payload):
        self.replies.clear()
        buf = [0x00] * self.length
        for i, value in enumerate(payload):
            buf[1 + i] = value
        self.device.send_output_report(bytes(buf))
        for _ in range(30):
            time.sleep(0.01)
            if self.replies:
                return list(self.replies[0])
        return None

    def get(self, qsid, width):
        reply = self._send([VIAL_PREFIX, SETTINGS_GET, qsid & 0xFF, qsid >> 8])
        if reply is None:
            return None, None
        status = reply[1]
        value = reply[2] if width == 1 else reply[2] | (reply[3] << 8)
        return status, value

    def set(self, qsid, width, value):
        payload = [VIAL_PREFIX, SETTINGS_SET, qsid & 0xFF, qsid >> 8, value & 0xFF]
        if width == 2:
            payload.append((value >> 8) & 0xFF)
        reply = self._send(payload)
        return None if reply is None else reply[1]


def show(link, everything=False):
    ids = sorted(SETTINGS) if everything else TAP_HOLD
    print(f"{'qsid':>5}  {'setting':<26} value")
    for qsid in ids:
        label, width = SETTINGS[qsid]
        status, value = link.get(qsid, width)
        if status is None:
            print(f"{qsid:>5}  {label:<26} no reply")
        elif status != 0:
            print(f"{qsid:>5}  {label:<26} unsupported")
        else:
            print(f"{qsid:>5}  {label:<26} {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classic", action="store_true",
                        help="turn chordal_hold and flow_tap_term off")
    parser.add_argument("--all", action="store_true",
                        help="show every setting, not just the tap-hold ones")
    parser.add_argument("--set", metavar="ID=VALUE", action="append", default=[],
                        help="set one setting, may be repeated")
    args = parser.parse_args()

    with Link() as link:
        changes = dict(CLASSIC) if args.classic else {}
        for item in args.set:
            qsid, _, value = item.partition("=")
            changes[int(qsid)] = int(value)

        if not changes:
            show(link, args.all)
            return

        print("before:")
        show(link, args.all)

        for qsid, value in changes.items():
            if qsid not in SETTINGS:
                raise SystemExit(f"Unknown setting id {qsid}.")
            label, width = SETTINGS[qsid]
            link.set(qsid, width, value)
            print(f"\nset {label} = {value}")

        time.sleep(0.3)
        print("\nafter:")
        show(link, args.all)


if __name__ == "__main__":
    main()

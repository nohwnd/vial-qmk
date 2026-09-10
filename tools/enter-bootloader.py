"""Restart the half that holds the USB cable into its bootloader, over raw HID.

This is the way to flash without opening the case or unplugging anything. It
uses the VIA id_bootloader_jump command, which Vial gates behind its unlock
state. rules.mk sets VIAL_INSECURE, so vial.c compiles vial_unlocked as 1 and
the command is always accepted.

Only the half the cable is plugged into reboots. The other half keeps running.

    python enter-bootloader.py --check    # look only, send nothing
    python enter-bootloader.py            # ask first, then jump
    python enter-bootloader.py --yes      # no prompt, for scripting
"""

import argparse
import sys
import time

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61

CMD_GET_PROTOCOL_VERSION = 0x01
CMD_BOOTLOADER_JUMP = 0x0B


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
                self.product = device.product_name
                device.set_raw_data_handler(self._on_data)
                return self
            device.close()
        raise SystemExit("No raw-HID interface found. Is the keyboard plugged in?")

    def __exit__(self, *_):
        if self.device:
            try:
                self.device.close()
            except Exception:
                # The board is already rebooting after a successful jump.
                pass

    def _on_data(self, data):
        self.replies.append(list(data))

    def send(self, payload, wait_for_reply=True):
        self.replies.clear()
        buf = [0x00] * self.length
        for i, value in enumerate(payload):
            buf[1 + i] = value
        if not self.device.send_output_report(bytes(buf)):
            raise SystemExit("Write to the keyboard failed.")
        if not wait_for_reply:
            return None
        for _ in range(20):
            time.sleep(0.05)
            if self.replies:
                return self.replies[0]
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report what was found and send nothing")
    parser.add_argument("--yes", action="store_true",
                        help="skip the confirmation prompt")
    args = parser.parse_args()

    with RawHid() as link:
        print(f"Found: {link.product}")
        print(f"  raw HID, usage page 0x{RAW_USAGE_PAGE:04X}, "
              f"report length {link.length}")

        reply = link.send([CMD_GET_PROTOCOL_VERSION])
        if reply is None:
            sys.exit("The board did not answer, so the jump would not be safe.")
        print(f"  VIA protocol version: {(reply[2] << 8) | reply[3]}")

        if args.check:
            print("\nChecked only, nothing was sent.")
            return

        if not args.yes:
            print("\nThe half holding the cable will restart into its bootloader")
            print("and stop typing until a .uf2 is copied onto the RPI-RP2 drive.")
            if input("Continue? [y/N] ").strip().lower() not in ("y", "yes"):
                print("Nothing sent.")
                return

        # The board reboots while handling this, so there is no reply to wait for.
        link.send([CMD_BOOTLOADER_JUMP], wait_for_reply=False)

    print("\nSent. The RPI-RP2 drive should appear in a moment.")
    print("Copy the firmware with: python tools/flash-when-ready.py")
    print("If nothing happens, hold ` on the left half or 6 on the right")
    print("while plugging the cable in.")


if __name__ == "__main__":
    main()

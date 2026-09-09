"""Put the USB-connected fiddly half into its RP2040 bootloader over USB.

Saves opening the case: the firmware exposes the VIA raw-HID command
id_bootloader_jump (0x0B), and rules.mk sets VIAL_INSECURE, which makes
vial.c define `int vial_unlocked = 1`, so the command is accepted without
an unlock combo.

Only the half the USB cable is plugged into reboots. Flash one, then move
the cable to the other half and run this again.

    pip install pywinusb
    python enter-bootloader.py --check    # only look, send nothing
    python enter-bootloader.py            # ask, then reboot into bootloader
"""

import argparse
import sys

try:
    from pywinusb import hid
except ImportError:
    sys.exit("Missing dependency. Run:  pip install pywinusb")

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61
CMD_BOOTLOADER_JUMP = 0x0B


def find_raw_hid():
    """Return the raw-HID interfaces the keyboard exposes, if any."""
    found = []
    for device in hid.HidDeviceFilter(vendor_id=VENDOR_ID).get_devices():
        try:
            device.open()
            caps = device.hid_caps
            if caps.usage_page == RAW_USAGE_PAGE and caps.usage == RAW_USAGE_ID:
                found.append((device, caps.output_report_byte_length))
                continue
        except Exception:
            pass
        device.close()
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report what was found and exit without sending anything")
    parser.add_argument("--yes", action="store_true",
                        help="skip the confirmation prompt")
    args = parser.parse_args()

    interfaces = find_raw_hid()
    if not interfaces:
        sys.exit("No raw-HID interface found. Is the keyboard plugged in directly "
                 "(not through a hub or KVM) and running Vial firmware?")

    device, report_length = interfaces[0]
    try:
        print(f"Found: {device.product_name}  "
              f"{device.vendor_id:#06x}:{device.product_id:#06x}  "
              f"report length {report_length}")

        if args.check:
            print("Check only, nothing sent.")
            return

        if not args.yes:
            print("\nThis reboots the half the cable is plugged into. It will stop "
                  "typing and appear as the RPI-RP2 drive.")
            if input("Continue? [y/N] ").strip().lower() not in ("y", "yes"):
                print("Cancelled.")
                return

        report = [0x00] * report_length
        report[1] = CMD_BOOTLOADER_JUMP  # byte 0 is the report ID
        device.send_output_report(bytes(report))
        print("\nSent. The half should now appear as the RPI-RP2 drive.")
        print("Copy fiddly_vial_v2.uf2 onto it, then repeat for the other half.")
    finally:
        for handle, _ in interfaces:
            handle.close()


if __name__ == "__main__":
    main()

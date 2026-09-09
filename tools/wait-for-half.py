"""Wait for a fiddly half to appear and report which firmware it runs.

The USB product id tells the halves apart: 0x0000 is the old placeholder id
still on the left half, 0xF1DD is the id this repo sets and so marks a half
that has already been reflashed.
"""

import time

from pywinusb import hid

VENDOR_ID = 0xFEED
OLD_PID = 0x0000
NEW_PID = 0xF1DD
TIMEOUT_SECONDS = 600


def current_pids():
    return {d.product_id for d in hid.HidDeviceFilter(vendor_id=VENDOR_ID).get_devices()}


def main():
    start = current_pids()
    print(f"Now connected: {[hex(p) for p in start] or 'nothing'}")
    print("Waiting for the cable to move to the left half.\n")

    deadline = time.time() + TIMEOUT_SECONDS
    was_empty = False

    while time.time() < deadline:
        pids = current_pids()

        if not pids:
            if not was_empty:
                print("  unplugged")
                was_empty = True
        elif was_empty or pids != start:
            if OLD_PID in pids:
                print("\nLeft half is up, still on the old firmware (pid 0x0000).")
                print("Its EEPROM has never been reset, so read it now.")
                return
            if NEW_PID in pids:
                print("\nA half with the new firmware is up (pid 0xF1DD) - "
                      "that is the right half, not the left one.")
                return
        time.sleep(0.5)

    print("Timed out.")


if __name__ == "__main__":
    main()

"""Show the live switch matrix so both halves can be checked without typing.

Rows 0-4 belong to the left half and rows 5-9 to the right half, because
split assigns the non-USB hand the first block of rows. Watching which rows
light up says whether the halves still talk to each other.

Uses VIA id_get_keyboard_value / id_switch_matrix_state, which the firmware
only answers while unlocked. VIAL_INSECURE leaves it unlocked.
"""

import time

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61

CMD_GET_KEYBOARD_VALUE = 0x02
VALUE_SWITCH_MATRIX_STATE = 0x03

MATRIX_ROWS = 10
MATRIX_COLS = 7
DURATION_SECONDS = 60

replies = []


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

    target.set_raw_data_handler(lambda data: replies.append(list(data)))

    print("Watching the matrix. Press keys on the LEFT half.")
    print("Rows 0-4 are the left half, rows 5-9 the right half.\n")

    seen_left = set()
    seen_right = set()
    deadline = time.time() + DURATION_SECONDS

    try:
        while time.time() < deadline:
            replies.clear()
            buf = [0x00] * length
            buf[1] = CMD_GET_KEYBOARD_VALUE
            buf[2] = VALUE_SWITCH_MATRIX_STATE
            target.send_output_report(bytes(buf))

            time.sleep(0.05)
            if not replies:
                continue

            # reply[0] report id, [1] command, [2] value id, then one byte per row
            rows = replies[0][3:3 + MATRIX_ROWS]
            for index, value in enumerate(rows):
                for col in range(MATRIX_COLS):
                    if value & (1 << col):
                        where = seen_left if index < 5 else seen_right
                        if (index, col) not in where:
                            where.add((index, col))
                            half = "LEFT " if index < 5 else "RIGHT"
                            print(f"  {half} row {index} col {col}")
            time.sleep(0.02)
    finally:
        target.close()

    print(f"\nLeft half keys seen : {len(seen_left)}")
    print(f"Right half keys seen: {len(seen_right)}")
    if seen_left:
        print("\nThe left half is reporting through the split link, so its old "
              "firmware still talks to the new firmware on the right.")
    else:
        print("\nNo left-half activity was seen.")


if __name__ == "__main__":
    main()

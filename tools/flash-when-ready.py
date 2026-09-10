"""Wait for an RP2040 bootloader drive and copy the firmware onto it.

The board mounts as a mass-storage device labelled RPI-RP2 and reboots by
itself once the .uf2 has been written, so the copy is the whole flash.

    python flash-when-ready.py NEW_RIGHT.uf2
    python flash-when-ready.py NEW_LEFT.uf2 --seconds 60
"""

import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path


def find_bootloader_drive():
    """Return the drive root of a mounted RP2040 bootloader, or None."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "Get-Volume | Where-Object { $_.FileSystemLabel -like '*RPI*' } "
         "| Select-Object -ExpandProperty DriveLetter"],
        capture_output=True, text=True,
    )
    letters = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    return f"{letters[0]}:\\" if letters else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware", help="the .uf2 to copy")
    parser.add_argument("--seconds", type=int, default=900,
                        help="how long to wait for the drive")
    args = parser.parse_args()

    firmware = Path(args.firmware)
    if not firmware.exists():
        beside_script = Path(__file__).with_name(firmware.name)
        if beside_script.exists():
            firmware = beside_script
        else:
            sys.exit(f"Firmware not found: {args.firmware}")

    print(f"Firmware: {firmware} ({firmware.stat().st_size} bytes)")
    print(f"Waiting for the RPI-RP2 drive, up to {args.seconds}s.")
    print("Hold ` on the left half or 6 on the right and plug the cable in,")
    print("or run enter-bootloader.py for the half that already has it.\n")

    deadline = time.time() + args.seconds
    while time.time() < deadline:
        drive = find_bootloader_drive()
        if drive:
            print(f"Bootloader drive at {drive}")
            time.sleep(1)  # let the mount settle before writing
            shutil.copy2(firmware, Path(drive) / firmware.name)
            print(f"Copied {firmware.name}")
            print("The half reboots on its own once the write completes.")
            return
        time.sleep(1)

    sys.exit("Timed out. The drive never appeared.")


if __name__ == "__main__":
    main()

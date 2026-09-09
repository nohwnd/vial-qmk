"""Wait for an RP2040 bootloader drive and copy the firmware onto it.

The board mounts as a mass-storage device labelled RPI-RP2 and reboots by
itself once the .uf2 has been written, so the copy is the whole flash.
"""

import shutil
import sys
import time
from pathlib import Path

import subprocess

FIRMWARE = Path(__file__).with_name("fiddly_vial_v3.uf2")
TIMEOUT_SECONDS = 900


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
    if not FIRMWARE.exists():
        sys.exit(f"Firmware not found: {FIRMWARE}")

    print(f"Waiting for the RPI-RP2 drive, up to {TIMEOUT_SECONDS}s.")
    print("Press the right thumb key now.\n")

    deadline = time.time() + TIMEOUT_SECONDS
    while time.time() < deadline:
        drive = find_bootloader_drive()
        if drive:
            print(f"Bootloader drive at {drive}")
            time.sleep(1)  # let the mount settle before writing
            target = Path(drive) / FIRMWARE.name
            shutil.copy2(FIRMWARE, target)
            print(f"Copied {FIRMWARE.name} ({FIRMWARE.stat().st_size} bytes)")
            print("The half reboots on its own once the write completes.")
            return
        time.sleep(1)

    print("Timed out. The drive never appeared.")


if __name__ == "__main__":
    main()

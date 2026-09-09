"""Print the physical position of each key from the KLE layout in vial.json.

Vial stores the layout in Keyboard Layout Editor format, where each row is a
list of key labels interleaved with dicts that shift the cursor. Walking it
gives the x/y of every matrix position, which is how a (row, col) pair maps
to a key someone can actually point at.
"""

import json
import subprocess
from pathlib import Path

WSL_PATH = "/home/nohwnd/p/fiddly/keyboards/fiddly/keymaps/vial/vial.json"
HIGHLIGHT = (9, 3)


def load_layout():
    result = subprocess.run(
        ["wsl", "-d", "Ubuntu-24.04", "--", "cat", WSL_PATH],
        capture_output=True, text=True,
    )
    return json.loads(result.stdout)


def walk(kle_rows):
    """Yield (matrix_row, matrix_col, x, y, width) for each key."""
    y = 0.0
    for row in kle_rows:
        x = 0.0
        width = 1.0
        for item in row:
            if isinstance(item, dict):
                x += float(item.get("x", 0))
                y += float(item.get("y", 0))
                width = float(item.get("w", width))
                continue
            label = item.split("\n")[0]
            if "," in label:
                try:
                    r, c = (int(part) for part in label.split(",")[:2])
                    yield r, c, x, y, width
                except ValueError:
                    pass
            x += width
            width = 1.0
        y += 1.0


def main():
    layout = load_layout()
    keys = list(walk(layout["layouts"]["keymap"]))

    target = [k for k in keys if (k[0], k[1]) == HIGHLIGHT]
    if not target:
        print(f"Matrix position {HIGHLIGHT} is not in the layout.")
        return

    _, _, tx, ty, _ = target[0]
    print(f"Key {HIGHLIGHT[0]},{HIGHLIGHT[1]} sits at x={tx}, y={ty}\n")

    same_row = sorted([k for k in keys if abs(k[3] - ty) < 0.5], key=lambda k: k[2])
    print("Everything on that physical row, left to right:")
    for r, c, x, _, _ in same_row:
        mark = "  <-- QK_BOOT is here" if (r, c) == HIGHLIGHT else ""
        print(f"  x={x:5.2f}  matrix {r},{c}{mark}")

    xs = [k[2] for k in keys]
    print(f"\nBoard spans x={min(xs):.2f} to {max(xs):.2f}; "
          f"this key is at {tx:.2f}.")


if __name__ == "__main__":
    main()

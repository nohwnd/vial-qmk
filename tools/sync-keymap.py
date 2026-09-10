"""Keep the keymap in the board and the keymap in the repo in sync, both ways.

Vial edits live in the board's EEPROM and nowhere else, and a flash does not
push keymap.c into EEPROM either, since EEPROM survives flashing. So the two
drift apart in both directions. capture-keymap.py covers board to repo. This
covers the rest, including single keys, so a layout can be tried live and only
then written down.

    python sync-keymap.py --show                  # what the board has now
    python sync-keymap.py --set 0,9,1=DICTATE     # one key, live
    python sync-keymap.py --push                  # keymap.c -> board
    python sync-keymap.py --diff                  # what differs, no writes
"""

import argparse
import re
import subprocess
import sys
import time

from pywinusb import hid

VENDOR_ID = 0xFEED
RAW_USAGE_PAGE = 0xFF60
RAW_USAGE_ID = 0x61
CMD_GET_KEYCODE = 0x04
CMD_SET_KEYCODE = 0x05

LAYERS, ROWS, COLS = 4, 10, 7
KEYMAP_WSL = "/home/nohwnd/p/fiddly/keyboards/fiddly/keymaps/vial/keymap.c"

# Custom keycodes, in the order the enum in keymap.c declares them. Vial refers
# to them positionally as USER00..USER04, so the order is what matters.
CUSTOM_BASE = 0x7E00
CUSTOM = ["ALT_TAB", "ALT_SHIFT_TAB", "CTRL_TAB", "CTRL_SHIFT_TAB", "DICTATE", "ENT_DICT"]

BASIC = {
    0x28: "KC_ENT", 0x29: "KC_ESC", 0x2A: "KC_BSPC", 0x2B: "KC_TAB", 0x2C: "KC_SPACE",
    0x2D: "KC_MINS", 0x2E: "KC_EQL", 0x2F: "KC_LBRC", 0x30: "KC_RBRC", 0x31: "KC_BSLS",
    0x33: "KC_SCLN", 0x34: "KC_QUOT", 0x35: "KC_GRV", 0x36: "KC_COMM", 0x37: "KC_DOT",
    0x38: "KC_SLSH", 0x39: "KC_CAPS", 0x49: "KC_INS", 0x4A: "KC_HOME", 0x4B: "KC_PGUP",
    0x4C: "KC_DEL", 0x4D: "KC_END", 0x4E: "KC_PGDN", 0x4F: "KC_RIGHT", 0x50: "KC_LEFT",
    0x51: "KC_DOWN", 0x52: "KC_UP",
    0xE0: "KC_LCTL", 0xE1: "KC_LSFT", 0xE2: "KC_LALT", 0xE3: "KC_LGUI",
    0xE4: "KC_RCTL", 0xE5: "KC_RSFT", 0xE6: "KC_RALT", 0xE7: "KC_RGUI",
}
for _i in range(26):
    BASIC[0x04 + _i] = f"KC_{chr(ord('A') + _i)}"
for _i, _d in enumerate("1234567890"):
    BASIC[0x1E + _i] = f"KC_{_d}"
for _i in range(12):
    BASIC[0x3A + _i] = f"KC_F{_i + 1}"

ALIASES = {"KC_SPC": 0x2C, "KC_GRAVE": 0x35, "KC_ENTER": 0x28, "KC_BSPACE": 0x2A}
MOD_ORDER = [(0x01, "LCTL"), (0x02, "LSFT"), (0x04, "LALT"), (0x08, "LGUI")]
NAME_TO_CODE = {name: code for code, name in BASIC.items()}
NAME_TO_CODE.update(ALIASES)


def to_source(code):
    """Render one keycode as the C expression that produces it."""
    if code == 0x0000:
        return "XXXXXXX"
    if code == 0x0001:
        return "_______"
    if code == 0x7C00:
        return "QK_BOOT"
    if CUSTOM_BASE <= code < CUSTOM_BASE + len(CUSTOM):
        return CUSTOM[code - CUSTOM_BASE]
    if code in BASIC:
        return BASIC[code]
    if 0x4000 <= code < 0x5000:
        return f"LT({(code >> 8) & 0x0F}, {to_source(code & 0xFF)})"
    if 0x0100 <= code < 0x2000:
        mods = (code >> 8) & 0x0F
        wrapped = to_source(code & 0xFF)
        for bit, tag in MOD_ORDER:
            if mods == bit:
                return f"{tag}({wrapped})"
        for bit, tag in reversed(MOD_ORDER):
            if mods & bit:
                wrapped = f"{tag}({wrapped})"
        return wrapped
    return f"0x{code:04X}"


def from_source(text):
    """Turn a C expression from keymap.c back into a keycode."""
    text = text.strip()
    if text in ("XXXXXXX", "KC_NO"):
        return 0x0000
    if text in ("_______", "KC_TRNS"):
        return 0x0001
    if text == "QK_BOOT":
        return 0x7C00
    if text in CUSTOM:
        return CUSTOM_BASE + CUSTOM.index(text)
    if text in NAME_TO_CODE:
        return NAME_TO_CODE[text]
    if text.startswith("0x"):
        return int(text, 16)

    match = re.fullmatch(r"LT\(\s*(\d+)\s*,\s*(.+?)\s*\)", text)
    if match:
        return 0x4000 | (int(match.group(1)) << 8) | (from_source(match.group(2)) & 0xFF)

    match = re.fullmatch(r"(LCTL|LSFT|LALT|LGUI)\(\s*(.+?)\s*\)", text)
    if match:
        bit = dict((tag, b) for b, tag in MOD_ORDER)[match.group(1)]
        inner = from_source(match.group(2))
        # Mods live in bits 8-11, so nesting is just another bit set there.
        return inner | (bit << 8) if 0x0100 <= inner < 0x2000 else (bit << 8) | (inner & 0xFF)

    raise SystemExit(f"Cannot translate {text!r} into a keycode.")


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
        if not self.device.send_output_report(bytes(buf)):
            raise SystemExit("Write to the keyboard failed.")

    def get(self, layer, row, col):
        self._send([CMD_GET_KEYCODE, layer, row, col])
        for _ in range(30):
            time.sleep(0.01)
            if self.replies:
                reply = list(self.replies[0])
                return (reply[5] << 8) | reply[6]
        raise SystemExit(f"No reply reading layer {layer} row {row} col {col}.")

    def set(self, layer, row, col, code):
        self._send([CMD_SET_KEYCODE, layer, row, col, (code >> 8) & 0xFF, code & 0xFF])
        time.sleep(0.02)

    def grid(self):
        return [[[self.get(l, r, c) for c in range(COLS)]
                 for r in range(ROWS)] for l in range(LAYERS)]


def keymap_c_grid():
    """Read keymap.c and return the same shape the board reports."""
    source = subprocess.run(["wsl", "-d", "Ubuntu-24.04", "--", "cat", KEYMAP_WSL],
                            capture_output=True, text=True).stdout
    if not source:
        raise SystemExit(f"Could not read {KEYMAP_WSL}.")

    grid = []
    for layer in range(LAYERS):
        block = re.search(rf"\[{layer}\]\s*=\s*LAYOUT_split_3x6_3\((.*?)\n    \)",
                          source, re.S)
        if not block:
            raise SystemExit(f"Layer {layer} not found in keymap.c.")
        body = re.sub(r"//[^\n]*", "", block.group(1))
        cells = split_cells(body)
        if len(cells) != ROWS * COLS:
            raise SystemExit(
                f"Layer {layer} has {len(cells)} entries, expected {ROWS * COLS}.")
        grid.append([[from_source(cells[r * COLS + c]) for c in range(COLS)]
                     for r in range(ROWS)])
    return grid


def split_cells(body):
    """Split on commas that are not inside brackets, so LT(1, KC_SPACE) survives."""
    cells, depth, current = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            cells.append(current)
            current = ""
        else:
            current += ch
    if current.strip():
        cells.append(current)
    return [c.strip() for c in cells if c.strip()]


def differences(board, repo):
    out = []
    for l in range(LAYERS):
        for r in range(ROWS):
            for c in range(COLS):
                if board[l][r][c] != repo[l][r][c]:
                    out.append((l, r, c, board[l][r][c], repo[l][r][c]))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--show", action="store_true", help="print what the board has")
    group.add_argument("--diff", action="store_true", help="compare board and keymap.c")
    group.add_argument("--push", action="store_true", help="write keymap.c into the board")
    group.add_argument("--set", metavar="L,R,C=KEYCODE", action="append",
                       help="set one key, may be repeated")
    args = parser.parse_args()

    with Link() as link:
        if args.set:
            for item in args.set:
                where, _, name = item.partition("=")
                layer, row, col = (int(x) for x in where.split(","))
                code = from_source(name)
                before = link.get(layer, row, col)
                link.set(layer, row, col, code)
                after = link.get(layer, row, col)
                print(f"layer {layer} row {row} col {col}: "
                      f"{to_source(before)} -> {to_source(after)}")
                if after != code:
                    sys.exit("The board did not take the new keycode.")
            return

        board = link.grid()

        if args.show:
            for l in range(LAYERS):
                print(f"\n== layer {l} ==")
                for r in range(ROWS):
                    half = "L" if r < 5 else "R"
                    cells = " ".join(to_source(board[l][r][c]).ljust(15)
                                     for c in range(COLS))
                    print(f" {half} r{r}  {cells}".rstrip())
            return

        repo = keymap_c_grid()
        diff = differences(board, repo)

        if args.diff:
            if not diff:
                print("The board and keymap.c agree.")
                return
            print(f"{len(diff)} differences, board vs keymap.c:")
            for l, r, c, on_board, in_repo in diff:
                print(f"  layer {l} row {r} col {c}: "
                      f"board {to_source(on_board)}, repo {to_source(in_repo)}")
            return

        if not diff:
            print("The board already matches keymap.c, nothing written.")
            return
        for l, r, c, on_board, in_repo in diff:
            link.set(l, r, c, in_repo)
            print(f"layer {l} row {r} col {c}: "
                  f"{to_source(on_board)} -> {to_source(in_repo)}")
        print(f"\n{len(diff)} keys written to the board.")


if __name__ == "__main__":
    main()

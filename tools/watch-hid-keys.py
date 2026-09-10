"""Log what Windows receives from the keyboard, to see whether holding grave
really sends a held Ctrl+Space.

Uses a WH_KEYBOARD_LL hook, so it sees the events as any application does,
after the firmware and the HID stack are done with them. Events are passed
through untouched, typing is not affected.

    python watch-hid-keys.py            # watch for 20 seconds
    python watch-hid-keys.py --seconds 40
"""

import argparse
import ctypes
import ctypes.wintypes as w
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

WH_KEYBOARD_LL = 13
WM_KEYDOWN, WM_KEYUP = 0x0100, 0x0101
WM_SYSKEYDOWN, WM_SYSKEYUP = 0x0104, 0x0105
LLKHF_INJECTED = 0x10

# Only the keys this question is about, so the log stays readable.
WATCHED = {
    0x11: "Ctrl",
    0xA2: "LCtrl",
    0xA3: "RCtrl",
    0x20: "Space",
    0xC0: "Grave",
}


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", w.DWORD),
        ("scanCode", w.DWORD),
        ("flags", w.DWORD),
        ("time", w.DWORD),
        ("dwExtraInfo", ctypes.POINTER(w.ULONG)),
    ]


HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_int, w.WPARAM, ctypes.POINTER(KBDLLHOOKSTRUCT)
)

events = []
start = None
down = set()


def on_key(nCode, wParam, lParam):
    if nCode == 0:
        info = lParam.contents
        name = WATCHED.get(info.vkCode)
        if name:
            pressed = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
            repeat = pressed and info.vkCode in down
            if pressed:
                down.add(info.vkCode)
            else:
                down.discard(info.vkCode)
            events.append(
                {
                    "t": (time.perf_counter() - start) * 1000.0,
                    "key": name,
                    "pressed": pressed,
                    "repeat": repeat,
                    "injected": bool(info.flags & LLKHF_INJECTED),
                    "held": sorted(WATCHED[v] for v in down),
                }
            )
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def main():
    global start
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=20)
    args = ap.parse_args()

    callback = HOOKPROC(on_key)
    hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, callback, None, 0)
    if not hook:
        raise ctypes.WinError(ctypes.get_last_error())

    start = time.perf_counter()
    print(f"Watching Ctrl, Space and Grave for {args.seconds} s.")
    print("Hold the grave key for about 2 seconds, then let go.\n")

    msg = w.MSG()
    deadline = start + args.seconds
    while time.perf_counter() < deadline:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.005)

    user32.UnhookWindowsHookEx(hook)

    if not events:
        print("Nothing was recorded. No Ctrl, Space or Grave was pressed.")
        return

    print(f"{'time ms':>9}  {'key':<6} {'edge':<8} {'flags':<12} held")
    for e in events:
        edge = "down" if e["pressed"] else "up"
        flags = []
        if e["repeat"]:
            flags.append("repeat")
        if e["injected"]:
            flags.append("injected")
        print(
            f"{e['t']:9.1f}  {e['key']:<6} {edge:<8} {','.join(flags):<12} "
            f"{'+'.join(e['held']) or '-'}"
        )

    print()
    summarise()


def summarise():
    """State the one thing this was run to answer."""
    ctrl_names = {"Ctrl", "LCtrl", "RCtrl"}
    combo_start = None
    longest = 0.0
    repeats = 0

    held = set()
    for e in events:
        if e["repeat"]:
            repeats += 1
        if e["pressed"]:
            held.add(e["key"])
        else:
            held.discard(e["key"])
        both = held & ctrl_names and "Space" in held
        if both and combo_start is None:
            combo_start = e["t"]
        elif not both and combo_start is not None:
            longest = max(longest, e["t"] - combo_start)
            combo_start = None
    if combo_start is not None:
        longest = max(longest, events[-1]["t"] - combo_start)

    if longest == 0.0:
        print("Ctrl and Space were never held down at the same time.")
    else:
        print(f"Ctrl+Space was held together for {longest:.0f} ms.")
    if repeats:
        print(f"{repeats} auto-repeat events, so the host sees the key repeating.")


if __name__ == "__main__":
    main()

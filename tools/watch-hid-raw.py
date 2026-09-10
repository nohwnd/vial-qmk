"""Log every key Windows receives, with the detail needed to tell a real
keypress from one some software injected.

The plain view in watch-hid-keys.py answers whether a macro produced the right
keys. This one answers where they came from: scan code 0 and the injected flag
mean a program called SendInput, a real scan code means the event came off the
wire from the keyboard.

    python watch-hid-raw.py --seconds 15
"""

import argparse
import ctypes
import ctypes.wintypes as w
import time

user32 = ctypes.WinDLL("user32", use_last_error=True)

WH_KEYBOARD_LL = 13
WM_KEYDOWN, WM_SYSKEYDOWN = 0x0100, 0x0104
LLKHF_EXTENDED = 0x01
LLKHF_LOWER_IL_INJECTED = 0x02
LLKHF_INJECTED = 0x10

VK_NAMES = {
    0x08: "BSpc", 0x09: "Tab", 0x0D: "Enter", 0x10: "Shift", 0x11: "Ctrl",
    0x12: "Alt", 0x14: "Caps", 0x1B: "Esc", 0x20: "Space", 0x25: "Left",
    0x26: "Up", 0x27: "Right", 0x28: "Down", 0x2E: "Del",
    0x5B: "LWin", 0x5C: "RWin",
    0xA0: "LShift", 0xA1: "RShift", 0xA2: "LCtrl", 0xA3: "RCtrl",
    0xA4: "LAlt", 0xA5: "RAlt", 0xBA: ";", 0xBB: "=", 0xBC: ",", 0xBD: "-",
    0xBE: ".", 0xBF: "/", 0xC0: "Grave", 0xDB: "[", 0xDC: "\\", 0xDD: "]",
    0xDE: "'",
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


def name_of(vk):
    if vk in VK_NAMES:
        return VK_NAMES[vk]
    if 0x30 <= vk <= 0x5A:
        return chr(vk)
    return f"vk{vk:02X}"


def on_key(nCode, wParam, lParam):
    if nCode == 0:
        info = lParam.contents
        extra = ctypes.cast(info.dwExtraInfo, ctypes.c_void_p).value or 0
        events.append(
            {
                "t": (time.perf_counter() - start) * 1000.0,
                "key": name_of(info.vkCode),
                "vk": info.vkCode,
                "scan": info.scanCode,
                "down": wParam in (WM_KEYDOWN, WM_SYSKEYDOWN),
                "injected": bool(info.flags & LLKHF_INJECTED),
                "low_il": bool(info.flags & LLKHF_LOWER_IL_INJECTED),
                "extended": bool(info.flags & LLKHF_EXTENDED),
                "extra": extra,
            }
        )
    return user32.CallNextHookEx(None, nCode, wParam, lParam)


def main():
    global start
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=15)
    args = ap.parse_args()

    callback = HOOKPROC(on_key)
    hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, callback, None, 0)
    if not hook:
        raise ctypes.WinError(ctypes.get_last_error())

    start = time.perf_counter()
    print(f"Logging every key for {args.seconds} s.\n")

    msg = w.MSG()
    deadline = start + args.seconds
    while time.perf_counter() < deadline:
        while user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))
        time.sleep(0.005)

    user32.UnhookWindowsHookEx(hook)

    if not events:
        print("Nothing was recorded.")
        return

    print(f"{'time ms':>9}  {'key':<6} {'edge':<5} {'scan':>5}  "
          f"{'source':<22} extraInfo")
    for e in events:
        if e["injected"]:
            source = "injected (SendInput)"
            if e["low_il"]:
                source = "injected, lower IL"
        else:
            source = "real device"
        print(f"{e['t']:9.1f}  {e['key']:<6} {'down' if e['down'] else 'up':<5} "
              f"{e['scan']:5d}  {source:<22} 0x{e['extra']:X}")

    print()
    scans = {}
    for e in events:
        scans.setdefault((e["key"], e["injected"]), set()).add(e["scan"])
    print("Scan codes seen per key:")
    for (key, injected), codes in sorted(scans.items()):
        origin = "injected" if injected else "real"
        print(f"  {key:<6} {origin:<9} scan {sorted(codes)}")


if __name__ == "__main__":
    main()

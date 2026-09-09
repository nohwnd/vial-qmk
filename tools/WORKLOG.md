# Worklog

Written before each step, so a stalled or long-running action is visible
rather than looking like silence.

Format: timestamp, what is about to happen, then the result once it lands.

---

## 2026-09-09 19:06 — set up this log

**About to do:** create this file and start recording every step before running it.

**Result:** done.

**State right now:**

- Right half: new firmware, USB pid `0xf1dd`, connected.
- Left half: old January 2025 firmware, works as slave over the split link.
- Keymap: in git, captured from the board, round-trip verified.
- Tuning in EEPROM: `tapping_term 400`, `quick_tap_term 0`, everything else 0.
- Saved to `tools/settings.json`, restore with `qmk-settings.py --restore`.
- 8 commits in `~/p/fiddly`.

**Open question I never got an answer to:** whether `hold_on_other_key_press`
should go back to 1. It is 0 now. Space + P + P was slow with it at 0 and a
400 ms tapping term, which is what setting it to 1 fixes.

**Nothing is running in the background.**

---

## 2026-09-09 19:07 — bake the tuning into the firmware

**Goal:** stop needing a script or Vial after a flash. The values we settled on
should be what the firmware comes up with by itself.

**About to do:** find out when `qmk_settings_reset()` runs and whether a hook
fires after it, since anything set before it would just be overwritten.

**Result:** found it. `eeconfig_init_quantum()` erases EEPROM, calls
`eeconfig_init_via()` (which resets the keymap and the QMK settings), and only
then calls `eeconfig_init_kb()` -> `eeconfig_init_user()`. So `eeconfig_init_user`
is a weak hook that runs *after* the reset, which is exactly where the values
have to be written. `qmk_settings_set()` is public and writes through to EEPROM.

---

## 2026-09-09 19:09 — write the defaults into keymap.c

**About to do:** add `eeconfig_init_user()` to keymap.c setting tapping_term 400
and quick_tap_term 0, then build. Only those two differ from what the reset
produces, so the rest is left alone.

**Why this survives:** the hook only runs when the EEPROM is initialised, i.e.
after a flash. Later tuning through Vial or the script is not overwritten on
every boot.

**Result:** done and committed as `f1429ed`. `arm-none-eabi-nm` shows
`eeconfig_init_user` as `T`, not `W`, so the override took. Firmware exported as
`fiddly_vial_v3.uf2`.

**Not yet verified on hardware:** whether the values really land after a flash.
That only shows once v3 is flashed and the EEPROM reset actually runs.

---

## Next step, waiting on a decision

Flashing v3 resets the EEPROM again, so the current tuning is wiped and
re-applied from the firmware. If it works, nothing has to be typed afterwards.

Flashing means: hold the key that types `6` on the right half while plugging in
the USB cable, then run `flash-when-ready.py`.

**Nothing is running in the background.**

---

## 2026-09-09 19:16 — flashing v3

**About to do:** start `flash-when-ready.py`, which waits for the RPI-RP2 drive
and copies `fiddly_vial_v3.uf2` onto it. Then read the settings back to see
whether `eeconfig_init_user` really applied them.

**What this tests:** the flash wipes the EEPROM, so the tuning has to come back
from the firmware without anything being typed. If tapping_term reads 400 and
quick_tap_term reads 0 afterwards, the mechanism works.

**Keeping `QMK_SETTINGS = yes`** so Vial's settings tab and live tuning stay.

**Result:** flashed and verified on hardware.

Bootmagic invalidates the EEPROM before jumping to the bootloader, so the reset
really happened. Without the hook, `qmk_settings_reset` would have left
tapping_term 200 and quick_tap_term 200. The board reads 400 and 0, so
`eeconfig_init_user` ran and applied them.

Did **not** run the `id_eeprom_reset` test: it calls `eeconfig_init_via()` only,
skipping `eeconfig_init_user()`, so it would have reset the tuning to 200/200.

**Nothing is running in the background.**

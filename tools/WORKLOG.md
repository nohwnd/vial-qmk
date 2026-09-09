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

---

## 2026-09-09 19:20 — prove the value really comes from the firmware

**Why:** so far the firmware set the same numbers the EEPROM already had, so a
correct reading proved nothing on its own.

**About to do:** put `tapping_term = 333` in `eeconfig_init_user`, build, flash,
and read it back. 333 is a value nothing else in the tree produces, so seeing it
can only mean the firmware wrote it. Then set it back to 400 and flash again.

**Result:** the board reads `tapping_term 333`. Nothing else in the tree
produces that number, so the firmware demonstrably wrote it during
`eeconfig_init_user`. Proven, not inferred.

Reverting to 400 and flashing again.

---

## 2026-09-09 19:26 — reverted and installed Vial

**Done:** tapping_term back to 400, rebuilt, flashed, board reads 400.
The 333 -> 400 round trip proves the value comes from the firmware.

Vial 0.7.5 portable extracted to `vial\Vial\Vial.exe` and running. It is a
standalone app; it needs no QMK toolchain.

**Nothing is running in the background.**

---

## 2026-09-09 19:27 — layer waits before firing

**Symptom:** space + P + P does not delete straight away, it waits.

**Cause:** tapping_term is 400 and hold_on_other_key_press is 0, so QMK holds the
decision until the term expires instead of committing to the hold as soon as a
second key arrives.

**About to do:** set hold_on_other_key_press to 1 live, so it can be felt before
deciding whether to bake it into the firmware.

**Result:** confirmed better, "mnohem min liny". Baking it into the firmware.

---

## 2026-09-09 19:31 — queued requests

Seven messages arrived while I was mid-step. Working through them:

1. Matrix tester works now — that follows from the vial.json matrix fix
   (11x12 -> 10x7), so Vial reads the right addresses.
2. hold_on_other_key_press 1 confirmed better -> bake into firmware.
3. Question: is there still a delay when not pressing space.
4. Question: what tapping term 200 actually means.
5. Tapping term appears in two places in Vial.
6. Compare the older .vil files and the commit history to infer what was
   originally tuned.
7. Write a README in English.

**About to do:** add hold_on_other_key_press to eeconfig_init_user, then diff
the .vil settings blocks against each other.

**Result:** pending.

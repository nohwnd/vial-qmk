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

---

## 2026-09-09 19:44 — v5: eager debounce

**Changed:** `DEBOUNCE_TYPE = sym_eager_pk` in rules.mk. Kept DEBOUNCE at 10;
lowering it to 5 is what made 's' repeat, per the comment in config.h.

sym_defer_pk waits the window out after the last transition, so every press
carries 10 ms. sym_eager_pk reports the press immediately and then ignores the
pin for the window, so the filtering stays and the latency goes.

Flashed. All three tuning values came back from the firmware on their own,
including hold_on_other_key_press.

**Nothing is running in the background.**

---

## 2026-09-09 19:46 — bound the PIO clear loop

**About to do:** patch `serial_transport_driver_clear` in vial-qmk to cap the
number of drain attempts, generate a patch file into the repo so it survives
re-cloning vial-qmk, build, flash.

**Result:** patched, patch saved to `patches/0001-bound-pio-clear-loop.patch`,
built as `fiddly_vial_v6.uf2`. Not flashed yet.

**Untested:** whether this actually stops the freeze with a phone near the
cable. The loop can no longer spin forever, which is provable from the code,
but that the freeze had this cause is still inference.

**Nothing is running in the background.**

---

## 2026-09-10 09:24 — flashing v6 to both halves, left first

**Correction to yesterday:** the slave calls `serial_transport_driver_clear` too,
from `SlaveThread` on every failed transaction, which is exactly what happens
during interference. The left half is more exposed to the freeze than the right,
and it still runs the January 2025 firmware. So both halves need v6, not just
the master.

**Left half needs its physical BOOTSEL button.** Bootmagic and a QK_BOOT key
cannot work there: with USB plugged in it reports as the right half and switches
to that pin set, which does not match its wiring. Measured yesterday, not
inferred — watch-matrix.py saw 0 left-half keys while it was the USB half.

**About to do:** point flash-when-ready.py at v6, wait for the left half in
bootloader, then repeat for the right.

**Result:** paused for a meeting. Nothing flashed, watcher stopped.

**Tilde question settled from the code.** `bootmagic_should_reset` reads row 0
unless `!is_keyboard_left()`, and with `MASTER_RIGHT` the half holding USB is
always the master, so `is_keyboard_left()` is always false for it. Row 5 is
therefore always the one checked and row 0 never is. `6` works, tilde cannot,
on either half. The remembered tilde behaviour is probably from the other
keyboard, the one with a single controller.

**State:** board runs v5 and works. v6 adds only the bounded PIO loop, so
nothing is urgent.

**To resume:** run `python flash-when-ready.py`, then hold `6` and plug in the
right half. The left half needs its physical BOOTSEL button.

**Nothing is running in the background.**

---

## 2026-09-10 09:53 — how to flash the left half

Checked three routes.

**Double-tap reset:** the board config `GENERIC_PROMICRO_RP2040` does define
`RP2040_BOOTLOADER_DOUBLE_TAP_RESET`, in both the old and the new firmware, so
the mechanism exists. The window is 200 ms, which is too short to hit by hand,
and it expects a reset button rather than a power cycle. `_TIMEOUT` can be
raised, but only by flashing, which is the problem being solved.

**RPC over the split link:** `transaction_register_rpc` lets the master send a
command the slave acts on, so the slave could jump to its own bootloader. This
needs the RPC present in *both* firmwares. The left half runs January 2025 code
that has no such handler, so it cannot help this time. It would work for every
flash after the left half has been flashed once.

**Physical BOOTSEL:** works now, needs the case open.

So: this one time the case has to come open, or the left half stays on the old
firmware. Adding the RPC now means it is the last time.

**Note:** the left half being on old firmware is not currently causing trouble.
The split wire format is unchanged and it works as a slave.

---

## 2026-09-10 09:56 — left half flashed with v6

Copy succeeded. The half did not re-enumerate as a keyboard afterwards, which is
expected rather than a failure: with USB plugged into the left half, MASTER_RIGHT
makes it act as the right one and switch to the GP4-GP8 pin set, which does not
match its wiring, so its matrix never scans.

Next: move the cable back to the right half, reconnect the TRRS, verify both
halves report through watch-matrix.py, then flash the right half with v6 too.

---

## 2026-09-10 10:35 — left half: the flash chip is failing

**Conclusion: hardware, not firmware.** Jakub called it; I spent too long on code.

Evidence:

| Runs from RAM | Works |
| --- | --- |
| ROM bootloader, RPI-RP2 mass storage | yes, every time |
| flash_nuke | yes, completed |

| Runs from flash | Works |
| --- | --- |
| any firmware: BASELINE, v6, MASTER_LEFT, LED test | no |

The board now stays in the bootloader after a valid .uf2 is written, meaning the
write itself does not take. That also happened on the very first left-half flash
today, which I wrongly called expected at the time.

What I ruled out along the way, all by diffing the January 2025 tree against the
current one: USB detection, split transport, transaction ids, boot2 selection,
assumed flash size, board config. Every one identical. That was the signal it was
not the QMK version, and I should have reached the hardware conclusion sooner.

**Practical outcome:** the left controller needs replacing. The right half is
fine and runs v6.

**Reverted:** the LED test (WS2812 on GP16, PIO1) and the EE_HANDS experiment.
config.h is back to MASTER_RIGHT.

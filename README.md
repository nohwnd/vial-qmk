# fiddly

Keyboard definition for my split RP2040 board, kept outside the vial-qmk
monorepo so that vial-qmk stays a disposable upstream clone.

## Layout

- `keyboards/fiddly/` - the keyboard definition and the Vial keymap.
- `qmk.json` - QMK External Userspace build target.
- `tools/` - talk to the running keyboard over raw HID, see below.

## What lives where, and what a flash destroys

Three things decide how the board behaves, and they are not stored together.

| | Where it lives | Survives a flash |
| --- | --- | --- |
| Keyboard definition, pins, USB ids | `keyboard.json`, firmware | yes |
| Keymap | EEPROM, seeded from `keymap.c` | no |
| Tap-hold tuning | EEPROM, seeded from `eeconfig_init_user` | no |

Flashing changes the EEPROM layout version, so the board wipes it and reseeds
from the firmware. Anything edited in Vial and not captured back into this repo
is gone at that point, silently and with no warning.

So: capture before flashing.

```bash
python tools/capture-keymap.py --write    # keymap  -> keymap.c
python tools/qmk-settings.py --save       # tuning  -> tools/settings.json
```

## Building

vial-qmk is a plain upstream clone, never a fork, so it can be deleted and
re-cloned to update. It lives in the WSL filesystem because building over
/mnt (9p) is roughly 20x slower.

```bash
git clone --depth 1 --single-branch --branch vial \
    https://github.com/vial-kb/vial-qmk.git ~/p/vial-qmk
cd ~/p/vial-qmk
git submodule update --init --recursive --depth 1 \
    lib/chibios lib/chibios-contrib lib/pico-sdk lib/printf

# External Userspace does not discover keyboard definitions, only keymaps,
# so the keyboard folder is linked into the tree.
ln -sfn ~/p/fiddly/keyboards/fiddly ~/p/vial-qmk/keyboards/fiddly

qmk config user.qmk_home=~/p/vial-qmk
qmk config user.overlay_dir=~/p/fiddly

cd ~/p/vial-qmk && make fiddly:vial
```

Output lands in `~/p/fiddly/fiddly_vial.uf2`, built for whichever half the
keymap config currently names. To get both, use `tools/build-hands.sh`, see
[Flashing](#flashing) below.

Reapply the patch after every re-clone, otherwise a noisy split wire can
deadlock the firmware:

```bash
cd ~/p/vial-qmk && git apply ~/p/fiddly/patches/*.patch
```

## Flashing quickly

Hold BOOTSEL, plug in the half, drag the .uf2 onto the `RPI-RP2` drive.
The RP2040 bootloader is in mask ROM, so a bad firmware cannot brick the board.
The full story, including which key replaces BOOTSEL on each half, is under
[Flashing](#flashing).

## Keeping the repo and the board in sync

The keymap Vial edits lives in the board's EEPROM, and flashing resets it,
so the board and the repo drift apart silently. `tools/` closes that loop
over the VIA raw-HID protocol, which addresses keys as (layer, row, column)
resolved firmware-side and so is unaffected by what vial.json declares.

```bash
python tools/capture-keymap.py --write    # keymap  -> keymap.c
python tools/qmk-settings.py --save       # tuning  -> tools/settings.json
```

After flashing, put the tuning back:

```bash
python tools/qmk-settings.py --restore
```

The tuning matters because `qmk_settings_reset` derives `quick_tap_term`
from `TAPPING_TERM` and never reads `QUICK_TAP_TERM`, so the 0 in config.h
has no effect and every reset lands on a value that breaks the thumb layer
key: a space followed by a held space inside that window reads as a repeated
tap, so the layer never engages and the space auto-repeats instead.

Capture before flashing, otherwise the EEPROM reset discards whatever was
tweaked in Vial since the last capture.

Other tools:

- `dump-keymap.py` - readable dump of all layers, both halves.
- `watch-matrix.py` - live matrix view; shows whether both halves report.
- `keymap-poke.py` - read or write one key; `--set-boot` puts QK_BOOT on a
  spare thumb key, which is how to reach the bootloader without opening the
  case when bootmagic cannot help.
- `locate-key.py` - map a (row, col) back to a physical position.
- `flash-when-ready.py` - wait for the RPI-RP2 drive and copy the firmware.

### Which half can reach the bootloader

Both of them, since the move to `EE_HANDS`.

| half | how |
| --- | --- |
| left | hold the key that types `` ` `` while plugging in |
| right | hold the key that types `6` while plugging in |

`EE_HANDS` keeps the handedness in EEPROM, so a half knows what it is before
its matrix is set up and scans the pins that match its own wiring. Bootmagic
then reads a real key on either side. `bootmagic.matrix` is `[0, 0]` for the
left half and `split.bootmagic.matrix` is `[5, 0]` for the right, because split
gives the right half rows 5-9.

This did not work under `MASTER_RIGHT`, which derived handedness from
`usb_bus_detected()`. Whichever half held the cable acted as the right one and
switched to the right pin set, so on the left half the matrix never scanned and
neither bootmagic nor a QK_BOOT key could work there. That half needed its
physical BOOTSEL button, which meant opening the case.

## Tap-hold tuning

Space is `LT(1, KC_SPACE)`: tapped it types a space, held it selects layer 1.
Getting that to feel right is what most of the tuning is about.

| Setting | Value | Effect |
| --- | --- | --- |
| `tapping_term` | 400 | Held shorter than this and released alone, it types a space. Held longer, nothing. |
| `quick_tap_term` | 0 | Must be 0, see below. |
| `hold_on_other_key_press` | 1 | Commit to the layer the moment a second key arrives, rather than waiting out the term. |

`quick_tap_term` cannot be set from `config.h`. `qmk_settings_reset` derives it
from `TAPPING_TERM` and never reads `QUICK_TAP_TERM`, so the `0` there has no
effect. At any non-zero value, typing a space and then holding space again
within that window reads as a repeated tap: the layer never engages and the
space auto-repeats instead. This is why the values are written from
`eeconfig_init_user` in `keymap.c`, which runs after the reset.

Tuning can still be changed live, through Vial's QMK Settings tab or:

```bash
python tools/qmk-settings.py --set 7=250
```

The firmware only supplies what a freshly initialised EEPROM starts from, so
live changes are not overwritten on the next boot.

## Tools

All of these talk to the board over the VIA raw-HID protocol and need
`pip install pywinusb`. They address keys as (layer, row, column), resolved
firmware-side, so they do not depend on what `vial.json` declares.

| Tool | Purpose |
| --- | --- |
| `capture-keymap.py` | Read the live keymap and write it back as `keymap.c`. |
| `dump-keymap.py` | Readable dump of every layer, both halves. |
| `qmk-settings.py` | Read, set, save and restore the tap-hold tuning. |
| `watch-matrix.py` | Live matrix view; shows whether both halves report. |
| `keymap-poke.py` | Read or write one key. `--set-boot` puts `QK_BOOT` on a spare thumb key. |
| `locate-key.py` | Map a (row, col) back to a physical position. |
| `flash-when-ready.py` | Wait for the RPI-RP2 drive and copy the firmware onto it. |

## Flashing

`EE_HANDS` means the two halves no longer share a firmware, so the build
produces one file per half:

```bash
tools/build-hands.sh                 # writes fiddly_LEFT.uf2 and fiddly_RIGHT.uf2
```

They are not interchangeable. Flashing the wrong one makes a half believe it is
the other one, and its matrix stops matching its wiring.

Only the half holding the USB cable is flashed, so each one is done in turn.
Hold `` ` `` on the left or `6` on the right while plugging in, then:

```bash
python tools/flash-when-ready.py
```

Changes to key handling only need the right half. The master runs
`process_record_user` for keys on both halves, and the left half only reports
its matrix over the split wire, so a keymap or macro change takes effect once
the master has it. Handedness, pin mapping and bootmagic are per half, and those
need both.

The RP2040 bootloader is in mask ROM, so a bad firmware cannot brick the board.

## Debounce

`DEBOUNCE` is 10 ms, and the default `sym_defer_pk` algorithm is deliberate.

A switch does not close cleanly: the contacts bounce for a few milliseconds and
the firmware would read that as several presses. The debounce window is how long
the pin is ignored after a transition, so it sets the shortest gap between two
presses of the same key that still registers as two.

At 10 ms that gap is far below what a finger can do. Deliberate double taps land
around 60 to 80 ms, so nothing reachable by hand is lost.

The value has moved around, and both directions were wrong:

- `DEBOUNCE 5` let the `s` key repeat on its own. That is what the original
  comment in config.h records.
- `DEBOUNCE_TYPE = sym_eager_pk` reports the press immediately and only then
  ignores the pin, which cuts the input delay. On these switches it let the
  bounce through, and `b` and `r` started doubling. It is now removed.

So the cost of 10 ms is 10 ms of input delay per press, and the benefit is that
no key repeats by itself. If a key ever doubles again, that is a contact problem
to fix with a soldering iron rather than a longer window.

## Patches against vial-qmk

vial-qmk is meant to be disposable, so the one change made to it lives here and
has to be reapplied after re-cloning:

```bash
cd ~/p/vial-qmk && git apply ~/p/fiddly/patches/*.patch
```

`0001-bound-pio-clear-loop.patch` caps the drain loop in
`serial_transport_driver_clear`. The master runs that loop before every split
transaction while holding the system lock, and it was unbounded: interference on
the half-duplex wire can refill the RX FIFO as fast as it is drained, which
takes the whole firmware down until power is removed rather than just losing a
transaction. This is the suspected cause of the freeze when a phone sits near
the cable, though that link is inferred and not yet confirmed on hardware.

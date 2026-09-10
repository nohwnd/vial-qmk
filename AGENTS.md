# Working on this repo

Notes for anyone, human or agent, picking this up. The README says how the
keyboard works. This says what has already gone wrong, so it does not go wrong
again. Everything here cost time to learn.

## Do not break bootmagic on either half

This is the one thing that must keep working. The right half's case is closed,
so holding `6` while plugging in is the only way into its bootloader. Lose that
and the only way back is opening the case.

`EE_HANDS` is what makes bootmagic work on both halves, because handedness is
known before the matrix is set up. Under `MASTER_RIGHT` the half holding the
cable always believed it was the right one and scanned a pin set that did not
match its wiring, so the left half could not read any key during early init.

The two firmware files are not interchangeable. Flashing the wrong one makes a
half believe it is the other one.

## Measure what the host receives, not what the firmware believes

Holding a key to dictate looked like a firmware bug for days. The firmware was
correct the whole time, and TouchCursor was swallowing the key on the host.

Every tool in `tools/` except `watch-hid-*.py` reports what the firmware
thinks. That cannot answer whether a macro produced the right result. When a
macro misbehaves, start with:

```bash
python tools/watch-hid-raw.py --seconds 15
```

An event marked injected came from software on the machine, not the keyboard.
The `extraInfo` field usually names the culprit: `0x54435552` is ASCII `TCUR`,
TouchCursor.

## The board and the repo drift in both directions

The keymap lives in the board's EEPROM. Vial edits never reach the repo on
their own, and `keymap.c` does not reach the board either, since EEPROM
survives a flash and `keymap.c` is only the fallback for a freshly initialised
one. Use `capture-keymap.py --write` one way and `sync-keymap.py --push` the
other, and `sync-keymap.py --diff` to see where they stand.

`sync-keymap.py --set` changes one key live. Prefer trying a layout that way
before writing it down, since it needs no flash and no reboot. A custom keycode
only works live if the running firmware already has it.

## Do not hide build configuration in a script

`EE_HANDS` was once applied by a build script that edited `config.h`, built,
and copied the original back. The board ran that firmware and the repo could
not rebuild it. File times showed the config restored 27 ms after the last
`.uf2` was written.

If a build needs a setting, commit the setting. `tools/build-hands.sh` now only
sets `INIT_EE_HANDS_LEFT` or `INIT_EE_HANDS_RIGHT`, which genuinely has to
differ per build, and refuses to run if `config.h` is not on `EE_HANDS`.

It also applies `patches/` and stops if a patch does not apply. Warning was not
enough: the bounded PIO loop was reverted during a debugging session, never
reapplied, and every build for a day went out without it.

## Only the master runs key handling

`process_record_user` and `matrix_scan_user` run on the half holding the cable.
The other half only reports its matrix. So a keymap or macro change needs the
right half flashed and nothing else. Handedness, pin mapping and bootmagic are
per half and need both.

The split serial code runs on both. `serial_transport_driver_clear` is called
by the master before every transaction and by the slave from a `while (true)`
loop, so a fix there needs both halves.

## Builds are not reproducible, by 7 bytes

Two builds of the same tree differ at offsets 64637 to 64705. Comparing a build
against a flashed `.uf2` is still worth doing, but expect those seven bytes and
do not go hunting for a source change that is not there.

## Say what was measured and what was inferred

Two separate sessions wrote down that the USB bootloader jump works, from
reading the enum and the inner `vial_unlocked` check without the `#if` above
them. `VIAL_INSECURE` removes the command rather than unlocking it, so the jump
does nothing and nothing comes back to say so.

Read the guard, not just the line. When something has not been tried on
hardware, write that down next to the claim.

## Process

File an issue, make the change on a branch, open a pull request, merge it. The
repo is the record of why things are the way they are, and that only works if
the reasoning lands in the commit and the pull request rather than in a chat.

`archive-2025-qmk-fork` holds the January 2025 full QMK tree this repo used to
be. Its history was truncated at some point, which left it with no common
ancestor with upstream, so it can never be merged or updated again. Nothing
depends on it. vial-qmk is now cloned fresh and kept disposable instead, which
is why `patches/` and External Userspace exist.

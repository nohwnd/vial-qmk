# fiddly

Keyboard definition for my split RP2040 board, kept outside the vial-qmk monorepo.

## Layout

- `keyboards/fiddly/` - the keyboard definition and the Vial keymap.
- `qmk.json` - QMK External Userspace build target.

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

Output lands in `~/p/fiddly/fiddly_vial.uf2`.

## Flashing

Hold BOOTSEL, plug in the half, drag the .uf2 onto the `RPI-RP2` drive.
The RP2040 bootloader is in mask ROM, so a bad firmware cannot brick the board.

## Keeping the repo and the board in sync

The keymap Vial edits lives in the board's EEPROM, and flashing resets it,
so the board and the repo drift apart silently. `tools/` closes that loop
over the VIA raw-HID protocol, which addresses keys as (layer, row, column)
resolved firmware-side and so is unaffected by what vial.json declares.

```bash
python tools/capture-keymap.py            # show the live keymap as C
python tools/capture-keymap.py --write    # write it back into keymap.c
```

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

`MASTER_RIGHT` derives handedness from `usb_bus_detected()`, so whichever
half holds the USB cable acts as the right one and switches to the right
pin set. On the left half that pin set does not match the wiring, so its
matrix does not scan and neither bootmagic nor a QK_BOOT key can work
there - the left half needs its physical BOOTSEL button.

The right half is fine: `split.bootmagic.matrix` is now `[5, 0]`, so
holding the key that types `6` while plugging in enters the bootloader.

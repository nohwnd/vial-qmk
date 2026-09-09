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

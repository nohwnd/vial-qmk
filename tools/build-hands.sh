#!/usr/bin/env bash
# Build one firmware per half.
#
# EE_HANDS keeps the handedness in EEPROM, so each half knows what it is no
# matter where the USB cable sits. The value is written on first boot from
# INIT_EE_HANDS_LEFT or INIT_EE_HANDS_RIGHT, which is the only thing that
# differs between the two builds, so it is set here instead of being committed.
#
# The two files are not interchangeable. Flashing the wrong one makes a half
# believe it is the other one, and its matrix stops matching its wiring.
set -e

export PATH="$HOME/.local/bin:$PATH"
export QMK_USERSPACE="${QMK_USERSPACE:-$HOME/p/fiddly}"
export QMK_HOME="${QMK_HOME:-$HOME/p/vial-qmk}"

KEYMAP_CFG="$QMK_USERSPACE/keyboards/fiddly/keymaps/vial/config.h"
OUT="${1:-/mnt/q/p/fiddly-firmware}"

if ! grep -q "^#define EE_HANDS" "$QMK_USERSPACE/keyboards/fiddly/config.h"; then
    echo "config.h does not define EE_HANDS, refusing to build" >&2
    exit 1
fi

# vial-qmk is a disposable clone, so the patch has to be reapplied after each
# re-clone. Without it a noisy split wire can deadlock the firmware.
if grep -A3 "^inline void serial_transport_driver_clear" \
    "$QMK_HOME/platforms/chibios/drivers/vendor/RP/RP2040/serial_vendor.c" \
    | grep -q "while (!pio_sm_is_rx_fifo_empty"; then
    echo "WARNING: patches/0001-bound-pio-clear-loop.patch is not applied to $QMK_HOME" >&2
    echo "         run: cd $QMK_HOME && git apply $QMK_USERSPACE/patches/*.patch" >&2
fi

cp "$KEYMAP_CFG" /tmp/keymap_config.h.bak
trap 'cp /tmp/keymap_config.h.bak "$KEYMAP_CFG"' EXIT

cd "$QMK_HOME"
for side in LEFT RIGHT; do
    sed -i '/INIT_EE_HANDS/d' "$KEYMAP_CFG"
    echo "#define INIT_EE_HANDS_$side" >> "$KEYMAP_CFG"

    echo "== building $side =="
    make fiddly:vial 2>&1 | grep -Ei "error|Creating UF2" | tail -2
    cp "$QMK_USERSPACE/fiddly_vial.uf2" "$OUT/fiddly_${side}.uf2"
done

echo
ls -la "$OUT"/fiddly_LEFT.uf2 "$OUT"/fiddly_RIGHT.uf2

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

# vial-qmk is a disposable clone, so the patches have to be reapplied after
# every re-clone. Applying them here rather than warning means a rebuild cannot
# quietly drop one, which is how the board ended up running a firmware without
# the fix for the split wire deadlock.
shopt -s nullglob
for patch in "$QMK_USERSPACE"/patches/*.patch; do
    name=$(basename "$patch")
    if git -C "$QMK_HOME" apply --reverse --check "$patch" 2>/dev/null; then
        echo "patch already applied: $name"
    elif git -C "$QMK_HOME" apply "$patch" 2>/dev/null; then
        echo "patch applied: $name"
    else
        echo "cannot apply $name to $QMK_HOME, refusing to build" >&2
        exit 1
    fi
done
shopt -u nullglob

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

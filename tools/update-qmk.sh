#!/usr/bin/env bash
# Update the vial-qmk clone, or create it if it is not there yet.
#
# The clone is disposable on purpose: this repo holds only keyboards/fiddly,
# tools/ and patches/, and vial-qmk is a build dependency that gets thrown away
# rather than a fork that gets merged. Updating is therefore a delete and a
# re-clone, which cannot produce a merge conflict.
#
# The old arrangement was a full fork with its history truncated to save space.
# That left it with no common ancestor with upstream, so it could never be
# merged or updated again. This exists so nobody has to remember any of that.
#
#   tools/update-qmk.sh            # update in place, keeping the old clone
#   tools/update-qmk.sh --check    # report versions and change nothing
set -e

export PATH="$HOME/.local/bin:$PATH"
QMK_USERSPACE="${QMK_USERSPACE:-$HOME/p/fiddly}"
QMK_HOME="${QMK_HOME:-$HOME/p/vial-qmk}"
REMOTE="https://github.com/vial-kb/vial-qmk.git"
BRANCH="vial"

local_sha() {
    git -C "$QMK_HOME" rev-parse HEAD 2>/dev/null || echo "none"
}

remote_sha() {
    git ls-remote "$REMOTE" "refs/heads/$BRANCH" | cut -f1
}

if [ "${1:-}" = "--check" ]; then
    echo "clone:    $QMK_HOME"
    if [ -d "$QMK_HOME/.git" ]; then
        echo "local:    $(local_sha)  $(git -C "$QMK_HOME" log -1 --format=%ad --date=short 2>/dev/null)"
    else
        echo "local:    not cloned yet"
    fi
    echo "upstream: $(remote_sha)  ($REMOTE, branch $BRANCH)"
    if [ -d "$QMK_HOME/.git" ] && [ "$(local_sha)" = "$(remote_sha)" ]; then
        echo
        echo "Up to date, nothing to do."
    else
        echo
        echo "Run tools/update-qmk.sh to update."
    fi
    exit 0
fi

echo "== updating $QMK_HOME to $REMOTE branch $BRANCH =="
echo "was: $(local_sha)"

# Clone beside the old one and swap at the end, so a failure part way through
# leaves the working clone in place.
FRESH="${QMK_HOME}.new.$$"
rm -rf "$FRESH"
trap 'rm -rf "$FRESH"' EXIT

git clone --depth 1 --single-branch --branch "$BRANCH" "$REMOTE" "$FRESH"
git -C "$FRESH" submodule update --init --recursive --depth 1 \
    lib/chibios lib/chibios-contrib lib/pico-sdk lib/printf

# External Userspace finds keymaps but not keyboard definitions, so the
# keyboard folder is linked into the tree rather than copied.
ln -sfn "$QMK_USERSPACE/keyboards/fiddly" "$FRESH/keyboards/fiddly"

# Fail before swapping if a patch no longer applies, so a broken update never
# replaces a working clone. build-hands.sh applies them for real at build time.
for patch in "$QMK_USERSPACE"/patches/*.patch; do
    [ -e "$patch" ] || continue
    if ! git -C "$FRESH" apply --check "$patch" 2>/dev/null; then
        echo "$(basename "$patch") no longer applies to the new clone." >&2
        echo "The existing clone is untouched. Rebase the patch first." >&2
        exit 1
    fi
done

if [ -d "$QMK_HOME" ]; then
    rm -rf "${QMK_HOME}.old"
    mv "$QMK_HOME" "${QMK_HOME}.old"
fi
mv "$FRESH" "$QMK_HOME"
trap - EXIT

qmk config user.qmk_home="$QMK_HOME" >/dev/null
qmk config user.overlay_dir="$QMK_USERSPACE" >/dev/null

echo "now: $(local_sha)"
echo
echo "The previous clone is at ${QMK_HOME}.old, delete it once a build works:"
echo "  tools/build-hands.sh && rm -rf ${QMK_HOME}.old"

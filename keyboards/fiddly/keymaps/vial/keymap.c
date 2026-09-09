/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "print.h"
#include "qmk_settings.h"

#include QMK_KEYBOARD_H

/* Generated from keymaps/vial/new.vil so that a firmware flash, which resets
 * the EEPROM, still comes up with the real layout instead of a placeholder.
 *
 * The custom keycodes must keep this order: Vial refers to them positionally
 * as USER00..USER03, matching the customKeycodes array in vial.json.
 */
enum custom_keycodes {
  ALT_TAB = QK_KB_0, // Instead of SAFE_RANGE, you need to use QK_KB_0 to support custom names defined in vial.json
  ALT_SHIFT_TAB,
  CTRL_TAB,
  CTRL_SHIFT_TAB,
  GRV_DICT, // USER04: tap = `, hold = drzene Ctrl+Space pro diktovani
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    /* 0: BASE */
    [0] = LAYOUT_split_3x6_3(
        // leva pulka
        GRV_DICT       , KC_1           , KC_2           , KC_3           , KC_4           , KC_5           , XXXXXXX,
        KC_TAB         , KC_Q           , KC_W           , KC_E           , KC_R           , KC_T           , XXXXXXX,
        KC_LCTL        , KC_A           , KC_S           , KC_D           , KC_F           , KC_G           , XXXXXXX,
        KC_LSFT        , KC_Z           , KC_X           , KC_C           , KC_V           , KC_B           , XXXXXXX,
        XXXXXXX        , XXXXXXX        , KC_LALT        , KC_LGUI        , LT(1, KC_SPACE), XXXXXXX        , XXXXXXX,

        // prava pulka
        KC_6           , KC_7           , KC_8           , KC_9           , KC_0           , KC_MINS        , KC_EQL,
        KC_Y           , KC_U           , KC_I           , KC_O           , KC_P           , KC_LBRC        , KC_RBRC,
        KC_H           , KC_J           , KC_K           , KC_L           , KC_SCLN        , KC_QUOT        , KC_BSLS,
        KC_N           , KC_M           , KC_COMM        , KC_DOT         , KC_SLSH        , KC_RSFT        , KC_ESC,
        XXXXXXX        , LT(1, KC_SPACE), KC_LCTL        , KC_LALT        , XXXXXXX        , XXXXXXX        , XXXXXXX
    ),

    /* 1: NAV / FUNKCE */
    [1] = LAYOUT_split_3x6_3(
        // leva pulka
        _______         , KC_F1           , KC_F2           , KC_F3           , KC_F4           , KC_F5           , XXXXXXX,
        _______         , KC_ESC          , LCTL(LSFT(KC_P)), CTRL_SHIFT_TAB  , CTRL_TAB        , LCTL(KC_T)      , XXXXXXX,
        KC_LCTL         , LCTL(KC_A)      , LCTL(KC_S)      , LCTL(KC_C)      , LCTL(KC_V)      , ALT_TAB         , XXXXXXX,
        _______         , LCTL(KC_Z)      , LCTL(KC_X)      , _______         , LGUI(KC_V)      , ALT_SHIFT_TAB   , XXXXXXX,
        XXXXXXX         , XXXXXXX         , _______         , _______         , _______         , XXXXXXX         , XXXXXXX,

        // prava pulka
        KC_F6           , KC_F7           , KC_F8           , KC_F9           , KC_F10          , KC_F11          , KC_F12,
        _______         , KC_HOME         , KC_UP           , KC_END          , KC_BSPC         , _______         , _______,
        KC_ENT          , KC_LEFT         , KC_DOWN         , KC_RIGHT        , KC_ENT          , LCTL(KC_GRV)    , _______,
        KC_BSPC         , KC_DEL          , LCTL(KC_LEFT)   , LCTL(KC_RIGHT)  , _______         , _______         , _______,
        XXXXXXX         , _______         , _______         , _______         , XXXXXXX         , XXXXXXX         , XXXXXXX
    ),

    /* 2: VRSTVA 2 */
    [2] = LAYOUT_split_3x6_3(
        // leva pulka
        _______, _______, _______, _______, _______, _______, XXXXXXX,
        _______, _______, _______, _______, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,

        // prava pulka
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX
    ),

    /* 3: VRSTVA 3 */
    [3] = LAYOUT_split_3x6_3(
        // leva pulka
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,

        // prava pulka
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX,
        XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX, XXXXXXX
    )
};


/**
 * Cool Function where a single key does ALT+TAB, ALT+SHIFT+TAB, CTRL+TAB, CTRL+SHIFT+TAB
 * From: https://beta.docs.qmk.fm/features/feature_macros#super-alt-tab
 */
bool is_alt_tab_active = false;
bool is_alt_shift_tab_active = false;
bool is_ctrl_tab_active = false;
bool is_ctrl_shift_tab_active = false;
uint16_t hold_timer = 0;

// Push-to-talk dictation on the grave key.
static bool     grv_pressed   = false;
static bool     grv_dictating = false;
static uint16_t grv_timer     = 0;

#define HOLD_TIMER 750

// key processing
bool process_record_user(uint16_t keycode, keyrecord_t *record) {
  #ifdef CONSOLE_ENABLE
    uprintf("KL: kc: 0x%04X, kc: %2u, col: %2u, row: %2u, pressed: %u, time: %5u, int: %u, count: %u\n", keycode, keycode, record->event.key.col, record->event.key.row, record->event.pressed, record->event.time, record->tap.interrupted, record->tap.count);
  #endif

  switch (keycode) {
    case ALT_TAB:
      if (record->event.pressed) {
        if (is_alt_shift_tab_active) {
            unregister_code(KC_LEFT_SHIFT);
            is_alt_shift_tab_active = false;
        }

        if (!is_alt_tab_active) {
          is_alt_tab_active = true;
          register_code(KC_LALT);
        }

        hold_timer = timer_read();
        register_code(KC_TAB);
      } else {
        unregister_code(KC_TAB);
      }
      break;
    case ALT_SHIFT_TAB:
      if (record->event.pressed) {
        if (!is_alt_shift_tab_active) {
          is_alt_shift_tab_active = true;
          register_code(KC_LALT);
          register_code(KC_LEFT_SHIFT);
        }
        hold_timer = timer_read();
        register_code(KC_TAB);
      } else {
        unregister_code(KC_TAB);
      }
      break;
    case CTRL_TAB:
      if (record->event.pressed) {

        if (is_ctrl_shift_tab_active) {
            unregister_code(KC_LEFT_SHIFT);
            is_ctrl_shift_tab_active = false;
        }

        if (!is_ctrl_tab_active) {
          is_ctrl_tab_active = true;
          register_code(KC_LEFT_CTRL);
        }
        hold_timer = timer_read();
        register_code(KC_TAB);
      } else {
        unregister_code(KC_TAB);
      }
      break;
    case CTRL_SHIFT_TAB:
      if (record->event.pressed) {
        if (!is_ctrl_shift_tab_active) {
          is_ctrl_shift_tab_active = true;
          register_code(KC_LEFT_CTRL);
          register_code(KC_LEFT_SHIFT);
        }
        hold_timer = timer_read();
        register_code(KC_TAB);
      } else {
        unregister_code(KC_TAB);
      }
      break;

    /* Tap sends a grave. Holding past the tapping term presses Ctrl+Space and
     * keeps it down until release, which is what push-to-talk dictation needs:
     * the combo has to read as held, not as a single press. */
    case GRV_DICT:
      if (record->event.pressed) {
        grv_pressed   = true;
        grv_dictating = false;
        grv_timer     = timer_read();
      } else {
        grv_pressed = false;
        if (grv_dictating) {
          unregister_code(KC_SPACE);
          unregister_code(KC_LEFT_CTRL);
          grv_dictating = false;
        } else {
          tap_code(KC_GRAVE);
        }
      }
      return false;

    // Releasing the layer-tap thumb key ends any Alt-Tab / Ctrl-Tab run.
    case LT(1, KC_SPACE):
      if (record->event.pressed) {
        return true;
      } else {
        if (is_alt_tab_active) {
          unregister_code(KC_LALT);
          is_alt_tab_active = false;
        }
        if (is_alt_shift_tab_active) {
          unregister_code(KC_LALT);
          unregister_code(KC_LEFT_SHIFT);
          is_alt_shift_tab_active = false;
        }
        if (is_ctrl_tab_active) {
          unregister_code(KC_LEFT_CTRL);
          is_ctrl_tab_active = false;
        }
        if (is_ctrl_shift_tab_active) {
          unregister_code(KC_LEFT_CTRL);
          unregister_code(KC_LEFT_SHIFT);
          is_ctrl_shift_tab_active = false;
        }
    }
  }
  return true;
}


void matrix_scan_user(void) {
  if (grv_pressed && !grv_dictating && timer_elapsed(grv_timer) > TAPPING_TERM) {
    grv_dictating = true;
    register_code(KC_LEFT_CTRL);
    register_code(KC_SPACE);
  }
}


/* Vial keeps the tap-hold tuning in EEPROM, and a flash resets it, so these
 * values used to have to be dialled back in by hand every time.
 *
 * eeconfig_init_user runs after eeconfig_init_via has already reset the
 * settings, so writing them here makes a freshly flashed board come up usable.
 * It only runs when the EEPROM is initialised, so later tuning through Vial or
 * tools/qmk-settings.py is not clobbered on every boot.
 *
 * Only these two differ from what qmk_settings_reset produces:
 *
 * quick_tap_term must be 0. qmk_settings_reset derives it from TAPPING_TERM and
 * never reads QUICK_TAP_TERM, so config.h cannot set it. At any non-zero value,
 * typing a space and then holding space again within that window reads as a
 * repeated tap, so the thumb layer never engages and the space auto-repeats.
 *
 * tapping_term is 400 rather than 200 to leave room for a deliberate tap.
 */
void eeconfig_init_user(void) {
    uint16_t tapping_term   = 400;
    uint16_t quick_tap_term = 0;

    qmk_settings_set(7, &tapping_term, sizeof(tapping_term));
    qmk_settings_set(25, &quick_tap_term, sizeof(quick_tap_term));
}

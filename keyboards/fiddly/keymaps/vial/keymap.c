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
  DICTATE, // USER04: tap = space, double tap = enter, hold = held Ctrl+Space
  ENT_DICT, // USER05: tap = enter, hold = held Ctrl+Space, for the left hand
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    /* 0: BASE */
    [0] = LAYOUT_split_3x6_3(
        // leva pulka
        KC_GRV         , KC_1           , KC_2           , KC_3           , KC_4           , KC_5           , XXXXXXX,
        KC_TAB         , KC_Q           , KC_W           , KC_E           , KC_R           , KC_T           , XXXXXXX,
        KC_LCTL        , KC_A           , KC_S           , KC_D           , KC_F           , KC_G           , XXXXXXX,
        KC_LSFT        , KC_Z           , KC_X           , KC_C           , KC_V           , KC_B           , XXXXXXX,
        XXXXXXX        , XXXXXXX        , KC_LALT        , KC_LGUI        , LT(1, KC_SPACE), XXXXXXX        , XXXXXXX,

        // prava pulka
        KC_6           , KC_7           , KC_8           , KC_9           , KC_0           , KC_MINS        , KC_EQL,
        KC_Y           , KC_U           , KC_I           , KC_O           , KC_P           , KC_LBRC        , KC_RBRC,
        KC_H           , KC_J           , KC_K           , KC_L           , KC_SCLN        , KC_QUOT        , KC_BSLS,
        KC_N           , KC_M           , KC_COMM        , KC_DOT         , KC_SLSH        , KC_RSFT        , KC_ESC,
        XXXXXXX        , DICTATE        , KC_LCTL        , KC_LALT        , XXXXXXX        , XXXXXXX        , XXXXXXX
    ),

    /* 1: NAV / FUNKCE */
    [1] = LAYOUT_split_3x6_3(
        // leva pulka
        _______         , KC_F1           , KC_F2           , KC_F3           , KC_F4           , KC_F5           , XXXXXXX,
        ALT_TAB         , KC_ESC          , LCTL(LSFT(KC_P)), CTRL_SHIFT_TAB  , CTRL_TAB        , LCTL(KC_T)      , XXXXXXX,
        KC_LCTL         , LCTL(KC_A)      , LCTL(KC_S)      , LCTL(KC_C)      , LCTL(KC_V)      , ENT_DICT        , XXXXXXX,
        _______         , LCTL(KC_Z)      , LCTL(KC_X)      , _______         , LGUI(KC_V)      , _______         , XXXXXXX,
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

// Push-to-talk dictation on the right thumb key.
static bool     dict_pressed = false;  // key is down right now
static bool     dict_active  = false;  // Ctrl+Space is being held
static uint16_t dict_timer   = 0;      // when the key went down
static bool     tap_pending  = false;  // a tap is waiting to see if a second follows
static uint16_t tap_timer    = 0;      // when that tap was released

// The same thing on layer 1, so enter and dictation are reachable with the
// left hand alone while the right hand is on the mouse.
static bool     ent_pressed  = false;
static bool     ent_active   = false;
static uint16_t ent_timer    = 0;

/* Own terms rather than TAPPING_TERM, which is the compile time 200 while the
 * tuning in EEPROM runs the layer key at 400. This key is not a layer key and
 * should not follow it. */
#define DICT_HOLD_TERM 200  // held longer than this starts dictation
#define DICT_TAP_TERM  250  // a second tap within this sends enter

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

    /* The right thumb space key, which used to be a second LT(1, KC_SPACE).
     * The layer stays on the left thumb, which is the one actually used for it.
     *
     *   tap         space
     *   double tap  enter, so a dictated message can be sent from the same key
     *   hold        Ctrl+Space held down until release, for push-to-talk
     *               dictation, which needs the combo held rather than tapped
     *
     * The single tap has to wait out DICT_TAP_TERM before it can be sent,
     * otherwise a double tap would emit a space and then the enter. */
    case DICTATE:
      if (record->event.pressed) {
        dict_pressed = true;
        dict_active  = false;
        dict_timer   = timer_read();
      } else {
        dict_pressed = false;
        if (dict_active) {
          unregister_code(KC_SPACE);
          unregister_code(KC_LEFT_CTRL);
          dict_active = false;
        } else if (tap_pending && timer_elapsed(tap_timer) <= DICT_TAP_TERM) {
          tap_pending = false;
          tap_code(KC_ENTER);
        } else {
          tap_pending = true;
          tap_timer   = timer_read();
        }
      }
      return false;

    /* Layer 1 on the G key, so the left hand alone can send enter or start
     * dictation while the right hand is on the mouse. No double tap here, the
     * tap is already enter, so it can be sent without waiting. */
    case ENT_DICT:
      if (record->event.pressed) {
        ent_pressed = true;
        ent_active  = false;
        ent_timer   = timer_read();
      } else {
        ent_pressed = false;
        if (ent_active) {
          unregister_code(KC_SPACE);
          unregister_code(KC_LEFT_CTRL);
          ent_active = false;
        } else {
          tap_code(KC_ENTER);
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
  /* Start dictation once the key has been down long enough. A tap that was
   * still waiting for a partner is sent first, so nothing is swallowed. */
  if (dict_pressed && !dict_active && timer_elapsed(dict_timer) > DICT_HOLD_TERM) {
    if (tap_pending) {
      tap_pending = false;
      tap_code(KC_SPACE);
    }
    dict_active = true;
    register_code(KC_LEFT_CTRL);
    register_code(KC_SPACE);
  }

  /* No second tap arrived in time, so the first one was a plain space. */
  if (tap_pending && !dict_pressed && timer_elapsed(tap_timer) > DICT_TAP_TERM) {
    tap_pending = false;
    tap_code(KC_SPACE);
  }

  /* Same hold, on the layer 1 key, which sends enter rather than space. */
  if (ent_pressed && !ent_active && timer_elapsed(ent_timer) > DICT_HOLD_TERM) {
    ent_active = true;
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
 *
 * hold_on_other_key_press commits to the hold the moment a second key arrives
 * instead of waiting out the term, which a 400 ms term otherwise makes felt as
 * a lag before the layer responds.
 */
void eeconfig_init_user(void) {
    uint16_t tapping_term   = 400;
    uint16_t quick_tap_term = 0;
    uint8_t  hold_on_other  = 1;

    qmk_settings_set(7, &tapping_term, sizeof(tapping_term));
    qmk_settings_set(25, &quick_tap_term, sizeof(quick_tap_term));
    qmk_settings_set(23, &hold_on_other, sizeof(hold_on_other));
}

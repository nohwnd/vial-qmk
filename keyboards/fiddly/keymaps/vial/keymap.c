/* SPDX-License-Identifier: GPL-2.0-or-later */
#include "print.h"

#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT_split_3x6_3(
      KC_ESCAPE, KC_1, KC_2, KC_3, KC_4, KC_5, KC_NO,                       
      KC_TAB,    KC_Q, KC_W, KC_E, KC_R, KC_T,  KC_NO,                      
      KC_LEFT_CTRL, KC_A, KC_S, KC_D, KC_F, KC_G, KC_NO,                                           
      KC_LEFT_SHIFT, KC_Z, KC_X, KC_C, KC_V, KC_B,  KC_NO,                  
      KC_NO,KC_NO,  KC_LEFT_ALT, KC_LEFT_GUI, KC_SPACE, KC_NO,    KC_NO,

      KC_6, KC_7, KC_8, KC_9, KC_0, KC_MINUS, KC_MINUS,
      KC_Y, KC_U, KC_I, KC_O, KC_P, KC_LEFT_BRACKET, KC_LEFT_BRACKET,
      KC_H, KC_J, KC_K, KC_L, KC_SEMICOLON, KC_QUOTE, KC_QUOTE, 
      KC_N, KC_M, KC_COMMA, KC_DOT, KC_SLASH, KC_RIGHT_SHIFT, KC_SPACE,
      KC_SPACE, KC_SPACE, KC_SPACE, KC_SPACE, KC_SPACE, KC_SPACE, KC_SPACE
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

#define HOLD_TIMER 750

enum custom_keycodes {
  ALT_TAB = QK_KB_0, // Instead of SAFE_RANGE, you need to use QK_KB_0 to support custom names defined in vial.json
  ALT_SHIFT_TAB,
  CTRL_TAB,
  CTRL_SHIFT_TAB,
};

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

    case 0x412C: // LT(1, SPACE)
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

// The very important timer.
void matrix_scan_user(void) { 
  // if (is_alt_tab_active && timer_elapsed(hold_timer) > HOLD_TIMER) {
  //   unregister_code(KC_LALT);
  //   is_alt_tab_active = false;
  // }
  // if (is_alt_shift_tab_active && timer_elapsed(hold_timer) > HOLD_TIMER) {
  //   unregister_code(KC_LALT);
  //   unregister_code(KC_LEFT_SHIFT);
  //   is_alt_shift_tab_active = false;
  // }
  // if (is_ctrl_tab_active && timer_elapsed(hold_timer) > HOLD_TIMER) {
  //   unregister_code(KC_LEFT_CTRL);
  //   is_ctrl_tab_active = false;
  // }
  // if (is_ctrl_shift_tab_active && timer_elapsed(hold_timer) > HOLD_TIMER) {
  //   unregister_code(KC_LEFT_CTRL);
  //   unregister_code(KC_LEFT_SHIFT);
  //   is_ctrl_shift_tab_active = false;
  // }
}

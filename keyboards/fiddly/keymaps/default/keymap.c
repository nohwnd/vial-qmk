// Copyright 2023 QMK
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
     /*
      * ┌───┬───┬───┬───┬───┬───┐       ┌───┬───┬───┬───┬───┬───┐
      * │Tab│ Q │ W │ E │ R │ T │       │ Y │ U │ I │ O │ P │Bsp│
      * ├───┼───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┼───┤
      * │Ctl│ A │ S │ D │ F │ G │       │ H │ J │ K │ L │ ; │ ' │
      * ├───┼───┼───┼───┼───┼───┤       ├───┼───┼───┼───┼───┼───┤
      * │Sft│ Z │ X │ C │ V │ B │       │ N │ M │ , │ . │ / │Sft│
      * └───┴───┴───┴───┴───┴───┘       └───┴───┴───┴───┴───┴───┘
      *               ┌───┐                   ┌───┐
      *               │GUI├───┐           ┌───┤Alt│
      *               └───┤Bsp├───┐   ┌───┤Ent├───┘
      *                   └───┤   │   │   ├───┘
      *                       └───┘   └───┘
      */
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

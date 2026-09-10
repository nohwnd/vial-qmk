// Copyright 2023 Thomas Haukland (@tompi)
// SPDX-License-Identifier: GPL-2.0-or-later

#pragma once

/*
 * Feature disable options
 *  These options are also useful to firmware size reduction.
 */

/* disable debug print */
//#define NO_DEBUG

/* disable print */
//#define NO_PRINT

/* disable action features */
//#define NO_ACTION_LAYER
//#define NO_ACTION_TAPPING
//#define NO_ACTION_ONESHOT

// #define BOTH_SHIFTS_TURNS_ON_CAPS_WORD
// #define WS2812_PIO_USE_PIO1 // Force the usage of PIO1 peripheral, by default the WS2812 implementation uses the PIO0 peripheral
//#define WS2812_TRST_US 80
// #define WS2812_BYTE_ORDER WS2812_BYTE_ORDER_RGB
// #define RGB_MATRIX_DEFAULT_VAL 32

// A bare DEBOUNCE 5 lost the chatter filtering and made 's' repeat on its own.
// sym_eager_pk was tried to get the latency back, but it reports the press on
// the first transition, so the bounce went through as a second press and 'b'
// and 'r' doubled. The stock sym_defer_pk waits the window out and reports once.
#define DEBOUNCE 10

// Handedness is stored in EEPROM, written once on first boot from
// INIT_EE_HANDS_LEFT/RIGHT in the keymap config. MASTER_RIGHT used to derive it
// from usb_bus_detected(), so whichever half held the cable acted as the right
// one and switched to the right-hand pin set. On the left half those pins do
// not match its wiring, its matrix never scanned, and bootmagic on tilde could
// never work there. Build one firmware per half with tools/build-hands.sh.
#define EE_HANDS

// Pick good defaults for enabling homerow modifiers
#define TAPPING_TERM 200
#define QUICK_TAP_TERM 0
// #define PERMISSIVE_HOLD

// #define WS2812_DI_PIN GP16 // The pin connected to the data pin of the LEDs
// #define RGBLIGHT_LED_COUNT 1                     // The number of LEDs connected


#define MAX_DEFERRED_EXECUTORS 32


// #define DEBUG_MATRIX_SCAN_RATE


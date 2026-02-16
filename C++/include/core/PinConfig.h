#pragma once

#include <vector>
#include <cstdint>
#include <algorithm>

/**
 * @file PinConfig.h
 * @brief Board Support Package (BSP) - Pin Definitions & Protection.
 * 
 * This file serves as the Single Source of Truth for hardware connections.
 * It defines which pins are SAFE for application use and which are PROTECTED.
 */

// =============================================================
// PIN DEFINITIONS (Semantic Names)
// =============================================================

// UART0 (Programming / Debug) -> PROTECTED
#define PIN_UART0_TX    1
#define PIN_UART0_RX    3

// UART2 (Peripheral / LoRa / GPS) -> PROTECTED
#define PIN_UART2_TX    17
#define PIN_UART2_RX    16

// Standard UART for Inter-Node Communication (if using UART)
#define PIN_UART_TX     17
#define PIN_UART_RX     16

// I2C (Sensors) -> SAFE (Managed by I2C Driver, but treat as reserved for GPIO)
#define PIN_I2C_SDA     21
#define PIN_I2C_SCL     22

// SPI (SD Card / LoRa) -> SAFE (Managed by SPI Driver)
#define PIN_SPI_MISO    19
#define PIN_SPI_MOSI    23
#define PIN_SPI_SCK     18
#define PIN_SPI_CS      5

// =============================================================
// PROTECTION LIST
// =============================================================

/**
 * @brief List of Pins that must NEVER be controlled as generic GPIO.
 * Attempting to set these via GpioController will satisfy a "Silent Reject" policy.
 */
static const std::vector<uint8_t> PROTECTED_PINS = {
    PIN_UART0_TX, PIN_UART0_RX,  // Serial Monitor / Upload
    PIN_UART2_TX, PIN_UART2_RX,  // Secondary UART
    8, 9, 10, 11                 // ESP32 Internal Flash SPI (Internal)
};

/**
 * @brief Helper to check if a pin is protected.
 */
inline bool isPinProtected(uint8_t pin) {
    for(uint8_t p : PROTECTED_PINS) {
        if(p == pin) return true;
    }
    return false;
}

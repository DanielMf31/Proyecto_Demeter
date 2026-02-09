/**
 * @file main_uart_test.cpp
 * @brief Simple UART TX Test Firmware.
 * 
 * CONTINUOUSLY SENDS 'U' (0x55) ON SERIAL2.
 * Used to verify physical wiring with an oscilloscope or RPi.
 * 
 * Pins:
 *  - RXD2: GPIO 16
 *  - TXD2: GPIO 17
 *  - Baud: 115200
 */

#include <Arduino.h>

#define RXD2 16
#define TXD2 17

void setup() {
    // Debug Serial (USB)
    Serial.begin(115200);
    Serial.println("=== UART HARDWARE TEST ===");
    Serial.printf("TX Pin: %d\n", TXD2);
    Serial.printf("RX Pin: %d\n", RXD2);
    
    // Hardware Serial 2
    Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
}

void loop() {
    // Send a known pattern
    Serial2.print("U"); 
    // Also blink LED 4 to show life
    static bool state = false;
    pinMode(4, OUTPUT);
    digitalWrite(4, state = !state);
    
    Serial.print("."); // Feedback to USB
    delay(500);
}

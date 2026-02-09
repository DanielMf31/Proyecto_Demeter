/**
 * @file main_uart_test.cpp
 * @brief UART Protocol Generator Test
 * 
 * Sends valid Demeter Protocol V2 Frames every 5 seconds.
 * Used to verify Receiver Logic on Raspberry Pi.
 * 
 * Pins: RX=16, TX=17
 * Baud: 115200
 */

#include <Arduino.h>

#define RXD2 16
#define TXD2 17

void setup() {
    Serial.begin(115200);
    Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
    
    Serial.println("=== UART PROTOCOL TEST GENERATOR ===");
    Serial.println("Sending PING and DATA_REPORT every 5 seconds...");
}

void loop() {
    // 1. Send PING (Src=1, Dst=0, Cmd=0x01)
    // CRC: 00+00+01+00+01 = 2
    static const uint8_t pingFrame[] = { 0xFE, 0x00, 0x00, 0x01, 0x00, 0x01, 0x02 };
    
    Serial2.write(pingFrame, sizeof(pingFrame));
    Serial.println(">> TX: PING (Cmd 0x01)");
    delay(2500);

    // 2. Send DATA REPORT (Src=1, Dst=0, Cmd=0x0B)
    // Payload: Temp 25.00 (2500 -> 09C4 -> C4 09), Hum 60.00 (6000 -> 1770 -> 70 17)
    // Sum: 04+00+01+00+0B + C4+09+70+17 = 356 -> CRC 100 (0x64)
    static const uint8_t dataFrame[] = { 
        0xFE, 0x04, 0x00, 0x01, 0x00, 0x0B, 
        0xC4, 0x09, 0x70, 0x17, 
        0x64 
    };
    
    Serial2.write(dataFrame, sizeof(dataFrame));
    Serial.println(">> TX: DATA REPORT (Cmd 0x0B)");
    delay(2500);
}

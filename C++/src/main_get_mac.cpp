#include <Arduino.h>
#include <WiFi.h>

void setup() {
    Serial.begin(115200);
    while(!Serial) delay(10);
    delay(1000);
    Serial.println("\n\n=== ESP32 MAC Address Utility ===");
    WiFi.mode(WIFI_STA);
    Serial.print("MAC Address: ");
    Serial.println(WiFi.macAddress());
    Serial.println("=================================");
    Serial.println("Press ENTER to get MAC again...");
}

void loop() {
    if (Serial.available()) {
        while(Serial.available()) Serial.read(); // Clear buffer
        Serial.print("MAC Address: ");
        Serial.println(WiFi.macAddress());
    }
    delay(100);
}

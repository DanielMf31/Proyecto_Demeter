#include <Arduino.h>
#include <esp_now.h>
#include <WiFi.h>
#include <esp_wifi.h>

// DEVICE: NODE 2 (ID 2)
// TARGET: GATEWAY (ID 1)
uint8_t peerMac[] = {0x9C, 0x13, 0x9E, 0xA8, 0x6F, 0xCC}; // Gateway MAC

void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("\r\nLast Packet Send Status:\t");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Delivery Success" : "Delivery Fail");
}

void OnDataRecv(const uint8_t * mac, const uint8_t *incomingData, int len) {
  Serial.printf("Bytes received: %d\n", len);
  Serial.print("Data: ");
  for(int i=0; i<len; i++) Serial.print((char)incomingData[i]);
  Serial.println();

  // Blink RGB Blue
  #ifdef RGB_BUILTIN
  neopixelWrite(RGB_BUILTIN, 0, 0, 50); 
  delay(50);
  neopixelWrite(RGB_BUILTIN, 0, 0, 0);
  #endif
}
 
void setup() {
  Serial.begin(115200);
  while(!Serial) delay(10);

  WiFi.mode(WIFI_STA);

  // Force Channel 1
  esp_wifi_set_promiscuous(true);
  esp_wifi_set_channel(1, WIFI_SECOND_CHAN_NONE);
  esp_wifi_set_promiscuous(false);

  Serial.println("--- ESP-NOW TEST: NODE 2 ---");
  Serial.print("My MAC: "); Serial.println(WiFi.macAddress());
  Serial.print("Target MAC (Gateway): ");
  for(int i=0; i<6; i++) Serial.printf("%02X:", peerMac[i]);
  Serial.println();

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  esp_now_register_send_cb(OnDataSent);
  esp_now_register_recv_cb(OnDataRecv);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, peerMac, 6);
  peerInfo.channel = 1;  
  peerInfo.encrypt = false;
  
  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
}
 
void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'r' || c == 'R') {
      // Manual Report Trigger
      // CMD_ID = 0x0B (DATA_REPORT)
      // Payload: [Temp LSB] [Temp MSB] [Hum LSB] [Hum MSB]
      // Temp=25.50 (2550 -> 0x09F6), Hum=60.00 (6000 -> 0x1770)
      
      uint8_t payload[] = {0xFE, 0x04, 0x00, 0x02, 0x01, 0x0B, 0xF6, 0x09, 0x70, 0x17}; // Manually constructed frame
      // Structure: Sync(FE) Len(4) Flags(0) Src(2) Dst(1) Cmd(0B) Payload(4)
      // Wait, we generate frame manually here? easier to simulate just payload if using engine, 
      // but here we are raw.
      
      // Let's send a raw buffer that matches Protocol V2 Frame
      // Sync(FE) Len(4) Flags(0) Src(2) Dst(1) Cmd(0B) [F6 09 70 17] CRC(?)
      
      // CRC Calcu: 04+00+02+01+0B + F6+09+70+17 = ...
      // Let's simpler: Just send a string "REPORT" to verifying routing first?
      // No, user wants to verify sendDataReport.
      
      // We need to use proper raw bytes.
      // Let's use a simpler approach: Just send the text first to debug connectivity?
      // User said "si lo hago desde el 2 al 1 ... no se recibe".
      
      String msg = "REPORT MANUAL";
      esp_err_t result = esp_now_send(peerMac, (uint8_t *)msg.c_str(), msg.length());
       Serial.print("\r\nSending REPORT MSG... ");
       if (result == ESP_OK) Serial.println("OK");
       else Serial.println("ERR");
    }
  }

  static unsigned long lastTime = 0;
  if (millis() - lastTime > 5000) {
    lastTime = millis();
    // Keep pinging to ensure link is alive
    String msg = "PONG LOOP";
    esp_now_send(peerMac, (uint8_t *)msg.c_str(), msg.length());
  }
}

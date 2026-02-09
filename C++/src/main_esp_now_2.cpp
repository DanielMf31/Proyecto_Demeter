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
  static unsigned long lastTime = 0;
  if (millis() - lastTime > 2000) {
    lastTime = millis();
    String msg = "PONG from Node 2";
    esp_err_t result = esp_now_send(peerMac, (uint8_t *)msg.c_str(), msg.length());
    
    if (result == ESP_OK) {
      Serial.println("Sent PONG");
    } else {
      Serial.println("Error sending the data");
    }
  }
}

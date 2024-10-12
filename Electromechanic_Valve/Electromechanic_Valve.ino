#include "ELECTROMECHANIC_VALVE.h"

void setup() {
 Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  OP_DEVICE_SYNC_Wrapper( ID_DEVICE, DEVICE_TYPE, TAG, DEVICE_DESCRIPTION);
  server.on("/", HTTP_POST, ServerHandler);
  server.begin();
}

void loop() {
  server.handleClient();
}




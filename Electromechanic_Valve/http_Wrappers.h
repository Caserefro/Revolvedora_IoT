#ifndef HTTP_WRAPPERS_H
#define HTTP_WRAPPERS_H


void httpGETRequest(String &serverName, String &payload) {  //Not used.
  if (WiFi.status() == WL_CONNECTED) {

    HTTPClient http;
    http.begin(serverName);  //HTTP
    Serial.print("[HTTP] GET...\n");
    int httpCode = http.GET();
    // httpCode will be negative on error
    if (httpCode > 0) {
      // HTTP header has been send and Server response header has been handled
      Serial.printf("[HTTP] GET... code: %d\n", httpCode);
      // file found at server
      if (httpCode == HTTP_CODE_OK) {
        payload = http.getString();
        Serial.println(payload);
      }
    } else {
      Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
    }

    http.end();
  }
}

bool postData(String &serverName, String &payload, String &response) {
  if (WiFi.status() == WL_CONNECTED) {  // Check WiFi connection status
    HTTPClient http;
    http.begin(serverName);  // Specify the URL
    http.addHeader("Content-Type", "text/plain");
    // Send HTTP POST request
    int httpResponseCode = http.POST(payload);
    Serial.println(httpResponseCode);
    // Check the returning code
    if (httpResponseCode > 0) {
      response = http.getString();  // Get the response to the request

      Serial.println(response);  // Print request answer
      http.end();                // Free resources
      return 1;
    } else {
      Serial.print("Error on sending POST: ");
      Serial.println(httpResponseCode);
      http.end();  // Free resources
      return 0;
    }

    http.end();  // Free resources
  } else {
    Serial.println("Error in WiFi connection");

    return 0;
  }
  return 1;
}

// Server Handler for receiving commands --------------------------
void ServerHandler() {
  if (server.hasArg("plain")) {
    String body = server.arg("plain");
    Serial.println("Received body: ");
    Serial.println(body);
    String Package = "ACK";
    // Response(body, Package);  MIGHT no be needed.
    server.send(200, "plain", Package);

    JsonDocument JsonPackageReceived;
    deserializeJson(JsonPackageReceived, body);
    if (JsonPackageReceived["Operation"] == OP_VALVE_SETPOINT_CONTROL) {
      SetPoint = JsonPackageReceived["SetPoint"];
      Serial.println(SetPoint);
    }
  } else {
    server.send(400, "plain", "No body received");
  }
}

void Package_OP_DEVICE_SYNC(JsonDocument &JsonPackagetoSend, String &PackagetoSend, int ID_DEVICE, String &DEVICE_TYPE, String &TAG, String &DEVICE_DESCRIPTION) {  //Client used for request that dont add any special parameters.
  JsonPackagetoSend["Operation"] = OP_DEVICE_SYNC;
  JsonPackagetoSend["ID"] = ID_DEVICE;
  JsonPackagetoSend["IP"] = WiFi.localIP();
  JsonPackagetoSend["Type"] = DEVICE_TYPE;
  JsonPackagetoSend["Tag"] = TAG;
  JsonPackagetoSend["DEVICE_DESCRIPTION"] = DEVICE_DESCRIPTION;
  serializeJson(JsonPackagetoSend, PackagetoSend);
  Serial.println("PackagetoSend");
  Serial.println(PackagetoSend);
}

void OP_DEVICE_SYNC_Wrapper (int ID_DEVICE, String &DEVICE_TYPE, String &TAG, String &DEVICE_DESCRIPTION) {
  String response = "";
  String Package = "";
  JsonDocument doc;
  Package_OP_DEVICE_SYNC(doc, Package, ID_DEVICE, DEVICE_TYPE, TAG, DEVICE_DESCRIPTION);
  if (!postData(ServerAdr + "/", Package, response)) {
    response = "error posting data";
    return;
  }
  Serial.println(response);
  return;
}

void Package_OP_SENSOR_DATA(JsonDocument &JsonPackagetoSend, String &PackagetoSend) {  //Client used for request that dont add any special parameters.
  JsonPackagetoSend["Operation"] = OP_SENSOR_DATA;
  JsonPackagetoSend["Flow"] = SensorData.Flow;
  JsonPackagetoSend["AngleofValve"] = SensorData.AngleofValve;
  JsonPackagetoSend["ValveOpeningPercentage"] = SensorData.ValveOpeningPercentage;
  serializeJson(JsonPackagetoSend, PackagetoSend);
  Serial.println("PackagetoSend");
  Serial.println(PackagetoSend);
}

void OP_SENSOR_DATA_Wrapper() {
  String response = "";
  String Package = "";
  JsonDocument doc;
  Package_OP_SENSOR_DATA(doc, Package);  //change this one for the one pointed in the
  if (!postData(ServerAdr+"/", Package, response)) {
    response = "error posting data";
    return;
  }
  Serial.println(response);
  return;
}


#endif

#ifndef ESP32_AC_LORA_H
#define ESP32_AC_LORA_H

#include <WiFi.h>
#include <WebServer.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

WebServer server(80);
String ServerAdr = "http://192.168.100.32:5000";

String requestBody;

int ID_DEVICE = 1;
String DEVICE_TYPE = "VALVE";
String TAG = "TAG-NUM";
String DEVICE_DESCRIPTION = "Intake valve for tank #1.";

#define OP_SERVER_PING 10
#define OP_DEVICE_SYNC 11
#define OP_SENSOR_DATA 12
#define OP_VALVE_SETPOINT_CONTROL 13 

static TaskHandle_t Step1_Task = NULL;  //Pending.
static TaskHandle_t Step2_Task = NULL;

struct SensorData {
  double Flow = 0;
  double AngleofValve = 0;
  double ValveOpeningPercentage = 0;
} SensorData;

double SetPoint = 0; 

#include "Credentials.h"
#include "Flowmeter.h"
#include "Valve.h"
#include "http_Wrappers.h"
#endif

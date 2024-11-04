#ifndef MIXER_H
#define MIXER_H

#include <WiFi.h>
#include <WebServer.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

WebServer server(80);
String ServerAdr = "http://192.168.100.32:5000";

String requestBody;

int ID_DEVICE1 = 7;
String DEVICE_TYPE1 = "Liquid Level Meter";
String TAG1 = "TAG-NUM";
String PLACE1 = "Tank #1";
String DEVICE_DESCRIPTION1 = "Intake valve for tank #1.";

int ID_DEVICE2 = 8;
String DEVICE_TYPE2 = "Mixer Motor";
String TAG2 = "TAG2-NUM2";
String PLACE2 = "Tank #1";
String DEVICE_DESCRIPTION2 = "Mixer Motor for tank #1.";

#define OP_SERVER_PING 10
#define OP_DEVICE_SYNC 11
#define OP_SENSOR_DATA 12
#define OP_VALVE_SETPOINT_CONTROL 13 

static TaskHandle_t Timer_Task = NULL;

hw_timer_t* timer = NULL;
uint8_t timer_id = 0;
uint16_t prescaler = 80;             // Between 0 and 65 535
int threshold = (1000000 / 2) * 60;  // 64 bits value (limited to int size of 32bits)
void IRAM_ATTR timer_isr();

struct SensorData {
  double LiquidLevel = 0;
  bool State = 1;
} SensorData;

#include "Credentials.h"
#include "http_Wrappers.h"
#endif

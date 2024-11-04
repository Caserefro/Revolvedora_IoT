#ifndef ELECTROMECHANIC_VALVE_H
#define ELECTROMECHANIC_VALVE_H

#include <WiFi.h>
#include <WebServer.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

WebServer server(80);
String ServerAdr = "http://192.168.100.32:5000";

String requestBody;

int ID_DEVICE1 = 1;
String DEVICE_TYPE1 = "Flowmeter";
String TAG1 = "TAG2-NUM2";
String PLACE1 = "Tank #1";
String DEVICE_DESCRIPTION1 = "Flowmeter for tank #1.";

int ID_DEVICE2 = 2;
String DEVICE_TYPE2 = "Electromechanical Valve";
String TAG2 = "TAG-NUM";
String PLACE2 = "Tank #1";
String DEVICE_DESCRIPTION2 = "Intake valve for tank #1.";

int FreqMinServo = 400;
int FreqMaxServo = 2400;

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

volatile int pulseCount = 0;  // Variable to store pulse count
int flowRatePin = 1;          // Pin connected to flowmeter signal
unsigned long lastTimeFlowSensor = 0;   // Variable to track time for flow calculation
float flowRate = 0;           // Calculated flow rate in L/min
// YF-B1 flowmeter constant 
const float calibrationFactor = 11; // pulses per second per liter/minute


struct SensorData {
  double Flow = 0;
  double AngleofValve = 0;
  double ValveOpeningPercentage = 0;
} SensorData;

double SetPoint = 0; 

#include "Credentials.h"
#include "Valve.h"
#include "http_Wrappers.h"
#endif

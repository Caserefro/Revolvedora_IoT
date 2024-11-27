#ifndef ELECTROMECHANIC_VALVE_H
#define ELECTROMECHANIC_VALVE_H

#include <WiFi.h>
#include <WebServer.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

WebServer server(80);
//String ServerAdr = "http://192.168.100.32:5000";
String ServerAdr = "http://192.168.209.73:5000";
String requestBody;


int ID_DEVICE1 = 1;
String DEVICE_TYPE1 = "Flowmeter";
String TAG1 = "FT-102";
String PLACE1 = "Tank #3";
String DEVICE_DESCRIPTION1 = "Intake Flowmeter for tank #3.";


int ID_DEVICE2 = 2;
String DEVICE_TYPE2 = "Electromechanical Valve";
String TAG2 = "FC-103";
String PLACE2 = "Tank #3";
String DEVICE_DESCRIPTION2 = "Intake valve for tank #3.";


/*
int ID_DEVICE1 = 3;
String DEVICE_TYPE1 = "Flowmeter";
String TAG1 = "FT-203";
String PLACE1 = "Tank #3";
String DEVICE_DESCRIPTION1 = "Intake Flowmeter for tank #3.";

int ID_DEVICE2 = 4;
String DEVICE_TYPE2 = "Electromechanical Valve";
String TAG2 = "FC-202";
String PLACE2 = "Tank #1";
String DEVICE_DESCRIPTION2 = "Intake valve for tank #2.";
*/

/*
int ID_DEVICE1 = 5;
String DEVICE_TYPE1 = "Flowmeter";
String TAG1 = "FT-304";
String PLACE1 = "Tank #3";
String DEVICE_DESCRIPTION1 = "Output Flowmeter for tank #3.";

int ID_DEVICE2 = 6;
String DEVICE_TYPE2 = "Electromechanical Valve";
String TAG2 = "FT-303";
String PLACE2 = "Tank #3";
String DEVICE_DESCRIPTION2 = "Output valve for tank #3.";
*/

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
int threshold = (1000000 / 2) * 5;  // 64 bits value (limited to int size of 32bits)
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

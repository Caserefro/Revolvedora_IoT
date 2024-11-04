#include "ELECTROMECHANIC_VALVE.h"

void TimerTask(void *parameters) {
  while (1) {
    Serial.println("TimerTask ran succesfull --------------------------");
    noInterrupts();                     // Disable interrupts while calculating the flow rate
    float pulseFrequency = pulseCount;  // Store pulse count locally
    pulseCount = 0;                     // Reset the pulse count for the next second
    interrupts();                       // Enable interrupts again

    // Calculate the flow rate in L/min
    SensorData.Flow = (pulseFrequency / calibrationFactor);
    // Print the flow rate
    Serial.print("Flow rate: ");
    Serial.print(SensorData.Flow);
    Serial.println(" L/min");

    OP_SENSOR_DATA_Wrapper();
    vTaskSuspend(NULL);
  }
}

void IRAM_ATTR countPulse() {
  pulseCount++;  // Increment the pulse count
}

void IRAM_ATTR timer_isr() {  //mutex not needed
  vTaskResume(Timer_Task);    // Resume the TimerTask
}


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

  Serial.begin(115200);  // Start the serial communication
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  myservo.setPeriodHertz(50);            // standard 50 hz servo
  myservo.attach(servoPin, FreqMinServo, FreqMaxServo);  // attaches the servo on pin 18 to the servo object
  MoveValve(0);

  pinMode(flowRatePin, INPUT);                                              // Set flowmeter pin as input
  attachInterrupt(digitalPinToInterrupt(flowRatePin), countPulse, RISING);  // Attach interrupt to flowmeter pin
  lastTimeFlowSensor = millis();                                            // Initialize the time

  OP_DEVICE_SYNC_Wrapper(ID_DEVICE1, DEVICE_TYPE1, TAG1, PLACE1, DEVICE_DESCRIPTION1);
  OP_DEVICE_SYNC_Wrapper(ID_DEVICE2, DEVICE_TYPE2, TAG2, PLACE2, DEVICE_DESCRIPTION2);
  

  timer = timerBegin(timer_id, prescaler, true);
  timerAttachInterrupt(timer, &timer_isr, true);
  timerAlarmWrite(timer, threshold, true);
  timerAlarmEnable(timer);

  xTaskCreate(TimerTask,
              "Timer Task",
              4096,
              NULL,
              1,
              &Timer_Task);
  server.on("/", HTTP_POST, ServerHandler);
  server.begin();
}

void loop() {
  server.handleClient();  //handles opening the valve
}

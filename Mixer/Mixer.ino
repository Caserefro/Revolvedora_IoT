#include "MIXER.h"

void TimerTask(void *parameters) {
  while (1) {
    Serial.println("TimerTask ran succesfull --------------------------");
    //Measure level in tank and send
    OP_SENSOR_DATA_Wrapper(); 
    vTaskSuspend(NULL);
  }
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

  Serial.begin(115200);


  OP_DEVICE_SYNC_Wrapper(ID_DEVICE1, DEVICE_TYPE1, TAG1, PLACE1, DEVICE_DESCRIPTION1); //level Sensor 
  OP_DEVICE_SYNC_Wrapper(ID_DEVICE2, DEVICE_TYPE2, TAG2, PLACE2, DEVICE_DESCRIPTION2); //Mixer (motor)

  timer = timerBegin(timer_id, prescaler, true);
  timerAttachInterrupt(timer, &timer_isr, true);
  timerAlarmWrite(timer, threshold, true);
  timerAlarmEnable(timer); //1min timer. 

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

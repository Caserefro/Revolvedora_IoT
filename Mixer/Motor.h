#ifndef MOTOR_H
#define MOTOR_H

/*
Here a control system needs to be implemented in which the flowrate (L/s) and the potentiometer (Analog, converted to angle)
position are used to output a control signal to the valve. PID?
*/

#include <ESP32Servo.h>

Servo myservo;  // create servo object to control a servo
int servoPin = 5;

void MoveValve(int Degrees) {
  // Allow range from 0 to 90 degrees
  if (Degrees >= 0 && Degrees <= 90) {
      myservo.write(Degrees);  // move the servo to the specified position
  }
}

#endif

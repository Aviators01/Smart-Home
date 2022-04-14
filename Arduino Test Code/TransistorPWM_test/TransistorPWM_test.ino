#include <TimerOne.h>

#define COMonitor 9
#define onPercent 30

void setup(){
  Timer1.initialize(1000); //us
  Timer1.pwm(COMonitor,0);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop(){
  //PWM-1.5v
  digitalWrite(LED_BUILTIN,LOW);
  Timer1.setPwmDuty(COMonitor, (onPercent / 100.0) * 1023);
  delay(10000);
  
  //Fully ON-5v
  digitalWrite(LED_BUILTIN,HIGH);
  Timer1.setPwmDuty(COMonitor,1023);
  delay(5000);
}

#include <TimerOne.h>

#define COMonitor 9
#define onPercent 30
#define CORead A3

void setup(){
  Serial.begin(115200);
  Timer1.initialize(1000); //us
  Timer1.pwm(COMonitor,1023);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(CORead,INPUT);

  //Test
  Timer1.setPwmDuty(COMonitor, (onPercent / 100.0) * 1023);
  delay(10000);
  
  //Preheat
  Timer1.setPwmDuty(COMonitor,1023);
  Serial.println("Pre-heating");
  float prestart = millis();
  while((prestart+60000)>=millis()){
    digitalWrite(LED_BUILTIN,HIGH);
    delay(1500);
    digitalWrite(LED_BUILTIN,LOW);
    delay(1500);
  }
}

void loop(){
  //Fully ON-5v-Heating cycle
  Serial.println("Heating now...");
  digitalWrite(LED_BUILTIN,HIGH);
  Timer1.setPwmDuty(COMonitor,1023);
  delay(60000);
  
  //PWM-1.5v
  Serial.println("Detecting now...");
  digitalWrite(LED_BUILTIN,LOW);
  Timer1.setPwmDuty(COMonitor, (onPercent / 100.0) * 1023);
  float timest = millis();
  while(timest+90000>=millis()){
    digitalWrite(LED_BUILTIN,HIGH);
    Serial.println(analogRead(CORead));
    delay(250);
    digitalWrite(LED_BUILTIN,LOW);
    delay(250);
  }
}

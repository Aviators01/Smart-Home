/*
This is to test the transistor in which we have hooked up to
blink an LED light.
*/

#define base 8

void setup(){
  //Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop(){
  //On
  digitalWrite(LED_BUILTIN,HIGH);
  digitalWrite(base,HIGH);
  delay(2000);
  
  //Off
  digitalWrite(LED_BUILTIN,LOW);
  digitalWrite(base,LOW);
  delay(2000);
}

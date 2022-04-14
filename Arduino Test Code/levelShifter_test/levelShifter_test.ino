void setup() {
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(8,OUTPUT);
}

void loop() {
  //Serial.println("8-high");
  digitalWrite(8,HIGH);
  digitalWrite(LED_BUILTIN, HIGH);
  delay(3000);
  //Serial.println("8-low");
  digitalWrite(8,LOW);
  digitalWrite(LED_BUILTIN, LOW);
  delay(3000);
}

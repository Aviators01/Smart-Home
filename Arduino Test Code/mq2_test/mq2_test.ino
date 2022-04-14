//Test of MQ-2 gas sensor

void setup() {
  Serial.begin(115200);
}

int val=0;
void loop() {
  Serial.print(digitalRead(7));
  Serial.print(" ");
  Serial.println(analogRead(A3));
  delay(200);
}

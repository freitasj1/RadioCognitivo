int reading;

unsigned long startM, beginM;

void setup() {
  Serial.begin(115200);
  //Serial.println("começando...");

}
int vet[1000];

void loop() {

  for (int i = 0; i < 1000; i++) {
    vet[i] = analogRead(A0);
    delay(1);
  }

  for (int i = 0; i < 1000; i++) {
    Serial.println(vet[i]);
  }

}

#include <SPI.h>
#include <RF24.h>

RF24 radio(9, 10); // CE, CSN pinos que você usou

//const byte endereco[6] = "00001"; // Endereço de comunicação

void setup() {
  Serial.begin(9600);
  radio.begin();
  
  //radio.openWritingPipe(endereco);
  
  radio.setPALevel(RF24_PA_HIGH);
  radio.setDataRate(RF24_1MBPS);
  
  radio.stopListening(); // Configura o módulo como transmissor
}

void loop() {
  const char texto[] = "Testando";
  radio.write(&texto, sizeof(texto)); // Envia o pacote
  delay(1000);
  Serial.println("Enviando");
}

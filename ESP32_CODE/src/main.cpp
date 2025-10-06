#include <Arduino.h>
#include <DHT.h>

#define DHTPIN 14
#define DHTTYPE DHT11
#define PIN_RED 27
#define PIN_GREEN 26

DHT dht(DHTPIN, DHTTYPE);

float tempHigh = 33.0;
float tempLow = 19.0;
float humidityHigh = 80.0;
float humidityLow = 20.0;

void checkForCommands();

void setup() {
  Serial.begin(9600);
  Serial.println("DHT!! Desk Confort Detector is Initialized");
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  dht.begin();
}

void loop() {
  checkForCommands();
  delay(2000);
  float Humidity = dht.readHumidity();
  float Temperature = dht.readTemperature();

  if(isnan(Humidity) || isnan(Temperature)){
    Serial.println("Failed to connect to the sensor!");
    digitalWrite(PIN_GREEN, HIGH);
    digitalWrite(PIN_RED, HIGH);
    return;
  }

  if(Humidity > humidityHigh || Humidity < humidityLow || Temperature > tempHigh|| Temperature < tempLow){
    digitalWrite(PIN_RED, HIGH);
    digitalWrite(PIN_GREEN, LOW);
  }else{
    digitalWrite(PIN_RED, LOW);
    digitalWrite(PIN_GREEN, HIGH);
  }

  char buffer[256];
  sprintf(buffer, "T:%f,H:%f", Temperature, Humidity);

  Serial.println(buffer);
}

void checkForCommands(){
  if(Serial.available()>0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    if(command.startsWith("SET:")){
      String values = command.substring(4);

      int firstComma = values.indexOf(',');
      int secondComma = values.indexOf(',', firstComma+1);
      int thirdComma = values.indexOf(',', secondComma+1);

      if(firstComma>0 && secondComma>0 && thirdComma>0){
        String th_str = values.substring(0, firstComma);
        String tl_str = values.substring(firstComma+1, secondComma);
        String hh_str = values.substring(secondComma+1, thirdComma);
        String hl_str = values.substring(thirdComma+1);

        tempHigh = th_str.toFloat();
        tempLow = tl_str.toFloat();
        humidityHigh = hh_str.toFloat();
        humidityLow = hl_str.toFloat();

        Serial.println("OK: Thresholds updated.");
      }
    }
  }
}

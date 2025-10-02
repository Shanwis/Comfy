#include <Arduino.h>
#include <DHT.h>

#define DHTPIN 14
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  Serial.println("DHT!! Desk Confort Detector is Initialized");

  dht.begin();
}

void loop() {
  delay(2000);
  float Humidity = dht.readHumidity();
  float Temperature = dht.readTemperature();

  if(isnan(Humidity) || isnan(Temperature)){
    Serial.println("Failed to connect to the sensor!");
    return;
  }

  char buffer[256];
  sprintf(buffer, "T:%f,H:%f", Temperature, Humidity);

  Serial.println(buffer);
}

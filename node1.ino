#include <Arduino.h>
#include <EEPROM.h>
#define USE_SERIAL Serial
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

WiFiClient client;

const  int sensor1 = 2;
const int sensor2 = 13;

char push_data [ 200 ];
int count1 = 0;
int count2 = 0;
float flowRate1  = 0.0;
float flowRate2  = 0.0;
int  flowMilliLitres1   = 0;
int  flowMilliLitres2   = 0;
int  oldTime  = 0;
char data[100];

const char* ssid = "Mr.XD";
const char* password = "dynamo2818";

int c = 1;

void scount1()
{
  count1++;
}
void scount2()
{
  count2++;
}
void  setup () {
  Serial. begin ( 115200 );
  delay ( 10 );
  WiFi.begin(ssid, password);
  Serial.println("Waiting for the connection...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(2000);
    Serial.print(".");
    if (WiFi.status() == WL_CONNECTED)
    {
      Serial.println();
//      Serial.print("Connected to the SSID: %s", ssid);
      Serial.println(WiFi.localIP());
    }
  }
  attachInterrupt(digitalPinToInterrupt(sensor1), scount1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(sensor2), scount2, CHANGE);
}
void loop() {
  if (((millis() - oldTime) > 5000) || (c == 1))   // Only process counters once per 5 second
  {
    c = 0;
    detachInterrupt(sensor1);
    detachInterrupt(sensor2);
    flowRate1 = ((1000.0 / (millis() - oldTime)) * count1) / 4.5;
    flowMilliLitres1 = (flowRate1 / 60) * 1000;
    Serial.print("Flow rate 1: ");
    Serial.println(int(flowRate1));
    count1 = 0;
    flowRate2 = ((1000.0 / (millis() - oldTime)) * count2) / 4.5;
    oldTime = millis();
    flowMilliLitres2 = (flowRate2 / 60) * 1000;
    Serial.print("Flow rate 2: ");
    Serial.println(int(flowRate2));
    count2 = 0;
    HTTPClient http;
    String postStr1 = "http://192.168.43.222:8080";
    postStr1 += "/";
    postStr1 += String(flowRate1);
    postStr1 += "/";
    postStr1 += String(flowRate2);
    Serial.println(postStr1);
    http.begin(postStr1);
    int httpCode = http.GET();
    if (httpCode > 0) {
      String payload = http.getString();
      Serial.println(payload);
    }
    http.end();

    
    Serial.println("Waiting for 5 seconds\n\n");
    attachInterrupt(digitalPinToInterrupt(sensor1), scount1, CHANGE);
    attachInterrupt(digitalPinToInterrupt(sensor2), scount2, CHANGE);
  }

}

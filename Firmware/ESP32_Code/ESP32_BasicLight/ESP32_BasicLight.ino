#include <WiFi.h>
#include <WiFiClient.h>
#include <WebServer.h>
#include "secrets.h"

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

WebServer server(80); // ESP32 will host a web server on port 80
const int ledPin = 22; // Change this based on your ESP32's LED GPIO

void handleRoot() {
    server.send(200, "text/plain", "ESP32 Light Control");
}

void handleLightOn() {
    digitalWrite(ledPin, LOW);
    server.send(200, "text/plain", "Light On");
}

void handleLightOff() {
    digitalWrite(ledPin, HIGH);
    server.send(200, "text/plain", "Light Off");
}

void setup() {
    pinMode(ledPin, OUTPUT);
    WiFi.begin(ssid, password);
    Serial.begin(115200);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    
    Serial.println("Connected to WiFi");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());

    // Define routes
    server.on("/", handleRoot);
    server.on("/light/on", handleLightOn);
    server.on("/light/off", handleLightOff);

    server.begin();
}

void loop() {
    server.handleClient();
}
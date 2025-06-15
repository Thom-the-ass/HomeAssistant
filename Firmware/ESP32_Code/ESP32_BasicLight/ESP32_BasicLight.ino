#include <WiFi.h>
#include <WebServer.h>
#include "secrets.h"

const char* ssid = WIFI_SSID;
const char* password = WIFI_PASSWORD;

WebServer server(80);
const int ledPin = 22;
bool ledState = false; // Tracks LED state

//Note needed to modify this so Flask server can read the status
void handleLightStatus() {
    server.sendHeader("Access-Control-Allow-Origin", "*"); // Allow all origins
    server.send(200, "text/plain", ledState ? "on" : "off");
}

void handleLightToggle() {
    ledState = !ledState; // Toggle LED state
    //BEcause this is normally on ,we have to invert this :digitalWrite(ledPin, ledState ? HIGH : LOW);
    digitalWrite(ledPin, ledState ? LOW : HIGH);
    server.sendHeader("Access-Control-Allow-Origin", "*"); // Allow all origins
    server.send(200, "text/plain", ledState ? "on" : "off");
}
void setup() {
    pinMode(ledPin, OUTPUT);
    WiFi.begin(ssid, password);
    Serial.begin(115200);

    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }

    Serial.println("Connected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());

    server.on("/light/toggle", handleLightToggle);
    server.on("/light/status", handleLightStatus);
    server.begin();
}

void loop() {
    server.handleClient();
}
#include <WiFi.h>

// === Wi-Fi credentials ===
const char* ssid = "ESP32_AP";       // ESP32 Access Point name
const char* password = "12345678";   // Wi-Fi password

WiFiServer server(80);  // TCP server on port 80

void setup() {
  Serial.begin(115200);

  // Start ESP32 as Access Point
  WiFi.softAP(ssid, password);
  Serial.println("Wi-Fi AP started");
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());

  server.begin(); // Start TCP server
  Serial.println("Server started");

  // Motor pins
  pinMode(27, OUTPUT);
  pinMode(26, OUTPUT);
  pinMode(25, OUTPUT);
  pinMode(33, OUTPUT);
}

void loop() {
  WiFiClient client = server.available();  // Check for incoming client

  if (client) {
    Serial.println("Client connected");

    while (client.connected()) {
      if (client.available()) {
        String command = client.readStringUntil('\n'); // Read command
        command.trim();
        Serial.println("Received: " + command);

        // === Motor control logic ===
        if (command == "go_forward") {
          digitalWrite(27, HIGH);
          digitalWrite(26, LOW);
          digitalWrite(25, HIGH);
          digitalWrite(33, LOW);
        }
        else if (command == "go_back") {
          digitalWrite(26, HIGH);
          digitalWrite(27, LOW);
          digitalWrite(33, HIGH);
          digitalWrite(25, LOW);
        } 
        else if (command == "go_lf") {
          digitalWrite(26, HIGH);
          digitalWrite(27, LOW);
          digitalWrite(25, HIGH);
          digitalWrite(33, LOW);
        } 
        else if (command == "go_rf") {
          digitalWrite(27, HIGH);
          digitalWrite(26, LOW);
          digitalWrite(33, HIGH);
          digitalWrite(25, LOW);
        } 
        else if (command == "stop") {
          digitalWrite(27, LOW);
          digitalWrite(26, LOW);
          digitalWrite(33, LOW);
          digitalWrite(25, LOW);
        }

        client.println("ACK"); // Send acknowledgment to laptop
      }
    }
    client.stop();
    Serial.println("Client disconnected");
  }
}

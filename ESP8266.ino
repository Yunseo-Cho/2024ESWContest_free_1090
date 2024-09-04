#include <Servo.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char *ssid = "HANULSO_2.4G";
const char *password = "hanulso8421";

Servo servo1;
Servo servo2;

// 핀 정의
#define TRIG_PIN D0  // 거리 센서 Trig
#define ECHO_PIN D1  // 거리 센서 Echo

#define LED_PIN_1 D2  // LED 빨강
#define LED_PIN_2 D5  // LED 노랑
#define LED_PIN_3 D6  // LED 초록

#define SERVO_PIN_1 D3  // 서보 모터 1
#define SERVO_PIN_2 D4  // 서보 모터 2

#define MELODY_IC_1 D7  // 멜로디 IC 1 (딩동)
#define MELODY_IC_2 D8  // 멜로디 IC 2 (엘리제를 위하여)

#define BUZZER_PIN D9  // 부저

ESP8266WebServer server(80);

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("Connecting to WiFi");
    Serial.println(attempts);
    attempts++;
    if (attempts > 20) {  
      Serial.println("Failed to connect to WiFi. Restarting...");
      ESP.restart();  
    }
  }
  
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);

  pinMode(MELODY_IC_1, OUTPUT);
  pinMode(MELODY_IC_2, OUTPUT);

  pinMode(BUZZER_PIN, OUTPUT);

  servo1.attach(SERVO_PIN_1);
  servo2.attach(SERVO_PIN_2);

  server.on("/distance", HTTP_GET, handleDistance);
  server.on("/move_servo", handleMoveServo);
  server.on("/control_led", handleControlLED);
  server.on("/start_melody1", handleStartMelody1);
  server.on("/stop_melody1", handleStopMelody1);
  server.on("/start_melody2", handleStartMelody2);
  server.on("/stop_melody2", handleStopMelody2);
  server.on("/play_buzzer", handlePlayBuzzer);

  server.begin();
}

void handleDistance() {
  long duration, distance;
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  server.send(200, "text/plain", String(distance));
}

void handleMoveServo() {
  if (server.hasArg("angle1")) {
    int angle1 = server.arg("angle1").toInt();
    servo1.write(angle1);
  }
  
  if (server.hasArg("angle2")) {
    int angle2 = server.arg("angle2").toInt();
    servo2.write(angle2);
  }

  if (server.hasArg("angle1") || server.hasArg("angle2")) {
    server.send(200, "text/plain", "Servo(s) moved");
  } else {
    server.send(400, "text/plain", "Invalid request");
  }
}




void handleControlLED() {
    if (server.hasArg("color") && server.hasArg("state")) {
        String color = server.arg("color");
        String state = server.arg("state");

        int pins[3];  
        int pinCount = 0;

        if (color == "red") {
            pins[0] = LED_PIN_1;
            pinCount = 1;
        } else if (color == "yellow") {
            pins[0] = LED_PIN_2;
            pinCount = 1;
        } else if (color == "green") {
            pins[0] = LED_PIN_3;
            pinCount = 1;
        } else if (color == "all") {
            pins[0] = LED_PIN_1;
            pins[1] = LED_PIN_2;
            pins[2] = LED_PIN_3;
            pinCount = 3;
        } else {
            server.send(400, "text/plain", "Invalid color");
            return;
        }

        if (state == "blink") {
            for (int j = 0; j < 3; j++) {  
                for (int i = 0; i < pinCount; i++) {
                    digitalWrite(pins[i], HIGH);
                }
                delay(500); 

                for (int i = 0; i < pinCount; i++) {
                    digitalWrite(pins[i], LOW);
                }
                delay(500); 
            }
        } else {
            for (int i = 0; i < pinCount; i++) {
                digitalWrite(pins[i], state == "on" ? HIGH : LOW);
            }
        }

        server.send(200, "text/plain", "LED state changed");
    } else {
        server.send(400, "text/plain", "Invalid request");
    }
}



void handleStartMelody1() {
  server.send(200, "text/plain", "Melody 1 started");
  digitalWrite(MELODY_IC_1, HIGH);  
}

void handleStopMelody1() {
  server.send(200, "text/plain", "Melody 1 stopped");
  digitalWrite(MELODY_IC_1, LOW); 
}

void handleStartMelody2() {
  server.send(200, "text/plain", "Melody 2 started");
  digitalWrite(MELODY_IC_2, HIGH);  
}

void handleStopMelody2() {
  server.send(200, "text/plain", "Melody 2 stopped");
  digitalWrite(MELODY_IC_2, LOW); 
}


void handlePlayBuzzer() {
    tone(BUZZER_PIN, 1000);
    delay(500);
    noTone(BUZZER_PIN);  
 
  server.send(200, "text/plain", "Buzzer played");
}

void loop() {
    server.handleClient();
}

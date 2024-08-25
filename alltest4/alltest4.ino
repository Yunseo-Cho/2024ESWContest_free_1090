#include <Servo.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

const char* ssid = "U+Net9641";
const char* password = "34512149M#";

Servo servo1;
Servo servo2;

// 핀 정의
#define TRIG_PIN D0  // 거리 센서 Trig
#define ECHO_PIN D1  // 거리 센서 Echo

#define LED_PIN_1 D2  // LED 1
#define LED_PIN_2 D5  // LED 2
#define LED_PIN_3 D6  // LED 3

#define SERVO_PIN_1 D3  // 서보 모터 1
#define SERVO_PIN_2 D4  // 서보 모터 2

#define MELODY_IC_1 D7  // 멜로디 IC 1
#define MELODY_IC_2 D8  // 멜로디 IC 2

#define BUZZER_PIN D9  // 능동 부저

ESP8266WebServer server(80);

void setup() {
  // 시리얼 모니터 초기화
  Serial.begin(115200);

  // WiFi 연결
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print("Connecting to WiFi");
    Serial.println(attempts);
    attempts++;
    if (attempts > 20) {  // 20번 시도 후 실패 시 코드 재시작
      Serial.println("Failed to connect to WiFi. Restarting...");
      ESP.restart();  // WiFi 연결 실패 시 재시작
    }
  }
  
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());
  // 핀 설정
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);

  pinMode(MELODY_IC_1, OUTPUT);
  pinMode(MELODY_IC_2, OUTPUT);

  pinMode(BUZZER_PIN, OUTPUT);

  // 서보 모터 초기화
  servo1.attach(SERVO_PIN_1);
  servo2.attach(SERVO_PIN_2);

  // 엔드포인트 설정
  server.on("/distance", HTTP_GET, handleDistance);
  server.on("/move_servo", handleMoveServo);
  server.on("/control_led", handleControlLED);
  server.on("/play_melody1", handlePlayMelody1);
  server.on("/play_melody2", handlePlayMelody2);
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
  if (server.hasArg("angle")) {
    int angle = server.arg("angle").toInt();
    servo1.write(angle);
    servo2.write(angle);
    
    server.send(200, "text/plain", "Servo moved");
  } else {
    server.send(400, "text/plain", "Invalid request");
  }
}

void handleControlLED() {
    if (server.hasArg("color") && server.hasArg("state")) {
        String color = server.arg("color");
        String state = server.arg("state");

        int pins[3];  // 모든 LED 핀 배열
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
            for (int j = 0; j < 3; j++) {  // 5번 깜빡임
                for (int i = 0; i < pinCount; i++) {
                    digitalWrite(pins[i], HIGH);
                }
                delay(500);  // 0.5초 동안 켬

                for (int i = 0; i < pinCount; i++) {
                    digitalWrite(pins[i], LOW);
                }
                delay(500);  // 0.5초 동안 끔
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



void handlePlayMelody1() {
  // 클라이언트에게 즉시 응답을 보냄
  server.send(200, "text/plain", "Melody 1 started");
  
  // 멜로디 1 (딩동)을 재생
  digitalWrite(MELODY_IC_1, HIGH);  // Turn on transistor 1
  delay(1500);  // Play for 1.5 seconds
  digitalWrite(MELODY_IC_1, LOW);   // Turn off transistor 1
  
  // 추가 딜레이
  delay(100);  // Pause for 2 seconds
}

void handlePlayMelody2() {
  // 클라이언트에게 즉시 응답을 보냄
  server.send(200, "text/plain", "Melody 2 started");
  
  // 멜로디 2 (엘리제를 위하여)를 재생
  digitalWrite(MELODY_IC_2, HIGH);  // Turn on transistor 2
  delay(2500);  // Play for 3 seconds
  digitalWrite(MELODY_IC_2, LOW);   // Turn off transistor 2
  
  // 추가 딜레이
  delay(100);  // Pause for 2 seconds
}



void handlePlayBuzzer() {
  // 0.5초 간격으로 5번 울리는 부저

    tone(BUZZER_PIN, 1000);  // 1kHz 주파수로 톤 발생
    delay(500);
    noTone(BUZZER_PIN);      // 부저 끄기
 
  server.send(200, "text/plain", "Buzzer played");
}

void loop() {
    server.handleClient();
}

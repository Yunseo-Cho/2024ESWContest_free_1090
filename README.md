# 🚧 Smart Bollard with License Plate Recognition

차량 번호판을 자동으로 인식하여 등록 차량의 출입을 제어하는 **AI 기반 스마트 볼라드 시스템**입니다.

기존 수동식 또는 원격 제어식 볼라드의 불편함을 개선하기 위해,
카메라를 통해 차량 번호판을 인식하고 데이터베이스의 등록 차량 여부를 확인하여
볼라드를 자동으로 제어하는 시스템을 구현했습니다.

---

## 📌 Project Overview

- **Project**: AI 기반 스마트 볼라드
- **Period**: 2024
- **Team**: 3명
- **My Role**: 차량 번호판 인식 알고리즘 구현
- **Field**: Computer Vision / Embedded System / IoT

### 주요 기능

1. 카메라를 통한 차량 영상 획득
2. 차량 번호판 영역 탐지
3. OCR 기반 번호판 문자 인식
4. 데이터베이스 등록 차량 확인
5. 인식 결과에 따른 볼라드 자동 제어

---

## ⚙️ System Architecture

전체 시스템은 다음과 같은 흐름으로 동작합니다.

Camera
↓
License Plate Detection
↓
Image Preprocessing
↓
OCR
↓
License Plate Number
↓
Database Verification
↓
Bollard Control

차량이 접근하면 카메라에서 영상을 획득하고 번호판 영역을 탐지합니다.
추출된 번호판 영역에 OCR을 적용하여 차량 번호를 인식한 뒤,
데이터베이스에 등록된 차량인지 확인합니다.

등록 차량으로 확인되면 제어 시스템으로 신호를 전달하여
볼라드가 자동으로 동작하도록 구성했습니다.

---

## 🧠 License Plate Recognition Pipeline

제가 담당한 번호판 인식 과정은 다음과 같이 구성했습니다.

### 1. Image Acquisition
카메라에서 차량 이미지를 획득합니다.

### 2. Image Preprocessing
번호판 인식 성능 향상을 위해 영상 전처리를 수행합니다.

- Grayscale 변환
- Gaussian Blur
- Edge Detection
- Noise Reduction

### 3. License Plate ROI Detection
영상의 윤곽선과 형태 정보를 이용하여
번호판 후보 영역을 탐색하고 ROI(Region of Interest)를 추출합니다.

### 4. OCR
추출된 번호판 영역을 OCR 엔진에 입력하여
번호판 문자를 텍스트 데이터로 변환합니다.

### 5. Post-processing
OCR 결과에서 불필요한 문자를 제거하고
차량 번호판 형식에 맞도록 결과를 정제합니다.

---

## 🛠 Tech Stack

### Computer Vision
- Python
- OpenCV
- OCR

### Embedded / Hardware
- Raspberry Pi
- Camera
- Servo Motor
- Ultrasonic Sensor

### Communication / Database
- SQL Database
- Network Communication



---

## 🔧 Repository Structure

```text
.
├── CameraWebServer.ino    # Camera web server
├── ESP8266.ino            # ESP8266 control
├── app_httpd.cpp          # HTTP server implementation
├── camera_index.h         # Camera web interface
├── camera_pins.h          # Camera pin configuration
├── client.py              # Client communication / recognition
├── database.sql           # Vehicle database
└── ci.json                # Configuration

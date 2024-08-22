'''
pip install opencv-python-headless
pip install easyocr
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117

pip install ultralytics
pip install pillow
'''

import torch
import requests
import time
import cv2  # OpenCV 라이브러리
import numpy as np
import matplotlib.pyplot as plt
import easyocr
import re
import os

from PIL import Image
from ultralytics import YOLO

# GPU가 없는 경우 CPU로 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# 예제 텐서를 CPU에 할당
tensor = torch.tensor([1.0, 2.0, 3.0]).to(device)
print(tensor)

esp32_ip = r"http://192.168.0.29/"

def stream_video():
    cap = cv2.VideoCapture(f"{esp32_ip}/stream")
    if not cap.isOpened():
        print("Failed to open video stream")
        return None
    return cap

def get_distance():
    response = requests.get(f"{esp32_ip}/get_distance")
    if response.status_code == 200:
        return float(response.text)
    else:
        print("Failed to get distance")
        return None

def move_servo(angle):
    if 0 <= angle <= 180:
        response = requests.get(f"{esp32_ip}/move_servo?angle={angle}")
        if response.status_code == 200:
            print(f"Servo moved to angle: {angle}")
        else:
            print("Failed to move servo")
    else:
        print("Invalid angle. Must be between 0 and 180.")

def control_led(color, state):
    response = requests.get(f"{esp32_ip}/control_led?color={color}&state={state}")
    if response.status_code == 200:
        print(f"{color.capitalize()} LED turned {state}")
    else:
        print(f"Failed to control {color} LED")

def play_melody(melody):
    response = requests.get(f"{esp32_ip}/play_melody?melody={melody}")
    if response.status_code == 200:
        print(f"Melody {melody} played successfully")
    else:
        print(f"Failed to play Melody {melody}")

def play_buzzer():
    response = requests.get(f"{esp32_ip}/play_buzzer")
    if response.status_code == 200:
        print("Buzzer played successfully")
    else:
        print("Failed to play buzzer")

def detect_license_plate(frame):
    # YOLOv8 모델 로드
    model = YOLO(r'C:\Users\yunse\OneDrive\바탕 화면\하늘소\볼라드\best.pt')
    
    image = cv2.imread(frame)
    results = model(image) # 모델로 예측 수행
    
    # 예측 결과에서 자동차 번호판 영역 추출 및 문자 인식
    for result in results:
        boxes = result.boxes
        for box in boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            license_plate = image[y1:y2, x1:x2]

    #그레이스케일 변환
    gray = cv2.cvtColor(license_plate, cv2.COLOR_BGR2GRAY)

    #가우시안 블러 적용
    img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

    #이미지 이진화
    img_thresh = cv2.adaptiveThreshold(
        img_blurred,
        maxValue=255.0,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=19,
        C=9
    )

    #extract_plate_characters
    plate_img = cv2.equalizeHist(img_thresh)
    _, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.5, fy=1.5)
    plate_img = cv2.GaussianBlur(plate_img, (3, 3), 0)
    #plate_img = cv2.adaptiveThreshold(plate_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)

    reader = easyocr.Reader(['ko'], gpu=torch.cuda.is_available())
    try:
        chars = reader.readtext(plate_img, detail=0)[0]
    except IndexError:
        chars = ""
    '''
    # 결과 필터링: 형식에 맞는 텍스트 추출
    result_chars = ''
    has_digit = False
    # 정규식 패턴: 2-3개의 숫자, 1개의 한글, 4개의 숫자
    pattern = re.compile(r'\d{2,3}[가-힣]\d{4}')
    for c in chars:
        if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
            if c.isdigit():
                    has_digit = True
            result_chars += c
    # 정규식 패턴으로 필터링
    result_chars = pattern.findall(result_chars)
    '''
    result_chars = chars #정규식 패턴으로 필터링 한다면 필요 없는 코드
    ''' 결과 출력
    print(result_chars)

    # 이미지 출력
    plt.imshow(plate_img, cmap='gray')
    plt.show()
    '''
    return result_chars

def main():
    current_state = "Basic State"
    start_time = time.time()

    video_stream = None

    while True:
        distance = 0.3#get_distance()
        
        if current_state == "Basic State":
            if distance is not None and distance <= 1:
                current_state = "Vehicle Detected State"
                control_led("red", "on")
                video_stream = stream_video()  # 차량 감지 시 영상 스트리밍 시작

        elif current_state == "Vehicle Detected State":
            if video_stream:
                ret, frame = video_stream.read()
                if ret:
                    detect_license_plate(frame) # 번호판 인식 코드. return result_chars
                    pass

            if distance is not None:
                if distance <= 0.5:
                    # 차량이 옳다는 조건을 추가로 확인하는 코드
                    # 번호판 인식 결과 확인

                    '''MySQL 데이터베이스 연결'''

                    import mysql.connector

                    def connect_to_database():
                        # MySQL 데이터베이스 연결 설정
                        conn = mysql.connector.connect(
                            host='localhost',        # MySQL 서버 호스트 이름
                            user='root',    # MySQL 사용자 이름
                            password='new03',# MySQL 사용자 비밀번호
                            database='bolla' # 사용할 데이터베이스 이름
                        )
                        return conn

                    # 연결 테스트
                    conn = connect_to_database()
                    if conn.is_connected():
                        print("Database connection successful")
                    else:
                        print("Database connection failed")
                    conn.close()


                    '''인식된 번호판 데이터 비교'''

                    def compare_license_plate(conn, recognized_plate):
                        cursor = conn.cursor()

                        # 데이터베이스에서 번호판 조회
                        query = "SELECT * FROM license_plates WHERE license_plate = %s"
                        cursor.execute(query, (recognized_plate,))

                        # 결과 가져오기
                        result = cursor.fetchone()
                        cursor.close()

                        if result:
                            return True, result
                        else:
                            return False, None

                    def main():
                        # 인식된 번호판 데이터 가져오기
                        recognized_plate = result_chars.replace(' ', '')

                        # 연결 및 번호판 비교
                        conn = connect_to_database()
                        if conn.is_connected():
                            print("Database connection successful")
                            match, data = compare_license_plate(conn, recognized_plate)
                            if match:
                                print("번호판이 일치합니다:", data)
                                correct_car = Truesi
                            else:
                                print("번호판이 일치하지 않습니다.")
                        else:
                            print("Database connection failed")
                        conn.close()
                        
                    if correct_car:
                        current_state = "Authorized State"
                        control_led("green", "on")
                        play_melody(1)
                    else:
                        current_state = "Unauthorized State"
                        control_led("red", "blink")
                        play_buzzer()

        elif current_state == "Authorized State":
            time.sleep(1)
            current_state = "Bollard Lowering State"
            move_servo(0)
            control_led("yellow", "on")
            play_melody(2)

        elif current_state == "Unauthorized State":
            time.sleep(5)
            if distance is not None:
                if distance > 0.5:
                    current_state = "Basic State"
                    control_led("red", "on")
                else:
                    play_buzzer()

        elif current_state == "Bollard Lowering State":
            time.sleep(2)
            current_state = "Parking Standby State"
            control_led("green", "on")
            start_time = time.time()  # 상태 전환 시간 초기화

        elif current_state == "Parking Standby State":
            if time.time() - start_time > 120:
                if distance is not None and distance <= 0.5:
                    current_state = "Parking State"
                    control_led("off", "off")

        elif current_state == "Parking State":
            if distance is not None and distance > 0.5:
                current_state = "Exit State"
                control_led("green", "on")

        elif current_state == "Exit State":
            if distance is not None and distance > 0.5:
                time.sleep(20)
                current_state = "Bollard Raising State"
                move_servo(90)
                control_led("yellow", "on")
                play_melody(2)

        elif current_state == "Bollard Raising State":
            time.sleep(2)
            current_state = "Basic State"
            control_led("red", "on")
            if video_stream:
                video_stream.release()

        time.sleep(1)

if __name__ == "__main__":
    main()

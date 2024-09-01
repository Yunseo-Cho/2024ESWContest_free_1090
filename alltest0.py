import cv2
import numpy as np
import easyocr
import requests
import torch
import re
import mysql.connector
import time

url = "http://192.168.0.29/capture"  # ESP32-CAM의 IP 주소
esp8266_url = "http://192.168.0.39"  # ESP32 제어용 URL
reader = easyocr.Reader(['ko'], gpu=torch.cuda.is_available())

def connect_to_database():
    # MySQL 데이터베이스 연결 설정
    conn = mysql.connector.connect(
        host='localhost',        # MySQL 서버 호스트 이름
        user='root',             # MySQL 사용자 이름
        password='new03',        # MySQL 사용자 비밀번호
        database='bolla'         # 사용할 데이터베이스 이름
    )
    return conn

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

def get_distance():
    distance=0
    try:
        response = requests.get(f"{esp8266_url}/distance")
        distance = float(response.text)
        print(f"Distance: {distance} cm")
        
    except Exception as e:
        print(f"Failed to retrieve data: {e}")

    time.sleep(1)
    return distance

def move_servos(angle1=None, angle2=None):
    params = {}
    
    if angle1 is not None:
        params['angle1'] = angle1
    if angle2 is not None:
        params['angle2'] = angle2

    if params:
        response = requests.get(f"{esp8266_url}/move_servo", params=params)
        if response.status_code == 200:
            print(f"Servo(s) moved to angles: angle1={angle1}, angle2={angle2}")
        else:
            print("Failed to move servo(s)")
    else:
        print("No valid angles provided. Must provide at least one angle between 0 and 180.")

def control_led(color, state):
    response = requests.get(f"{esp8266_url}/control_led?color={color}&state={state}")
    if response.status_code == 200:
        print(f"{color.capitalize()} LED turned {state}")
    else:
        print(f"Failed to control {color} LED")

def play_melody(melody_number):
    if melody_number == 1:
        response = requests.get(f"{esp8266_url}/play_melody1", timeout=10)
    elif melody_number == 2:
        response = requests.get(f"{esp8266_url}/play_melody2", timeout=10)
    else:
        print("Invalid melody number")
        return
    
    if response.status_code == 200:
        print(f"Melody {melody_number} played successfully")
    else:
        print(f"Failed to play Melody {melody_number}")

def play_buzzer():
    response = requests.get(f"{esp8266_url}/play_buzzer")
    if response.status_code == 200:
        print("Buzzer played successfully")
    else:
        print("Failed to play buzzer")

def recognize_license_plate(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0) #지워도 실행 되는지 확인 필요
    img_thresh = cv2.adaptiveThreshold(
        img_blurred,
        maxValue=255.0,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=19,
        C=9
    )

    plate_img = cv2.equalizeHist(img_thresh)
    _, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.5, fy=1.5)
    plate_img = cv2.GaussianBlur(plate_img, (3, 3), 0)

    try:
        chars = reader.readtext(plate_img, detail=0)[0]
    except IndexError:
        chars = ""

    result_chars = ''
    pattern = re.compile(r'\d{2,3}[가-힣]\d{4}')
    for c in chars:
        if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
            result_chars += c
    
    result_chars = pattern.findall(result_chars)
    return result_chars

def main():
    current_state = "Basic State"
    cap = cv2.VideoCapture(url)
    conn = connect_to_database()

    while True:
        distance = get_distance()
        start_time = None

        if current_state == "Basic State":
            control_led("all", "off")
            control_led("red", "on")
            while True:
                distance = get_distance()
                if distance < 40:
                    if start_time is None:
                        start_time = time.time()  
                    elif time.time() - start_time >= 1:
                        current_state = "Vehicle Detected State"
                        break
                else:
                    start_time = None

        elif current_state == "Vehicle Detected State":
            ret, frame = cap.read()
            if ret:
                recognized_plate = recognize_license_plate(frame)
                if recognized_plate:
                    recognized_plate = recognized_plate[0].replace(' ', '')
                    match, data = compare_license_plate(conn, recognized_plate)
                    correct_car = match
                else:
                    correct_car = False

            while True:
                distance = get_distance()
                if distance <= 20:
                    if correct_car:
                        current_state = "Authorized State"
                        break
                    else:
                        current_state = "Unauthorized State"
                        break
                else:
                    time.sleep(1)
                    distance = get_distance()
                    if distance >= 40:
                        current_state = "Basic State"
                        break
            
        elif current_state == "Authorized State":
            control_led("all", "off")
            control_led("green", "on")
            play_melody(1)
            time.sleep(1)
            current_state = "Bollard Lowering State"
            
        elif current_state == "Unauthorized State":
            control_led("all", "off")
            control_led("red", "blink")
            control_led('red', 'on')

            while True:
                distance = get_distance()
                if distance < 20:
                    for _ in range(3):
                        control_led('red', 'on')
                        play_buzzer()
                        control_led('red', 'off')
                        time.sleep(0.3)
                    control_led('red', 'on')
                    time.sleep(3)
                    start_time = None
                elif distance >= 40:
                    if start_time is None:
                        start_time = time.time()  
                    elif time.time() - start_time >= 10:
                        current_state = "Basic State"
                        break

        elif current_state == "Bollard Lowering State":
            control_led("all", "on")
            play_melody(2)
            move_servos(angle1=20, angle2=180)
            current_state = "Parking Standby State"
            
        elif current_state == "Parking Standby State":
            control_led("all", "off")
            control_led("green", "blink")
            control_led("green", "on")
            while True:
                distance = get_distance()

                if distance < 10:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 10:
                        current_state = "Parking State"
                        break
                else:
                    start_time = None

        elif current_state == "Parking State":
            control_led("all", "off")
            start_time = None
            while True:
                distance = get_distance()
                if distance > 10:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 10:
                        current_state = "Exit State"
                        break
                else:
                    start_time = None
                    
        elif current_state == "Exit State":
            control_led("all", "off")
            control_led("green", "blink")
            control_led("green", "on")

            p_start_time = None
            start_time = None
            while True:
                distance = get_distance()
                if distance < 10:
                    start_time = None
                    if p_start_time is None:
                        p_start_time = time.time()
                    elif time.time() - p_start_time >= 10:
                        current_state = "Parking State"
                        break
                else:
                    p_start_time = None
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 10:
                        current_state = "Bollard Raising State"
                        break

        elif current_state == "Bollard Raising State":
            control_led("all", "on")
            play_melody(2)
            move_servos(angle1=180, angle2=20)
            current_state = "Basic State"

    conn.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


import requests
import time
import cv2
import numpy as np
import easyocr
import torch
import re
import mysql.connector

url = "http://192.168.0.52"
url_cam = "http://192.168.0.29/capture"  # ESP32-CAM의 IP 주소

# 번호판 인식 함수
def process_frame(img, reader):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)
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
        chars = []

    result_chars = ''
    pattern = re.compile(r'\d{2,3}[가-힣]\d{4}')
    for c in chars:
        if ord('가') <= ord(c) <= ord('힣') or c.isdigit():
            result_chars += c

    result_chars = pattern.findall(result_chars)
    print(result_chars)
    cv2.imshow("Plate Image", plate_img)
    return result_chars

# 데이터베이스 연결 함수
def connect_to_database():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='new03',
        database='bolla'
    )
    return conn

# 번호판 비교 함수
def compare_license_plate(conn, recognized_plate):
    cursor = conn.cursor()
    query = "SELECT * FROM license_plates WHERE license_plate = %s"
    cursor.execute(query, (recognized_plate,))
    result = cursor.fetchone()
    cursor.close()
    return result is not None

# 비디오 스트리밍 & 번호판 인식 & 데이터베이스 확인
def stream_video(url_cam, reader):
    cap = cv2.VideoCapture(url_cam)
    num_attempts = 0

    while num_attempts < 3:
        img_resp = requests.get(url_cam)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)
        cv2.imshow("ESP32-CAM", img)

        plates = process_frame(img, reader)
        if plates:
            conn = connect_to_database()
            if conn.is_connected():
                print("Database connection successful")
                match_found = False
                for plate in plates:
                    if compare_license_plate(conn, plate):
                        print(f"번호판 {plate}이(가) 데이터베이스와 일치합니다.")
                        cap.release()
                        cv2.destroyAllWindows()
                        conn.close()
                        return True
                num_attempts += 1
                conn.close()
            else:
                print("Database connection failed")
                cap.release()
                cv2.destroyAllWindows()
                return False

    cap.release()
    cv2.destroyAllWindows()
    return False

def get_distance():
    try:
        response = requests.get(f"{url}/distance")
        distance = float(response.text)
        print(f"Distance: {distance} cm")
    except Exception as e:
        print(f"Failed to retrieve data: {e}")
        distance = None

    time.sleep(1)
    return distance   

def move_servos(angle1=None, angle2=None):
    params = {}
    if angle1 is not None:
        params['angle1'] = angle1
    if angle2 is not None:
        params['angle2'] = angle2

    if params:
        response = requests.get(f"{url}/move_servo", params=params)
        if response.status_code == 200:
            print(f"Servo(s) moved to angles: angle1={angle1}, angle2={angle2}")
        else:
            print("Failed to move servo(s)")
    else:
        print("No valid angles provided. Must provide at least one angle between 0 and 180.")

def control_led(color, state):
    response = requests.get(f"{url}/control_led?color={color}&state={state}")
    if response.status_code == 200:
        print(f"{color.capitalize()} LED turned {state}")
    else:
        print(f"Failed to control {color} LED")

def start_melody(melody_number):
    response = requests.get(f"{url}/start_melody{melody_number}")
    if response.status_code == 200:
        print(f"Melody {melody_number} started")
    else:
        print(f"Failed to start Melody {melody_number}")

def stop_melody(melody_number):
    response = requests.get(f"{url}/stop_melody{melody_number}")
    if response.status_code == 200:
        print(f"Melody {melody_number} stopped")
    else:
        print(f"Failed to stop Melody {melody_number}")

def play_buzzer():
    response = requests.get(f"{url}/play_buzzer")
    if response.status_code == 200:
        print("Buzzer played successfully")
    else:
        print("Failed to play buzzer")

def main():
    current_state = "Basic State"
    reader = easyocr.Reader(['ko'], gpu=torch.cuda.is_available())

    while True:
        distance = get_distance()
        start_time = None
        p_start_time=None

        if current_state == "Basic State":
            control_led("all", "off")
            control_led("red", "on")
            while True:
                distance = get_distance()
                if distance and distance < 40:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 2:
                        current_state = "Vehicle Detected State"
                        break
                else:
                    start_time = None

        elif current_state == "Vehicle Detected State":
            result = stream_video(url_cam, reader)
            if result:
                print("번호판이 데이터베이스와 일치합니다.")
            else:
                print("번호판이 데이터베이스와 일치하지 않습니다.")
            
            while True:
                distance = get_distance()
                if distance and distance <= 20:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 2:
                        if result:
                            current_state = "Authorized State"   
                            break
                        else:
                            current_state = "Unauthorized State"
                            break
                else:
                    if distance and distance >= 40:
                        if start_time is None:
                            start_time = time.time()
                        elif time.time() - start_time >= 2:
                            current_state = "Basic State"
                            break

        elif current_state == "Authorized State":
            control_led("all", "off")                       
            control_led("green", "on")                    
            start_melody(1)
            time.sleep(1)  #1초동안 딩동
            stop_melody(1)
            current_state = "Bollard Lowering State"
            
        elif current_state == "Unauthorized State":
            control_led("all", "off")
            control_led("red", "blink")
            control_led('red', 'on')

            while True:
                distance = get_distance()
                if distance and distance < 20:
                    for _ in range(3):
                        play_buzzer()
                        control_led('red', 'off')
                        time.sleep(0.3)
                        control_led('red', 'on')                    
                    time.sleep(3)
                    start_time = None
                elif distance and distance >= 40:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 5:
                        current_state = "Basic State"
                        break

                elif current_state == "Bollard Lowering State":
            control_led("all", "on")
            start_melody(2)
            for i in range(36):
                move_servos(5*i,180 - 5 * i)
            stop_melody(2)
            time.sleep(0.5)
            current_state = "Parking Standby State"
            
            # 안들어오면 기본 상태로 가기
        elif current_state == "Parking Standby State":
            control_led("all", "off")
            control_led("green", "blink")
            control_led("green", "on")
            while True:
                distance = get_distance()
                if distance and distance < 10:
                    start_time=None  # 수정한 부분 #################
                    if p_start_time is None:
                        p_start_time = time.time()
                    elif time.time() - p_start_time >= 5:  
                        current_state = "Parking State"
                        break
                else:
                    p_start_time = None
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 10:
                        current_state = "Bollard Raising State"
                        break

                    

        elif current_state == "Parking State":
            control_led("all", "off")
            start_time = None
            while True:
                distance = get_distance()
                if distance and distance > 10:
                    if start_time is None:
                        start_time = time.time()
                    elif time.time() - start_time >= 5:
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
                if distance and distance < 10:
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
            start_melody(2)
            # 볼라드가 올라가는 경우
            for i in range(36):
                move_servos( 180 - 5* i,5* i)
            stop_melody(2)
            current_state = "Basic State"

if __name__ == "__main__":
    main()

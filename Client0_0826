#esp32-cam과 번호판 인식, 데이터베이스를 제외한 제어 코드

import requests
import time
import cv2  # OpenCV 라이브러리
import numpy as np
import time as t


url = "http://192.168.219.111"

'''
def stream_video():
    cap = cv2.VideoCapture(f"{esp32_ip}/stream")
    if not cap.isOpened():
        print("Failed to open video stream")
        return None
    return cap
'''

#수정함
def get_distance():
    try:
        response = requests.get(f"{url}/distance")
        distance = float(response.text)
        print(f"Distance: {distance} cm")
        
    except Exception as e:
        print(f"Failed to retrieve data: {e}")

    t.sleep(1)
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

def play_melody(melody_number):
    if melody_number == 1:
        response = requests.get(f"{url}/play_melody1", timeout=10)
    elif melody_number == 2:
        response = requests.get(f"{url}/play_melody2", timeout=10)
    else:
        print("Invalid melody number")
        return
    
    if response.status_code == 200:
        print(f"Melody {melody_number} played successfully")
    else:
        print(f"Failed to play Melody {melody_number}")

def play_buzzer():
    response = requests.get(f"{url}/play_buzzer")
    if response.status_code == 200:
        print("Buzzer played successfully")
    else:
        print("Failed to play buzzer")



def main():
    current_state = "Basic State"

    video_stream = None
    
    while True:
        distance = get_distance()
        start_time = None
        #나중에 거리측정이랑 출력 함수 분리하고 싶다
        if current_state == "Basic State":
            control_led("all", "off")
            control_led("red", "on")
            while True:
                distance = get_distance()
                if distance < 40:
                    if start_time is None:
                        start_time = time.time()  # 안정적인 상태 시작 시간 기록
                    elif time.time() - start_time >= 1:
                        current_state = "Vehicle Detected State"
                        #video_stream = stream_video()  # 차량 감지 시 영상 스트리밍 시작
                        break
                else:
                    start_time = None

        #이것도 차량 감지 상태가 됐다가 10초동안 차없으면 다시 기본상태로 돌아가야할듯
        elif current_state == "Vehicle Detected State":
            if video_stream:
                ret, frame = video_stream.read()
                if ret:
                    # 여기에 번호판 인식 코드를 추가
                    pass

            # 차량이 옳다는 조건을 추가로 확인하는 코드를 삽입
            # 예: 번호판 인식 결과 확인
            #correct_car = True  # 임시 조건
            correct_car = False
            '''
            if video_stream:
                video_stream.release()
        '''


            while True:
                distance=get_distance()
                if distance <= 20:
                    # 차량이 옳다는 조건을 추가로 확인하는 코드를 삽입
                    # 예: 번호판 인식 결과 확인
                    if correct_car:
                        current_state = "Authorized State"   
                        break                      
                    else:
                        current_state = "Unauthorized State"
                        break

                else:
                    t.sleep(1)
                    distance=get_distance()
                    if distance >= 40:
                        current_state="Basic State"
                        break
            
        elif current_state == "Authorized State":
            control_led("all", "off")                       
            control_led("green", "on")                    
            play_melody(1)
            t.sleep(1)
            current_state = "Bollard Lowering State"
            
        
        elif current_state == "Unauthorized State":
            control_led("all", "off")
            control_led("red", "blink")
            control_led('red','on')

            while True:
                distance=get_distance()
                if distance < 20:
                    for i in range(3):
                        control_led('red','on')
                        play_buzzer()
                        control_led('red','off')
                        t.sleep(0.3)
                    control_led('red','on')
                    t.sleep(3)
                    start_time=None

                elif distance >= 40:
                    if start_time is None:
                        start_time = time.time()  
                    elif time.time() - start_time >= 10:
                        current_state = "Basic State"
                        break

        
        elif current_state == "Bollard Lowering State":
            control_led("all", "on")
            play_melody(2)
            move_servos(angle1=20,angle2=180) #내려가는
            current_state = "Parking Standby State"
            
        
        elif current_state == "Parking Standby State":
            control_led("all", "off")
            control_led("green", "blink")
            control_led("green", "on")
            while True:
                distance=get_distance()

                if distance < 10:
                    if start_time is None:
                        start_time = time.time()  # 안정적인 상태 시작 시간 기록
                    elif time.time() - start_time >= 10:
                        current_state = "Parking State"
                        break
                else:
                    start_time = None

        
        elif current_state == "Parking State":
            control_led("all", "off")
            start_time=None
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

            p_start_time=None
            start_time=None
            while True:
                
                distance=get_distance()
                if distance < 10:
                    start_time=None
                    if p_start_time is None:
                        p_start_time = time.time()  
                    elif time.time() - p_start_time >= 10:
                        current_state = "Parking State"
                        break
                else:
                    p_start_time=None
                    if start_time is None:
                        start_time = time.time() 
                    elif time.time() - start_time >= 10:                        
                        current_state = "Bollard Raising State"
                        break


        elif current_state == "Bollard Raising State":
            control_led("all", "on")
            play_melody(2)
            move_servos(angle1=180,angle2=20) #올라가는
            current_state = "Basic State"


if __name__ == "__main__":
    main()

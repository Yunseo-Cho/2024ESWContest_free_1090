import cv2
import numpy as np
import easyocr
import requests
import torch
import re

url = "http://192.168.0.29/capture"  # ESP32-CAM의 IP 주소

# OpenCV로 영상 스트리밍 받기
cap = cv2.VideoCapture(url)
reader = easyocr.Reader(['ko'], gpu=torch.cuda.is_available())

while True:
    img_resp = requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img = cv2.imdecode(img_arr, -1)

    # 실시간 화면을 imshow 창에 출력
    cv2.imshow("ESP32-CAM", img)

    # 그레이스케일 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 가우시안 블러 적용
    img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

    # 이미지 이진화
    img_thresh = cv2.adaptiveThreshold(
        img_blurred,
        maxValue=255.0,
        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        thresholdType=cv2.THRESH_BINARY_INV,
        blockSize=19,
        C=9
    )

    # 추출된 번호판 문자 인식
    plate_img = cv2.equalizeHist(img_thresh)
    _, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.5, fy=1.5)
    plate_img = cv2.GaussianBlur(plate_img, (3, 3), 0)

    # 번호판 문자 인식
    try:
        chars = reader.readtext(plate_img, detail=0)[0]
    except IndexError:
        chars = ""

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
    result_chars = pattern.findall(result_chars) # 정규식 패턴으로 필터링 할 경우 필요 없음

    # 결과 출력
    print(result_chars)

    # 번호판 이미지 출력
    cv2.imshow("Plate Image", plate_img)

    # 'q' 키를 눌러서 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

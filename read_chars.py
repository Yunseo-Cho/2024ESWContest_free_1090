# -*- coding: utf-8 -*-
'''
!pip install opencv-python-headless

!pip install easyocr

!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
'''
import torch

# GPU가 없는 경우 CPU로 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# 예제 텐서를 CPU에 할당
tensor = torch.tensor([1.0, 2.0, 3.0]).to(device)
print(tensor)

#print("CUDA available:", torch.cuda.is_available())

'''
# Commented out IPython magic to ensure Python compatibility.
%pip install ultralytics
%pip install pillow
'''

import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch
import easyocr
import re
import os

# 테스트 코드
from PIL import Image
from ultralytics import YOLO

# YOLOv8 모델 로드
model = YOLO(r'C:\Users\yunse\OneDrive\바탕 화면\하늘소\볼라드\best.pt')
'''
# 테스트용 이미지 경로
image_path = r'C:\Users\yunse\OneDrive\바탕 화면\하늘소\볼라드\사진\다운로드 (2).jpeg'

image = cv2.imread(image_path)
results = model(image) # 모델로 예측 수행
'''

image = cv2.imread(frame)
results = model(image) # 모델로 예측 수행

# 예측 결과에서 자동차 번호판 영역 추출 및 문자 인식
for result in results:
    boxes = result.boxes
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        license_plate = image[y1:y2, x1:x2]

#이미지 정보 추출
height, width, channel = license_plate.shape


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
#_, plate_img = cv2.threshold(plate_img, thresh=0.0, maxval=255.0, type=cv2.THRESH_BINARY | cv2.THRESH_OTSU)
#plate_img = cv2.resize(plate_img, dsize=(0, 0), fx=1.5, fy=1.5)
#plate_img = cv2.GaussianBlur(plate_img, (3, 3), 0)
plate_img = cv2.adaptiveThreshold(plate_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY, 11, 2)

reader = easyocr.Reader(['ko'], gpu=torch.cuda.is_available())
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
result_chars = pattern.findall(result_chars)
# 결과 출력
print(result_chars)

# 이미지 출력
#plt.subplot(len(plate_imgs), 1, i+1)
plt.imshow(plate_img, cmap='gray')
plt.show()

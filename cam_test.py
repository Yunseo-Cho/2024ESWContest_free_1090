import cv2

# 노트북의 기본 카메라를 엽니다
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 가져올 수 없습니다.")
        break

    # 프레임을 화면에 표시합니다
    cv2.imshow('Camera', frame)

    # 'q' 키를 누르면 루프를 종료합니다
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

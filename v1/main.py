import cv2
import time
from recognition import EasyOCRPlateRecognizer

def main():
    recognizer = EasyOCRPlateRecognizer(gpu=False)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        return

    frame_count = 0
    process_every = 5
    last_plate = None
    last_plate_conf = 0.0

    print("按 'q' 退出，按 's' 保存当前帧")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display_frame = frame.copy()
        frame_count += 1

        if frame_count % process_every == 0:
            small = cv2.resize(frame, (640, 480))
            plates = recognizer.recognize(small)
            if plates:
                last_plate, last_plate_conf = plates[0]
            else:
                last_plate = None

        if last_plate:
            cv2.putText(display_frame, f"Plate: {last_plate} ({last_plate_conf:.2f})",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        else:
            cv2.putText(display_frame, "No plate detected",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

        cv2.imshow("License Plate Recognition (v1)", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            cv2.imwrite(f"capture_{int(time.time())}.jpg", frame)
            print("截图保存")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
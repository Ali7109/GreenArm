from ultralytics import YOLO
import cv2

model = YOLO('yolov8m.pt') 

# Continous video capture from webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLOv8 inference
    results = model.predict(frame, stream=True, conf=0.2)

    # Draw boxes and labels
    for r in results:
        annotated_frame = r.plot()

    cv2.imshow("YOLOv8 Real-Time Detection", annotated_frame)

    # Quit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

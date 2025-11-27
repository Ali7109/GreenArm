# object_detection/test/test_video.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))

from prediction_helper import ObjectDetector
import cv2

if __name__ == "__main__":
    detector = ObjectDetector("model_v6_refined")

    cap = cv2.VideoCapture(0)  # or port 4 on Ubuntu

    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run detection on each frame
        results = detector.model.predict(frame, stream=True, conf=0.5, classes=None)

        annotated = frame
        for r in results:
            annotated = r.plot()

        cv2.imshow("Video Detection", annotated)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

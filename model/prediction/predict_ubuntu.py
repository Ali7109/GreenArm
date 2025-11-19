#!/usr/bin/env python3

from ultralytics import YOLO
import cv2

def main():
    # Load your model
    model = YOLO("ODv3.3.pt")

    # Try opening webcam using V4L2 backend (best for Ubuntu)
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("❌ Error: Could not access webcam on /dev/video0")
        return

    print("📸 Webcam opened. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Error: Failed to grab frame.")
            break

        # Run inference (stream=True gives generator results)
        results = model.predict(frame, stream=True, conf=0.2)

        annotated_frame = frame  # fallback

        # Draw bounding boxes + labels
        for r in results:
            annotated_frame = r.plot()

        # Display
        cv2.imshow("YOLOv8 Real-Time Detection", annotated_frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("👋 Exiting...")
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

# object_detection/test/test_photo.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))

from prediction_helper import ObjectDetector
import cv2

if __name__ == "__main__":
    detector = ObjectDetector("model_v6_refined")
    input_image_path = "static_image_sample.png"
    output_image_path = "detected_image_sample.jpg"

    annotated = detector.predict(input_image_path, output_path=output_image_path, conf=0.5)

    cv2.imshow("Detection", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

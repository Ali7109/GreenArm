# object_detection/test/test_photo.py
import sys
import os
from pathlib import Path

# Ensure scripts folder is in path
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from prediction_helper import ObjectDetector
import cv2

if __name__ == "__main__":
    # Resolve paths relative to THIS script
    current_dir = Path(__file__).parent
    input_image_path = current_dir / "static_image_sample.png"
    output_image_path = current_dir / "detected_image_sample.jpg"

    detector = ObjectDetector("model_v6_refined")
    annotated = detector.predict(str(input_image_path), output_path=str(output_image_path), conf=0.5)

    cv2.imshow("Detection", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

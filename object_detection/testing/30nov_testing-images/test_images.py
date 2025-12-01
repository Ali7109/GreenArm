import sys
import os
from pathlib import Path
# import cv2

# Ensure scripts folder is in path
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts"))
from prediction_helper import ObjectDetector

if __name__ == "__main__":
    # Resolve paths relative to THIS script
    current_dir = Path(__file__).parent
    # model_name = "model_v6_refined"
    # model_name = "model_v7_refined"
    # model_name = "model_v8"
    model_name = "model_v9"
    detector = ObjectDetector(model_name)

    folders = ["by_contrast", "by_hue", "by_saturation", "tp_only"]

    for folder in folders:
        input_dir = Path(folder)
        output_dir = Path(f"{model_name}_predictions-{folder}")
        os.makedirs(output_dir, exist_ok=True)
        for _, _, files in os.walk(folder):
            for file in files:
                input_image_path = input_dir / file
                output_image_path = output_dir / f"prediction_{file}"
                print(output_image_path)
                detector.predict(str(input_image_path), output_path=str(output_image_path), conf=0.5)

    # annotated = detector.predict(str(input_image_path), output_path=str(output_image_path), conf=0.5)

    # cv2.imshow("Detection", annotated)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

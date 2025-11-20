# object_detect_predict.py

from ultralytics import YOLO
import cv2
import os


class ObjectDetector:
    def __init__(self, model_name):
        """
        Loads a YOLO model located at ./models/<model_name>.pt
        Resolves the path relative to this file.
        """
        self.model_path = self._resolve_model_path(model_name)

        if not os.path.isfile(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        self.model = YOLO(self.model_path)

    @staticmethod
    def _resolve_model_path(model_name):
        # Resolve relative to the file this class is in
        script_dir = os.path.dirname(os.path.realpath(__file__))  # realpath ensures no symlink issues
        model_path = os.path.join(script_dir, "..", "models", f"{model_name}.pt")
        return os.path.abspath(model_path)  # absolute path

    def predict(self, image_path, output_path=None, conf=0.5, classes=None):
        """
        Runs YOLO detection on a single image.
        Returns the annotated frame.

        Parameters:
            image_path  - input image path
            output_path - where to save the annotated output
            conf        - confidence threshold
            classes     - restrict classes (e.g., [0, 2])

        Prints all detections (cls + confidence).
        """

        # Load image
        frame = cv2.imread(image_path)
        if frame is None:
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Predict
        results = self.model.predict(frame, conf=conf, classes=classes)

        # Collect detections
        detections = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf_val = float(box.conf[0])
                detections.append((cls, conf_val))

        # Log results
        if detections:
            print(f"Detections in '{image_path}':")
            for cls, conf_val in detections:
                print(f" - Class {cls}, confidence {conf_val:.3f}")
        else:
            print(f"No detections in '{image_path}'")

        # Annotate
        annotated = results[0].plot()

        # Save output
        if output_path:
            cv2.imwrite(output_path, annotated)

        return annotated
    
if __name__ == "__main__":
    model_name = "model_v6_refined"
    image_path = "input.jpg"
    output_path = "output.jpg"

    detector = ObjectDetector(model_name)
    annotated = detector.predict(image_path, output_path)

    cv2.imshow("Detection", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
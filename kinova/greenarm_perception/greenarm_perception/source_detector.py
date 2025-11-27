import cv2
import numpy as np
import rclpy
import os
from rclpy.node import Node
from kinova_gen3_interfaces.msg import SourceTarget

# Add YOLO import
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path):
        """
        Loads a YOLO model from the specified path with robust path handling.
        """
        # Resolve the model path - try multiple approaches
        resolved_path = self._resolve_model_path(model_path)
        
        #if not os.path.isfile(resolved_path):
            # Try with .pt extension if not already there
            
        #    if not resolved_path.endswith('.pt'):
        #        resolved_path_with_ext = resolved_path + '.pt'
        #        if os.path.isfile(resolved_path_with_ext):
        #
        #        else:
        #            # Try to find the file in common locations
        #            resolved_path = self._find_model_file(model_path)
        
        #if not os.path.isfile(resolved_path):
        #    raise FileNotFoundError(f"Model not found. Tried: {resolved_path}")
        
        self.model = YOLO(resolved_path)
        print(f"Loaded YOLO model from: {resolved_path}")

    def _resolve_model_path(self, model_path):
        """Resolve model path with multiple fallback strategies"""
        
        # If it's already an absolute path and exists, use it
        if os.path.isabs(model_path) and os.path.isfile(model_path):
            return model_path
        
        # If it's already an absolute path with .pt and exists, use it
        if os.path.isabs(model_path + '.pt') and os.path.isfile(model_path + '.pt'):
            return model_path + '.pt'
        
        # Strategy 1: Relative to current working directory
        cwd_path = os.path.join(os.getcwd(), model_path)
        if os.path.isfile(cwd_path):
            return cwd_path
        
        cwd_path_pt = os.path.join(os.getcwd(), model_path + '.pt')
        if os.path.isfile(cwd_path_pt):
            return cwd_path_pt
        
        # Strategy 2: Relative to this source file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, model_path)
        if os.path.isfile(script_path):
            return script_path
        
        script_path_pt = os.path.join(script_dir, model_path + '.pt')
        if os.path.isfile(script_path_pt):
            return script_path_pt
        
        # Strategy 3: Just return the original and let it fail with clear error
        return model_path

    def _find_model_file(self, model_name):
        """Try to find the model file in common locations"""
        search_locations = [
            # Current directory
            model_name,
            model_name + '.pt',
            # Same directory as this file
            os.path.join(os.path.dirname(__file__), model_name),
            os.path.join(os.path.dirname(__file__), model_name + '.pt'),
            # Common model directories
            os.path.join(os.getcwd(), 'models', model_name),
            os.path.join(os.getcwd(), 'models', model_name + '.pt'),
            os.path.join(os.path.dirname(__file__), 'models', model_name),
            os.path.join(os.path.dirname(__file__), 'models', model_name + '.pt'),
        ]
        
        for location in search_locations:
            if os.path.isfile(location):
                return location
        
        return model_name  # Return original if not found

    def predict_frame(self, frame, conf=0.5, classes=None):
        """
        Runs YOLO detection on a frame.
        Returns list of (class_id, confidence, bbox_center_x, bbox_center_y)
        """
        results = self.model.predict(frame, conf=conf, classes=classes, verbose=False)
        
        detections = []
        for r in results:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf_val = float(box.conf[0])
                # Get bounding box center
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                center_x = (x1 + x2) / 2
                center_y = (y1 + y2) / 2
                detections.append((cls, conf_val, center_x, center_y))
        
        return detections


class SourceDetector(Node):
    """Publishes Kinova-ready pick targets based on ArUco + YOLO object detection."""

    def __init__(self):
        super().__init__("source_detector")

        # --- Parameters ---
        self.declare_parameter("video_device", "")
        self.declare_parameter("camera_index", 4)  # 0 for my mac and /dev/video4 for lab
        self.declare_parameter("pickup_height", 0.005)  # meters
        self.declare_parameter("min_confidence", 0.5)  # YOLO confidence threshold
        self.declare_parameter("publish_rate", 10.0)  # Hz
        self.declare_parameter("calibration_file", "workspace_calibration.npy")
        self.declare_parameter("force_recalibration", False)
        self.declare_parameter("model_path", "/home/ali745/Downloads/GreenArm/kinova/greenarm_perception/models/model_v6_refined.pt")  # YOLO model path

        # Marker layout / mapping (matches test_aruco.py defaults)
        self.workspace_marker_order = [0, 1, 2, 3]
        self.marker_inner_corner = {
            0: 3,
            1: 0,
            2: 2,
            3: 1,
        }
        self.workspace_pts = np.float32([
            [0.2, 0],
            [0.5, 0],
            [0.2, -0.3],
            [0.5, -0.3],
        ])
        self.kinova_min_x = 0.2
        self.kinova_max_x = 0.5
        self.kinova_min_y = -0.3
        self.kinova_max_y = 0
        self.workspace_side_m = 0.25

        video_device = self.get_parameter("video_device").get_parameter_value().string_value
        camera_index = self.get_parameter("camera_index").get_parameter_value().integer_value
        self.capture = cv2.VideoCapture(video_device if video_device else camera_index)
        if not self.capture.isOpened():
            raise RuntimeError("Cannot open camera for source_detector node")

        self.min_confidence = float(self.get_parameter("min_confidence").value)
        self.pickup_height = float(self.get_parameter("pickup_height").value)
        publish_rate = float(self.get_parameter("publish_rate").value)
        calibration_file = self.get_parameter("calibration_file").get_parameter_value().string_value
        force_recalibration = self.get_parameter("force_recalibration").get_parameter_value().bool_value
        model_path_param = self.get_parameter("model_path").get_parameter_value().string_value

        self.publisher = self.create_publisher(SourceTarget, "/source_zone/pick_target", 10)
        self.timer = self.create_timer(1.0 / publish_rate, self._process_frame)

        # Initialize YOLO detector with robust path handling
        try:
            # Get the directory where this source file is located
            current_file_dir = os.path.dirname(os.path.abspath(__file__))
            # Construct the full path to the model
            model_full_path = os.path.join(current_file_dir, model_path_param)
            
            self.detector = ObjectDetector(model_full_path)
            self.get_logger().info("YOLO detector initialized successfully")
        except Exception as e:
            self.get_logger().error(f"Failed to initialize YOLO detector with full path: {e}")
            # Fallback: try with the parameter value as-is
            try:
                self.get_logger().info("Trying fallback model path...")
                self.detector = ObjectDetector(model_path_param)
                self.get_logger().info("YOLO detector initialized with fallback path")
            except Exception as e2:
                self.get_logger().error(f"Fallback also failed: {e2}")
                raise

        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.aruco_detector = cv2.aruco.ArucoDetector(self.aruco_dict)
        self.marker_length_m = 0.05

        self.camera_matrix = np.array(
            [[1.62926289e3, 0.0, 9.71234776e2],
             [0.0, 1.62748788e3, 5.30839748e2],
             [0.0, 0.0, 1.0]],
            dtype=np.float32)
        self.dist_coeffs = np.array(
            [0.595836256, -7.01481761, -0.00206565224, 0.0000525532496, 24.2404007],
            dtype=np.float32)

        # Load or create calibration
        self.workspace_transform = self._load_calibration(calibration_file, force_recalibration)
        self.calibration_completed = self.workspace_transform is not None

    def _load_calibration(self, calibration_file, force_recalibration):
        """Load existing calibration or prepare for new one"""
        if not force_recalibration and os.path.exists(calibration_file):
            try:
                transform = np.load(calibration_file)
                self.get_logger().info(f"Loaded calibration from {calibration_file}")
                return transform
            except Exception as e:
                self.get_logger().warn(f"Failed to load calibration: {e}")
                
        self.get_logger().info("No calibration found or forced recalibration. Waiting for markers...")
        return None
        
    def _save_calibration(self, transform, calibration_file):
        """Save calibration to file"""
        try:
            np.save(calibration_file, transform)
            self.get_logger().info(f"Calibration saved to {calibration_file}")
            return True
        except Exception as e:
            self.get_logger().error(f"Failed to save calibration: {e}")
            return False

    # --- Geometry helpers -------------------------------------------------
    def estimate_marker_pixel_size(self, corner_quad):
        p = corner_quad.astype(np.float32)
        return (
            np.linalg.norm(p[1] - p[0]) +
            np.linalg.norm(p[2] - p[1]) +
            np.linalg.norm(p[3] - p[2]) +
            np.linalg.norm(p[0] - p[3])
        ) / 4.0

    def build_workspace_transform(self, marker_corners, marker_ids):
        if marker_ids is None:
            return None
        
        # Check if we have all required markers
        flat_ids = marker_ids.flatten()
        if not all(marker_id in flat_ids for marker_id in self.workspace_marker_order):
            return None
        
        ordered_points = []
        for expected_id in self.workspace_marker_order:
            idx = np.where(flat_ids == expected_id)[0][0]
            ordered_points.append(
                marker_corners[idx][0][self.marker_inner_corner[expected_id]]
            )
        
        transform = cv2.getPerspectiveTransform(
            np.float32(ordered_points),
            self.workspace_pts,
        )
        
        # Validate transform by checking if it produces reasonable coordinates
        test_points = np.float32([[[0, 0]], [[100, 100]]])
        transformed = cv2.perspectiveTransform(test_points, transform)
        if np.any(np.isnan(transformed)) or np.any(np.isinf(transformed)):
            return None
            
        return transform

    def workspace_to_source_zone(self, wx, wy):
        x = np.clip(wx / self.workspace_side_m, 0.0, 1.0)
        y = np.clip(wy / self.workspace_side_m, 0.0, 1.0)
        sx = self.kinova_min_x + x * (self.kinova_max_x - self.kinova_min_x)
        sy = self.kinova_min_y + y * (self.kinova_max_y - self.kinova_min_y)
        return sx, sy

    def _process_frame(self):
        ret, frame = self.capture.read()

        if not ret:
            self.get_logger().warning("Camera frame grab failed")
            self.publish_empty()
            return

        # ---- ArUco detection ----
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        #corners, ids, _ = cv2.aruco.detectMarkers(
        #    gray, self.aruco_dict, parameters=self.detector_params)
        corners, ids, _ = self.aruco_detector.detectMarkers(gray)
        workspace_transform = None
        
        # If we have a saved calibration, use it
        if self.workspace_transform is not None:
            workspace_transform = self.workspace_transform
            self.get_logger().debug("Using cached calibration")
        # Otherwise, try to create new calibration
        elif ids is not None and len(ids) >= 4:
            workspace_transform = self.build_workspace_transform(corners, ids)
            if workspace_transform is not None:
                calibration_file = self.get_parameter("calibration_file").get_parameter_value().string_value
                if self._save_calibration(workspace_transform, calibration_file):
                    self.workspace_transform = workspace_transform  # Cache it
                    self.calibration_completed = True
                    self.get_logger().info("Calibration completed and saved!")
        else:
            if not self.calibration_completed:
                self.get_logger().warn("Need 4 markers for initial calibration")
            self.publish_empty()
            return

        if workspace_transform is None:
            if not self.calibration_completed:
                self.get_logger().warn("No workspace transform available - need calibration")
            else:
                self.get_logger().warn("Workspace transform failed")
            self.publish_empty()
            return

        # ---- YOLO Object Detection ----
        # Only detect classes 0 (recycling) and 2 (compost), ignore class 1
        detections = self.detector.predict_frame(frame, conf=self.min_confidence, classes=[0, 2])
        
        if not detections:
            self.get_logger().debug("No objects detected above confidence threshold")
            self.publish_empty()
            return

        # Use the highest confidence detection
        best_detection = max(detections, key=lambda x: x[1])  # Sort by confidence
        class_id, confidence, center_x, center_y = best_detection
        
        self.get_logger().info(
            f"Detected object - Class: {class_id}, Confidence: {confidence:.3f}, "
            f"Position: ({center_x:.1f}, {center_y:.1f})"
        )

        # ---- Transform to workspace coordinates ----
        workspace_pt = cv2.perspectiveTransform(
            np.array([[[center_x, center_y]]], dtype=np.float32),
            workspace_transform
        )[0][0]

        wx, wy = workspace_pt

        # Use direct mapping
        kinova_x, kinova_y = wx, wy

        # Validate coordinates are within reasonable bounds
        if not (self.kinova_min_x <= kinova_x <= self.kinova_max_x and 
                self.kinova_min_y <= kinova_y <= self.kinova_max_y):
            self.get_logger().warn(f"Target outside workspace: ({kinova_x:.3f}, {kinova_y:.3f})")
            self.publish_empty()
            return

        # ---- Publish ----
        msg = SourceTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.x = float(kinova_x)
        msg.y = float(kinova_y)
        msg.z = float(self.pickup_height)
        msg.confidence = float(confidence)
        
        # Set label based on class ID
        if class_id == 0:
            msg.label = "recycle"
        elif class_id == 2:
            msg.label = "compost"
        else:
            msg.label = "unknown"  # Shouldn't happen since we filter classes

        self.get_logger().info(
            f"Publishing target: ({msg.x:.3f}, {msg.y:.3f}) -> {msg.label} "
            f"(confidence: {msg.confidence:.2f})"
        )
        
        self.publisher.publish(msg)

    def publish_empty(self):
        msg = SourceTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.confidence = 0.0
        msg.x = msg.y = msg.z = 0.0
        msg.label = ""
        self.publisher.publish(msg)

    def destroy_node(self):
        if self.capture is not None:
            self.capture.release()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SourceDetector()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

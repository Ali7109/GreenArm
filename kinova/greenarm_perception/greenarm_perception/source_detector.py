import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from kinova_gen3_interfaces.msg import SourceTarget


class SourceDetector(Node):
    """Publishes Kinova-ready pick targets based on ArUco + color segmentation."""

    def __init__(self):
        super().__init__("source_detector")

        # --- Parameters ---
        self.declare_parameter("video_device", "")
        self.declare_parameter("camera_index", 4)  # 0 for my mac and /dev/video4 for lab
        self.declare_parameter("pickup_height", 0.0)  # meters
        self.declare_parameter("min_red_area_px", 500)
        self.declare_parameter("publish_rate", 10.0)  # Hz

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

        self.min_red_area_px = int(self.get_parameter("min_red_area_px").value)
        self.pickup_height = float(self.get_parameter("pickup_height").value)
        publish_rate = float(self.get_parameter("publish_rate").value)

        self.publisher = self.create_publisher(SourceTarget, "/source_zone/pick_target", 10)
        self.timer = self.create_timer(1.0 / publish_rate, self._process_frame)

        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.detector_params = cv2.aruco.DetectorParameters_create()
        self.marker_length_m = 0.05

        self.camera_matrix = np.array(
            [[1.62926289e3, 0.0, 9.71234776e2],
             [0.0, 1.62748788e3, 5.30839748e2],
             [0.0, 0.0, 1.0]],
            dtype=np.float32)
        self.dist_coeffs = np.array(
            [0.595836256, -7.01481761, -0.00206565224, 0.0000525532496, 24.2404007],
            dtype=np.float32)

        # Add state tracking
        self.last_valid_transform = None
        self.transform_timeout = 5.0  # seconds
        self.last_transform_time = self.get_clock().now()

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
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.detector_params)

        workspace_transform = None
        if ids is not None and len(ids) >= 4:  # Need all 4 markers
            workspace_transform = self.build_workspace_transform(corners, ids)
            if workspace_transform is not None:
                self.last_valid_transform = workspace_transform
                self.last_transform_time = self.get_clock().now()
        else:
            # Use last valid transform if recent enough
            current_time = self.get_clock().now()
            time_since_valid = (current_time - self.last_transform_time).nanoseconds / 1e9
            if time_since_valid < self.transform_timeout and self.last_valid_transform is not None:
                workspace_transform = self.last_valid_transform
                self.get_logger().debug("Using cached transform")

        if workspace_transform is None:
            self.get_logger().warn("No workspace transform available")
            self.publish_empty()
            return

        # ---- Compute pixels-per-meter ----
        px_per_meter = None
        if ids is not None and len(ids) > 0:
            mpx = self.estimate_marker_pixel_size(corners[0][0])
            if mpx > 0:
                m_per_px = self.marker_length_m / mpx
                px_per_meter = 1.0 / m_per_px

        # ---- Red detection ----
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Combine both red ranges (0-10 and 170-180)
        mask1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        mask = cv2.bitwise_or(mask1, mask2)

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_cnt = None
        best_area = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > best_area and area >= self.min_red_area_px:
                best_area = area
                best_cnt = cnt

        if best_cnt is None:
            self.get_logger().debug("No red object found above area threshold")
            self.publish_empty()
            return

        # ---- ROI + transform ----
        x, y, w, h = cv2.boundingRect(best_cnt)
        cx, cy = x + w // 2, y + h // 2

        workspace_pt = cv2.perspectiveTransform(
            np.array([[[cx, cy]]], dtype=np.float32),
            workspace_transform
        )[0][0]

        wx, wy = workspace_pt

        # Use direct mapping instead of workspace_to_source_zone if that's what you want
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
        
        # Calculate confidence based on area and transform quality
        confidence = 1.0
        if px_per_meter is not None:
            normalized_area = best_area / (px_per_meter ** 2)
            confidence = min(1.0, normalized_area / 0.01)  # Normalize to ~10cm²
            
        msg.confidence = confidence
        msg.label = "red_object"

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

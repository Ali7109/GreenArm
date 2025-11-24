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
        self.declare_parameter("camera_index", 0) #0 for my mac and /dev/video4 for lab
        self.declare_parameter("pickup_height", 0.01)  # meters
        self.declare_parameter("min_red_area_px", 500)

        # Marker layout / mapping (matches test_aruco.py defaults)
        self.workspace_marker_order = [0, 1, 2, 3]
        self.marker_inner_corner = {
            0: 3,
            1: 0,
            2: 2,
            3: 1,
        }
        self.workspace_pts = np.float32([
            [0.3, 0.2],
            [0.0, 0.2],
            [0.3, 0.5],
            [0.0, 0.5],
        ])
        self.kinova_min_x = 0.0
        self.kinova_max_x = 0.3
        self.kinova_min_y = 0.2
        self.kinova_max_y = 0.5
        self.workspace_side_m = 0.25

        video_device = self.get_parameter("video_device").get_parameter_value().string_value
        camera_index = self.get_parameter("camera_index").get_parameter_value().integer_value
        self.capture = cv2.VideoCapture(video_device if video_device else camera_index)
        if not self.capture.isOpened():
            raise RuntimeError("Cannot open camera for source_detector node")

        self.min_red_area_px = int(self.get_parameter("min_red_area_px").value)
        self.pickup_height = float(self.get_parameter("pickup_height").value)

        self.publisher = self.create_publisher(SourceTarget, "/source_zone/pick_target", 10)
        self.timer = self.create_timer(0.1, self._process_frame)

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
        ordered_points = []
        flat = marker_ids.flatten()
        for expected_id in self.workspace_marker_order:
            matches = np.where(flat == expected_id)[0]
            if matches.size == 0:
                return None
            idx = matches[0]
            ordered_points.append(
                marker_corners[idx][0][self.marker_inner_corner[expected_id]]
            )
        return cv2.getPerspectiveTransform(
            np.float32(ordered_points),
            self.workspace_pts,
        )

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.detector_params)

        workspace_transform = self.build_workspace_transform(corners, ids) if ids is not None else None

        px_per_meter = None
        if ids is not None and len(ids) > 0:
            mpx = self.estimate_marker_pixel_size(corners[0][0])
            m_per_px = self.marker_length_m / mpx
            px_per_meter = 1.0 / m_per_px

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        mask |= cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
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

        if best_cnt is None or workspace_transform is None:
            self.publish_empty()
            return

        x, y, w, h = cv2.boundingRect(best_cnt)
        cx, cy = x + w // 2, y + h // 2

        workspace_pt = cv2.perspectiveTransform(
            np.array([[[cx, cy]]], dtype=np.float32),
            workspace_transform
        )[0][0]
        wx, wy = workspace_pt
        kinova_x, kinova_y = self.workspace_to_source_zone(wx, wy)

        msg = SourceTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.x = float(kinova_x)
        msg.y = float(kinova_y)
        msg.z = float(self.pickup_height)
        msg.confidence = float(min(1.0, best_area / (px_per_meter**2) if px_per_meter else 1.0))
        msg.label = "unknown"

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

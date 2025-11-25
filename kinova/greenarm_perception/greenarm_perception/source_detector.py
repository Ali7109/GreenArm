#!/usr/bin/env python3
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from kinova_gen3_interfaces.msg import SourceTarget

class SourceDetector(Node):
    """Publishes Kinova-ready pick targets based on ArUco + color segmentation.

    Behavior (one-shot origin calibration):
      - The first valid detected block is treated as the workspace origin (0,0).
      - All subsequent published positions are transformed to local coordinates:
            local_x = raw_x - origin_x
            local_y = raw_y - origin_y
      - Arm and aruco markers are assumed static. The block is what you place (center for calibration).
    """

    def __init__(self):
        super().__init__("source_detector")

        # --- Parameters ---
        self.declare_parameter("video_device", "")
        self.declare_parameter("camera_index", 4)  # 0 for local mac, /dev/video4 in lab
        self.declare_parameter("pickup_height", 0.01)  # meters
        self.declare_parameter("min_red_area_px", 500)

        # Marker layout / mapping (matches test_aruco.py defaults)
        self.workspace_marker_order = [0, 1, 2, 3]
        self.marker_inner_corner = {0: 3, 1: 0, 2: 2, 3: 1}
        self.workspace_pts = np.float32([
            [0.3, 0.2],
            [0.0, 0.2],
            [0.3, 0.5],
            [0.0, 0.5],
        ])
        # Kinova mapping bounds (these are still used as target mapping range)
        self.kinova_min_x = 0.0
        self.kinova_max_x = 0.3
        self.kinova_min_y = 0.2
        self.kinova_max_y = 0.5
        self.workspace_side_m = 0.25
        self.marker_length_m = 0.05

        # Origin calibration state (one-shot)
        self.origin_calibrated = False
        self.origin_x = 0.0
        self.origin_y = 0.0

        # Read params
        video_device = self.get_parameter("video_device").get_parameter_value().string_value
        camera_index = self.get_parameter("camera_index").get_parameter_value().integer_value
        self.min_red_area_px = int(self.get_parameter("min_red_area_px").value)
        self.pickup_height = float(self.get_parameter("pickup_height").value)

        # Video capture
        self.capture = cv2.VideoCapture(video_device if video_device else camera_index)
        if not self.capture.isOpened():
            raise RuntimeError("Cannot open camera for source_detector node")

        # ROS publisher & timer
        self.publisher = self.create_publisher(SourceTarget, "/source_zone/pick_target", 10)
        self.timer = self.create_timer(0.1, self._process_frame)

        # ArUco
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        self.detector_params = cv2.aruco.DetectorParameters_create()

        # Camera intrinsics/distortion (optional, used for px-per-meter estimate)
        self.camera_matrix = np.array(
            [[1.62926289e3, 0.0, 9.71234776e2],
             [0.0, 1.62748788e3, 5.30839748e2],
             [0.0, 0.0, 1.0]],
            dtype=np.float32)
        self.dist_coeffs = np.array(
            [0.595836256, -7.01481761, -0.00206565224, 0.0000525532496, 24.2404007],
            dtype=np.float32)

        self.get_logger().info("SourceDetector initialized (waiting for first calibration block).")

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

    def order_corners_by_position(self, pts):
        # pts = list of (x, y) points
        pts = np.array(pts)

        # sort by Y
        y_sorted = pts[np.argsort(pts[:, 1])]

        top = y_sorted[:2]
        bottom = y_sorted[2:]

        # sort top by X → TL, TR
        top_left, top_right = top[np.argsort(top[:, 0])]

        # sort bottom by X → BL, BR
        bottom_left, bottom_right = bottom[np.argsort(bottom[:, 0])]

        return top_left, top_right, bottom_right, bottom_left

    def workspace_to_source_zone(self, wx, wy):
        """Map workspace coordinates (meters) into kinova working rectangle.

        Note: this function returns the raw kinova coordinates (not local-offset).
        The origin calibration (local offset) is applied later in _process_frame.
        """
        x = np.clip(wx / self.workspace_side_m, 0.0, 1.0)
        y = np.clip(wy / self.workspace_side_m, 0.0, 1.0)
        sx = self.kinova_min_x + x * (self.kinova_max_x - self.kinova_min_x)
        sy = self.kinova_min_y + y * (self.kinova_max_y - self.kinova_min_y)
        return sx, sy

    def _process_frame(self):
        # Grab frame
        ret, frame = self.capture.read()
        if not ret:
            self.get_logger().warning("Camera frame grab failed")
            self.publish_empty()
            return

        # ArUco detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = cv2.aruco.detectMarkers(
            gray, self.aruco_dict, parameters=self.detector_params
        )

        if ids is None or len(ids) < 4:
            self.get_logger().info("Not enough markers detected")
            self.publish_empty()
            return

        flat_ids = ids.flatten().tolist()
        self.get_logger().info(f"Detected markers: {flat_ids}")

        # --- ORDER MARKER CENTERS BY SPATIAL POSITION ---
        centers = [np.mean(c[0], axis=0) for c in corners]
        top_left, top_right, bottom_right, bottom_left = self.order_corners_by_position(centers)
        self.get_logger().info(
            f"Ordered corners -> TL={top_left}, TR={top_right}, BR={bottom_right}, BL={bottom_left}"
        )

        # Build workspace transform using the spatially ordered points
        ordered_corners = [top_left, top_right, bottom_right, bottom_left]
        workspace_transform = cv2.getPerspectiveTransform(np.float32(ordered_corners), self.workspace_pts)

        # ---- Compute pixels-per-meter (approx) ----
        try:
            mpx = self.estimate_marker_pixel_size(corners[0][0])
            if mpx > 0:
                m_per_px = self.marker_length_m / mpx
                px_per_meter = 1.0 / m_per_px
                self.get_logger().debug(f"px_per_meter = {px_per_meter:.1f}")
            else:
                self.get_logger().warning("Marker pixel size computed as zero")
                px_per_meter = None
        except Exception as e:
            self.get_logger().warning(f"Failed to estimate marker pixel size: {e}")
            px_per_meter = None

        # ---- Red detection ----
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        low1, high1 = np.array([0, 120, 70]), np.array([10, 255, 255])
        low2, high2 = np.array([170, 120, 70]), np.array([180, 255, 255])
        mask = cv2.bitwise_or(cv2.inRange(hsv, low1, high1), cv2.inRange(hsv, low2, high2))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        best_cnt, best_area = None, 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > best_area and area >= self.min_red_area_px:
                best_cnt, best_area = cnt, area

        if best_cnt is None:
            self.get_logger().info("No red object found above area threshold")
            self.publish_empty()
            return

        # Centroid
        x, y, w, h = cv2.boundingRect(best_cnt)
        cx, cy = x + w // 2, y + h // 2
        self.get_logger().debug(f"Red centroid pixel coords: ({cx}, {cy}) area={best_area}")

        # Map to workspace
        workspace_pt = cv2.perspectiveTransform(np.array([[[cx, cy]]], dtype=np.float32), workspace_transform)[0][0]
        wx, wy = workspace_pt[0], workspace_pt[1]
        self.get_logger().debug(f"Workspace XY (m): ({wx:.4f}, {wy:.4f})")

        # Map to Kinova coordinates
        kinova_x, kinova_y = self.workspace_to_source_zone(wx, wy)
        self.get_logger().info(f"Mapped Kinova XY (raw): ({kinova_x:.3f}, {kinova_y:.3f})")

        # --- ONE-SHOT ORIGIN CALIBRATION ---
        if not self.origin_calibrated:
            self.origin_x, self.origin_y = kinova_x, kinova_y
            self.origin_calibrated = True
            self.get_logger().info(f"Calibrated origin at ({self.origin_x:.3f}, {self.origin_y:.3f})")

        # Local coordinates relative to origin
        local_x, local_y = kinova_x - self.origin_x, kinova_y - self.origin_y
        self.get_logger().info(f"Local (workspace-agnostic) XY: ({local_x:.3f}, {local_y:.3f})")

        # ---- Publish SourceTarget message ----
        msg = SourceTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.x, msg.y, msg.z = float(local_x), float(local_y), self.pickup_height
        msg.confidence = float(min(1.0, best_area / (px_per_meter ** 2))) if px_per_meter else 1.0
        msg.label = "unknown"
        self.get_logger().info(f"Publishing target (local coords): {msg}")
        self.publisher.publish(msg)

    def publish_empty(self):
        msg = SourceTarget()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.confidence = 0.0
        msg.x = msg.y = msg.z = 0.0
        msg.label = ""
        self.publisher.publish(msg)

    def destroy_node(self):
        # Clean up camera
        try:
            if self.capture is not None:
                self.capture.release()
        except Exception:
            pass
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

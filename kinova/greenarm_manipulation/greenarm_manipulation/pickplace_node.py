import random
import time
from collections import deque

import rclpy
from rclpy.node import Node

from kinova_gen3_interfaces.msg import SourceTarget
from kinova_gen3_interfaces.srv import SetGripper, SetTool, Status

# Fixed drop rectangles (meters) in Kinova base frame - using consistent values
DROP_ZONES = {
    "recycle": {"x_min": 0.35, "x_max": 0.45, "y_min": 0.05, "y_max": 0.15, "z": 0.02},
    "compost": {"x_min": 0.35, "x_max": 0.45, "y_min": 0.35, "y_max": 0.45, "z": 0.02},
}
DEFAULT_DROP = "recycle"


class PickPlaceNode(Node):
    def __init__(self):
        super().__init__("greenarm_pickplace")

        self.declare_parameter("confidence_threshold", 0.2)
        self.declare_parameter("queue_size", 5)
        self.declare_parameter("pickup_hover_z", 0.12)
        self.declare_parameter("drop_hover_z", 0.15)
        self.declare_parameter("default_pick_depth", 0.01)
        self.declare_parameter("grip_closed", 1.0)
        self.declare_parameter("grip_open", 0.0)
        self.declare_parameter("stability_samples", 5)
        self.declare_parameter("gripper_timeout", 5.0)
        self.declare_parameter("gripper_close_delay", 1.0)  # seconds to wait for gripper to close
        self.declare_parameter("gripper_open_delay", 1.0)   # seconds to wait for gripper to open

        self.confidence_threshold = float(self.get_parameter("confidence_threshold").value)
        self.queue_size = int(self.get_parameter("queue_size").value)
        self.pick_hover_z = float(self.get_parameter("pickup_hover_z").value)
        self.drop_hover_z = float(self.get_parameter("drop_hover_z").value)
        self.default_pick_depth = float(self.get_parameter("default_pick_depth").value)
        self.grip_closed = float(self.get_parameter("grip_closed").value)
        self.grip_open = float(self.get_parameter("grip_open").value)
        self.stability_samples = int(self.get_parameter("stability_samples").value)
        self.gripper_timeout = float(self.get_parameter("gripper_timeout").value)
        self.gripper_close_delay = float(self.get_parameter("gripper_close_delay").value)
        self.gripper_open_delay = float(self.get_parameter("gripper_open_delay").value)
        self.tool_rotation = (180.0, 0.0, 180.0)

        self.target_queue = deque(maxlen=max(1, self.queue_size))
        self.active_target = None
        self.drop_pose = None
        self.pending_action = None
        self.state = "idle"
        self.allow_detection = True  # Control when to accept new detections
        
        # Improved stability buffer
        self.buffer_queue = deque(maxlen=self.stability_samples)
        self.last_target_time = self.get_clock().now()
        self.target_timeout = 2.0  # seconds

        # Timer for gripper delays
        self.gripper_timer = None
        self.gripper_target_state = None

        self.set_tool_client = self.create_client(SetTool, "/set_tool")
        self.set_gripper_client = self.create_client(SetGripper, "/set_gripper")
        self.home_client = self.create_client(Status, "/home")

        for name, client in (("set_tool", self.set_tool_client),
                             ("set_gripper", self.set_gripper_client),
                             ("home", self.home_client)):
            while not client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f"Waiting for {name} service...")

        # Home once at startup
        self.get_logger().info("Homing robot before starting pick/place loop")
        self._blocking_home()

        # Initialize gripper to open position at startup
        self.get_logger().info("Initializing gripper to open position")
        self._blocking_set_gripper(self.grip_open)

        self.target_sub = self.create_subscription(
            SourceTarget, "/source_zone/pick_target", self._target_callback, 10
        )
        self.timer = self.create_timer(0.1, self._control_loop)

    def _target_callback(self, msg):
        # Only accept targets when robot is idle and detection is allowed
        if not self.allow_detection or self.state != "idle":
            return

        # Ignore low confidence immediately
        if msg.confidence < self.confidence_threshold:
            return

        current_time = self.get_clock().now()
        new_point = (msg.x, msg.y, msg.z, current_time)

        # Clear buffer if too much time has passed
        if self.buffer_queue:
            time_since_last = (current_time - self.last_target_time).nanoseconds / 1e9
            if time_since_last > self.target_timeout:
                self.buffer_queue.clear()

        self.buffer_queue.append(new_point)
        self.last_target_time = current_time

        # Check if we have enough stable samples
        if len(self.buffer_queue) >= self.stability_samples:
            # Calculate position stability
            xs = [p[0] for p in self.buffer_queue]
            ys = [p[1] for p in self.buffer_queue]
            
            avg_x = sum(xs) / len(xs)
            avg_y = sum(ys) / len(ys)
            
            # Check if positions are stable
            max_deviation_x = max(abs(x - avg_x) for x in xs)
            max_deviation_y = max(abs(y - avg_y) for y in ys)
            
            STABILITY_THRESHOLD = 0.01  # 1 cm
            
            if max_deviation_x <= STABILITY_THRESHOLD and max_deviation_y <= STABILITY_THRESHOLD:
                # Create confirmed target
                confirmed = SourceTarget()
                confirmed.x = avg_x
                confirmed.y = avg_y
                confirmed.z = msg.z
                confirmed.confidence = msg.confidence
                confirmed.label = msg.label
                
                # Check if this is a duplicate of an existing target in queue
                is_duplicate = False
                for existing in self.target_queue:
                    dx = abs(existing.x - confirmed.x)
                    dy = abs(existing.y - confirmed.y)
                    if dx < STABILITY_THRESHOLD and dy < STABILITY_THRESHOLD:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    self.target_queue.append(confirmed)
                    self.get_logger().info(
                        f"Queued target: ({confirmed.x:.3f}, {confirmed.y:.3f}) "
                        f"Confidence: {confirmed.confidence:.2f}"
                    )
                    # Disable further detection until this object is processed
                    self.allow_detection = False
                
                self.buffer_queue.clear()

    def _control_loop(self):
        # Handle pending action completion
        if self.pending_action:
            future = self.pending_action["future"]
            if future.done():
                try:
                    result = future.result()
                    self.state = self.pending_action["next_state"]
                    self.get_logger().info(
                        f"Completed: {self.pending_action['description']} -> {self.state}"
                    )
                except Exception as e:
                    self.get_logger().error(
                        f"Action '{self.pending_action['description']}' failed: {e}"
                    )
                    self._reset_cycle()
                self.pending_action = None
            return

        # Handle gripper timer delays
        if self.gripper_timer is not None:
            elapsed = time.time() - self.gripper_timer
            if elapsed >= self.gripper_target_state["delay"]:
                self.state = self.gripper_target_state["next_state"]
                self.gripper_timer = None
                self.gripper_target_state = None
            return

        # State machine
        if self.state == "idle":
            self._load_next_target()
        elif self.state == "approach_pick":
            self._send_set_tool(
                self.active_target.x,
                self.active_target.y,
                self.pick_hover_z,
                "descend_pick",
            )
        elif self.state == "descend_pick":
            pick_z = self.active_target.z if self.active_target.z > 0 else self.default_pick_depth
            self._send_set_tool(
                self.active_target.x,
                self.active_target.y,
                pick_z,
                "close_gripper",
            )
        elif self.state == "close_gripper":
            self._send_set_gripper_with_delay(self.grip_closed, "lift_after_pick", self.gripper_close_delay)
        elif self.state == "lift_after_pick":
            self._send_set_tool(
                self.active_target.x,
                self.active_target.y,
                self.pick_hover_z,
                "move_to_drop_hover",
            )
        elif self.state == "move_to_drop_hover":
            self._send_set_tool(
                self.drop_pose[0],
                self.drop_pose[1],
                self.drop_hover_z,
                "descend_drop",
            )
        elif self.state == "descend_drop":
            self._send_set_tool(
                self.drop_pose[0],
                self.drop_pose[1],
                self.drop_pose[2],
                "open_gripper",
            )
        elif self.state == "open_gripper":
            self._send_set_gripper_with_delay(self.grip_open, "lift_after_drop", self.gripper_open_delay)
        elif self.state == "lift_after_drop":
            self._send_set_tool(
                self.drop_pose[0],
                self.drop_pose[1],
                self.drop_hover_z,
                "return_home",
            )
        elif self.state == "return_home":
            self._send_home("idle")

    def _send_set_gripper_with_delay(self, value, next_state, delay):
        """Send gripper command and wait for specified delay before proceeding"""
        req = SetGripper.Request()
        req.value = float(value)
        future = self.set_gripper_client.call_async(req)
        
        gripper_state = "CLOSING" if value == self.grip_closed else "OPENING"
        self.get_logger().info(f"Gripper {gripper_state} to value: {value:.2f}, waiting {delay:.1f}s")
        
        # Store the future but don't wait for completion - use timer instead
        self.gripper_timer = time.time()
        self.gripper_target_state = {
            "next_state": next_state,
            "delay": delay
        }

    def _load_next_target(self):
        if self.target_queue:
            msg = self.target_queue.popleft()
            self.active_target = msg
            self.drop_pose = self._choose_drop_pose(msg.label)
            self.state = "approach_pick"
            self.get_logger().info(
                f"Processing target ({msg.x:.3f}, {msg.y:.3f}, {msg.z:.3f}) -> drop zone '{self._label_to_zone(msg.label)}'"
            )
        else:
            # No targets in queue, re-enable detection
            self.allow_detection = True

    def _choose_drop_pose(self, label):
        zone_name = self._label_to_zone(label)
        zone = DROP_ZONES[zone_name]
        # Use fixed positions instead of random for consistency
        x = (zone["x_min"] + zone["x_max"]) / 2.0  # Center of zone
        y = (zone["y_min"] + zone["y_max"]) / 2.0  # Center of zone
        z = zone["z"]
        self.get_logger().info(f"Drop pose for {zone_name}: ({x:.3f}, {y:.3f}, {z:.3f})")
        return (x, y, z)

    def _label_to_zone(self, label):
        key = (label or "").strip().lower()
        return key if key in DROP_ZONES else DEFAULT_DROP

    def _send_set_tool(self, x, y, z, next_state):
        req = SetTool.Request()
        req.x = float(x)
        req.y = float(y)
        req.z = float(z)
        req.theta_x, req.theta_y, req.theta_z = self.tool_rotation
        future = self.set_tool_client.call_async(req)
        self.pending_action = {
            "future": future,
            "next_state": next_state,
            "description": f"set_tool({x:.3f}, {y:.3f}, {z:.3f})",
        }
        self.get_logger().info(f"Moving to: ({x:.3f}, {y:.3f}, {z:.3f})")

    def _send_set_gripper(self, value, next_state):
        req = SetGripper.Request()
        req.value = float(value)
        future = self.set_gripper_client.call_async(req)
        
        gripper_state = "CLOSING" if value == self.grip_closed else "OPENING"
        self.get_logger().info(f"Gripper {gripper_state} to value: {value:.2f}")
        
        self.pending_action = {
            "future": future,
            "next_state": next_state,
            "description": f"set_gripper({value:.2f})",
        }

    def _send_home(self, next_state):
        req = Status.Request()
        future = self.home_client.call_async(req)
        self.pending_action = {
            "future": future,
            "next_state": next_state,
            "description": "home()",
        }

    def _blocking_home(self):
        req = Status.Request()
        future = self.home_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if future.result() is None:
            self.get_logger().warn("Home service call timed out, but continuing...")
        else:
            self.get_logger().info("Home command acknowledged")

    def _blocking_set_gripper(self, value):
        """Blocking call to set gripper position during initialization"""
        req = SetGripper.Request()
        req.value = float(value)
        future = self.set_gripper_client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=self.gripper_timeout)
        if future.result() is None:
            self.get_logger().error(f"Gripper initialization to {value} failed!")
        else:
            state = "OPEN" if value == self.grip_open else "CLOSED"
            self.get_logger().info(f"Gripper initialized to {state} position")

    def _reset_cycle(self):
        self.get_logger().warn("Resetting pick/place cycle due to error")
        
        # Try to open gripper for safety
        try:
            self._blocking_set_gripper(self.grip_open)
        except:
            self.get_logger().error("Failed to open gripper during reset")
        
        self.pending_action = None
        self.active_target = None
        self.drop_pose = None
        self.state = "idle"
        self.buffer_queue.clear()
        self.allow_detection = True  # Re-enable detection after reset


def main(args=None):
    rclpy.init(args=args)
    node = PickPlaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
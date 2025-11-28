import random
import time
from collections import deque

import rclpy
from rclpy.node import Node

from kinova_gen3_interfaces.msg import SourceTarget
from kinova_gen3_interfaces.srv import SetGripper, SetTool, Status
from sensor_msgs.msg import JointState

DROP_ZONES = {
    "recycle": {"x_min": 0.35, "x_max": 0.45, "y_min": 0.05, "y_max": 0.15, "z": 0.15},
    "compost": {"x_min": 0.35, "x_max": 0.45, "y_min": 0.35, "y_max": 0.45, "z": 0.15},
}
DEFAULT_DROP = "recycle"


class PickPlaceNode(Node):
    def __init__(self):
        super().__init__("greenarm_pickplace")

        self.declare_parameter("confidence_threshold", 0.2)
        self.declare_parameter("queue_size", 5)
        self.declare_parameter("pickup_hover_z", 0.15)
        self.declare_parameter("drop_hover_z", 0.15)
        self.declare_parameter("default_pick_depth", 0.0)
        self.declare_parameter("grip_closed", 1.0)
        self.declare_parameter("grip_open", 0.0)
        self.declare_parameter("stability_samples", 5)
        self.declare_parameter("gripper_timeout", 5.0)
        self.declare_parameter("gripper_close_delay", 2.0)
        self.declare_parameter("gripper_open_delay", 2.0)
        
        # Haptic feedback parameters
        self.declare_parameter("max_gripper_close_attempts", 3)
        self.declare_parameter("initial_grip_strength", 0.7)
        self.declare_parameter("gripper_empty_threshold", 0.1)  # New parameter

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
        
        # Haptic feedback parameters
        self.max_gripper_close_attempts = int(self.get_parameter("max_gripper_close_attempts").value)
        self.initial_grip_strength = float(self.get_parameter("initial_grip_strength").value)
        self.gripper_empty_threshold = float(self.get_parameter("gripper_empty_threshold").value)
        
        self.tool_rotation = (180.0, 0.0, 180.0)

        self.target_queue = deque(maxlen=max(1, self.queue_size))
        self.active_target = None
        self.drop_pose = None
        self.pending_action = None
        self.state = "idle"
        self.allow_detection = True
        
        # Improved stability buffer
        self.buffer_queue = deque(maxlen=self.stability_samples)
        self.last_target_time = self.get_clock().now()
        self.target_timeout = 2.0

        # Timer for gripper delays
        self.gripper_timer = None
        self.gripper_target_state = None

        # Haptic feedback state
        self.gripper_close_attempts = 0
        self.last_gripper_position = 0.0
        self.last_gripper_current = 0.0
        self.current_grip_strength = self.initial_grip_strength
        
        # Gripper status tracking
        self.gripper_joint_name = None
        self.gripper_status_received = False
        self.gripper_position_at_close = None  # Track gripper position when closing

        self.set_tool_client = self.create_client(SetTool, "/set_tool")
        self.set_gripper_client = self.create_client(SetGripper, "/set_gripper")
        self.home_client = self.create_client(Status, "/home")

        for name, client in (("set_tool", self.set_tool_client),
                             ("set_gripper", self.set_gripper_client),
                             ("home", self.home_client)):
            while not client.wait_for_service(timeout_sec=1.0):
                self.get_logger().info(f"Waiting for {name} service...")

        # Subscribe to gripper status for haptic feedback
        self.gripper_sub = self.create_subscription(
            JointState,
            "/joint_states",
            self._gripper_status_callback,
            10
        )

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

    def _gripper_status_callback(self, msg):
        """Callback for gripper status updates from JointState"""
        # If we haven't identified the gripper joint yet, try to find it
        if self.gripper_joint_name is None:
            gripper_joint_names = [
                "robotiq_85_left_knuckle_joint", "finger_joint", 
                "gripper_finger1_joint", "gripper_finger2_joint",
                "left_inner_finger_joint", "right_inner_finger_joint",
                "robotiq_85_right_knuckle_joint", "robotiq_85_left_finger_joint",
                "robotiq_85_right_finger_joint"
            ]
            
            for i, name in enumerate(msg.name):
                if any(gripper_name in name for gripper_name in gripper_joint_names):
                    self.gripper_joint_name = name
                    self.get_logger().info(f"Found gripper joint: {name}")
                    break
        
        # If we know the gripper joint name, get its data
        if self.gripper_joint_name and self.gripper_joint_name in msg.name:
            idx = msg.name.index(self.gripper_joint_name)
            if idx < len(msg.position):
                self.last_gripper_position = msg.position[idx]
            if idx < len(msg.effort):
                self.last_gripper_current = msg.effort[idx]
            self.gripper_status_received = True

    def _check_pickup_success(self):
        """Check if gripper actually grabbed something by comparing position"""
        if self.gripper_position_at_close is None:
            self.get_logger().warn("No gripper position recorded at close time")
            return False
            
        # If gripper position is very close to fully closed (near 0), nothing was grabbed
        if self.last_gripper_position <= self.gripper_empty_threshold:
            self.get_logger().warn(f"Gripper empty - position: {self.last_gripper_position:.3f} <= threshold: {self.gripper_empty_threshold}")
            return False
            
        # Gripper has something - position should be significantly > 0
        self.get_logger().info(f"Gripper has object - position: {self.last_gripper_position:.3f}")
        return True

    def _attempt_pickup(self):
        """Try to pick up object"""
        if self.gripper_close_attempts >= self.max_gripper_close_attempts:
            self.get_logger().warn("Max pickup attempts reached, assuming failure")
            return "pickup_failed"
        
        # Open gripper first before retry attempt (except first attempt)
        if self.gripper_close_attempts > 0:
            self.get_logger().info("Opening gripper before retry attempt")
            self._send_set_gripper_with_delay(
                self.grip_open, 
                "prepare_retry_pickup", 
                self.gripper_open_delay
            )
            return "opening_for_retry"
        else:
            # First attempt - just close the gripper
            grip_strength = self.initial_grip_strength + (self.gripper_close_attempts * 0.2)
            grip_strength = min(grip_strength, self.grip_closed)
            self.current_grip_strength = grip_strength
            
            self.get_logger().info(
                f"Pickup attempt {self.gripper_close_attempts + 1}/"
                f"{self.max_gripper_close_attempts} with grip strength: {grip_strength:.2f}"
            )
            
            # Record current gripper position before closing
            self.gripper_position_at_close = self.last_gripper_position
            self.get_logger().info(f"Gripper position before close: {self.gripper_position_at_close:.3f}")
            
            self._send_set_gripper_with_delay(
                grip_strength, 
                "check_pickup_result", 
                self.gripper_close_delay
            )
            self.gripper_close_attempts += 1
            return "closing_gripper"

    def _target_callback(self, msg):
        if not self.allow_detection or self.state != "idle":
            return

        if msg.confidence < self.confidence_threshold:
            return

        current_time = self.get_clock().now()
        new_point = (msg.x, msg.y, msg.z, current_time)

        if self.buffer_queue:
            time_since_last = (current_time - self.last_target_time).nanoseconds / 1e9
            if time_since_last > self.target_timeout:
                self.buffer_queue.clear()

        self.buffer_queue.append(new_point)
        self.last_target_time = current_time

        if len(self.buffer_queue) >= self.stability_samples:
            xs = [p[0] for p in self.buffer_queue]
            ys = [p[1] for p in self.buffer_queue]
            
            avg_x = sum(xs) / len(xs)
            avg_y = sum(ys) / len(ys)
            
            max_deviation_x = max(abs(x - avg_x) for x in xs)
            max_deviation_y = max(abs(y - avg_y) for y in ys)
            
            STABILITY_THRESHOLD = 0.01
            
            if max_deviation_x <= STABILITY_THRESHOLD and max_deviation_y <= STABILITY_THRESHOLD:
                confirmed = SourceTarget()
                confirmed.x = avg_x
                confirmed.y = avg_y
                confirmed.z = msg.z
                confirmed.confidence = msg.confidence
                confirmed.label = msg.label
                
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
                "descend_to_pick",
            )
        elif self.state == "descend_to_pick":
            pick_z = self.active_target.z if self.active_target.z > 0 else self.default_pick_depth
            self._send_set_tool(
                self.active_target.x,
                self.active_target.y,
                pick_z,
                "close_gripper",
            )
        elif self.state == "close_gripper":
            self.gripper_close_attempts = 0
            self.current_grip_strength = self.initial_grip_strength
            self.gripper_position_at_close = None
            next_state = self._attempt_pickup()
            self.state = next_state
            
        elif self.state == "opening_for_retry":
            pass
            
        elif self.state == "prepare_retry_pickup":
            # After opening gripper, return home and get new pose estimation
            self.get_logger().info("Returning home to clear camera view for new pose estimation")
            self._send_home("reposition_for_retry")
            
        elif self.state == "reposition_for_retry":
            # After homing, allow detection and wait for new target
            self.get_logger().info("Waiting for new pose estimation after repositioning")
            self.allow_detection = True
            self.state = "waiting_for_retry_target"
            
        elif self.state == "waiting_for_retry_target":
            # Wait for new target detection
            if self.active_target and len(self.target_queue) > 0:
                # Use the latest target from queue
                self.active_target = self.target_queue[-1]
                self.get_logger().info(f"New target position: ({self.active_target.x:.3f}, {self.active_target.y:.3f})")
                self.state = "approach_pick"
            else:
                # Keep waiting for target
                pass
            
        elif self.state == "closing_gripper":
            pass
            
        elif self.state == "check_pickup_result":
            # Actually check if gripper grabbed something
            if self._check_pickup_success():
                self.get_logger().info("Pickup successful - proceeding with operation")
                self.state = "lift_after_pick"
            else:
                self.get_logger().warn("Pickup failed - gripper is empty")
                next_state = self._attempt_pickup()
                self.state = next_state
                
        elif self.state == "pickup_failed":
            self.get_logger().error("Failed to pick up object after multiple attempts")
            self._send_set_gripper_with_delay(
                self.grip_open, 
                "return_home_after_failure", 
                self.gripper_open_delay
            )
            
        elif self.state == "return_home_after_failure":
            self._send_set_tool(
                self.active_target.x,
                self.active_target.y,
                self.pick_hover_z,
                "reset_after_failure",
            )
            
        elif self.state == "reset_after_failure":
            self._send_home("idle")
            self.active_target = None
            self.drop_pose = None
            self.allow_detection = True
            
        elif self.state == "lift_after_pick":
            self._send_set_tool(
                self.active_target.x,
                self.active_target.y,
                self.pick_hover_z,
                "move_to_drop_approach",
            )
        elif self.state == "move_to_drop_approach":
            self._send_set_tool(
                self.drop_pose[0],
                self.drop_pose[1],
                self.drop_hover_z,
                "descend_to_drop",
            )
        elif self.state == "descend_to_drop":
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
        
        self.get_logger().info(f"Gripper command to value: {value:.2f}, waiting {delay:.1f}s")
        
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
            self.allow_detection = True

    def _choose_drop_pose(self, label):
        zone_name = self._label_to_zone(label)
        zone = DROP_ZONES[zone_name]
        x = (zone["x_min"] + zone["x_max"]) / 2.0
        y = (zone["y_min"] + zone["y_max"]) / 2.0
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
        self.get_logger().info(f"Moving to: ({x:.3f}, {y:.3f}, {z:.3f}) -> {next_state}")

    def _send_set_gripper(self, value, next_state):
        req = SetGripper.Request()
        req.value = float(value)
        future = self.set_gripper_client.call_async(req)
        
        self.get_logger().info(f"Gripper command to value: {value:.2f}")
        
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
        try:
            self._blocking_set_gripper(self.grip_open)
        except:
            self.get_logger().error("Failed to open gripper during reset")
        
        self.pending_action = None
        self.active_target = None
        self.drop_pose = None
        self.state = "idle"
        self.buffer_queue.clear()
        self.allow_detection = True
        self.gripper_close_attempts = 0
        self.current_grip_strength = self.initial_grip_strength
        self.gripper_position_at_close = None


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
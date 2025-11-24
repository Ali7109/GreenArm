import random
from collections import deque

import rclpy
from rclpy.node import Node

from greenarm_perception.msg import SourceTarget
from kinova_gen3_interfaces.srv import SetGripper, SetTool, Status

# Drop rectangles (meters) in Kinova base frame.
DROP_ZONES = {
    "recycle": {"x_min": 0.2, "x_max": 0.5, "y_min": 0.0, "y_max": 0.2, "z": 0.02},
    "compost": {"x_min": 0.2, "x_max": 0.5, "y_min": 0.3, "y_max": 0.5, "z": 0.02},
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

        self.confidence_threshold = float(self.get_parameter("confidence_threshold").value)
        self.queue_size = int(self.get_parameter("queue_size").value)
        self.pick_hover_z = float(self.get_parameter("pickup_hover_z").value)
        self.drop_hover_z = float(self.get_parameter("drop_hover_z").value)
        self.default_pick_depth = float(self.get_parameter("default_pick_depth").value)
        self.grip_closed = float(self.get_parameter("grip_closed").value)
        self.grip_open = float(self.get_parameter("grip_open").value)
        self.tool_rotation = (180.0, 0.0, 180.0)

        self.target_queue = deque(maxlen=max(1, self.queue_size))
        self.active_target = None
        self.drop_pose = None
        self.pending_action = None  # {"future": Future, "next_state": str, "description": str}
        self.state = "idle"

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

        self.target_sub = self.create_subscription(
            SourceTarget, "/source_zone/pick_target", self._target_callback, 10
        )
        self.timer = self.create_timer(0.1, self._control_loop)

    # ------------------------------------------------------------------ Callbacks
    def _target_callback(self, msg: SourceTarget):
        if msg.confidence < self.confidence_threshold:
            return
        self.get_logger().info(
            f"Queueing target ({msg.x:.3f}, {msg.y:.3f}, {msg.z:.3f}) label='{msg.label}' conf={msg.confidence:.2f}"
        )
        self.target_queue.append(msg)

    def _control_loop(self):
        if self.pending_action:
            future = self.pending_action["future"]
            if future.done():
                if future.exception() is not None:
                    self.get_logger().error(
                        f"Action '{self.pending_action['description']}' failed: {future.exception()}"
                    )
                    self._reset_cycle()
                else:
                    self.state = self.pending_action["next_state"]
                self.pending_action = None
            return

        if self.state == "idle":
            self._load_next_target()
            return

        if self.state == "approach_pick":
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
            self._send_set_gripper(self.grip_closed, "lift_after_pick")
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
            self._send_set_gripper(self.grip_open, "lift_after_drop")
        elif self.state == "lift_after_drop":
            self._send_set_tool(
                self.drop_pose[0],
                self.drop_pose[1],
                self.drop_hover_z,
                "return_home",
            )
        elif self.state == "return_home":
            self._send_home("idle")
            self.active_target = None
            self.drop_pose = None

    # ------------------------------------------------------------------ Helpers
    def _load_next_target(self):
        while self.target_queue:
            msg = self.target_queue.popleft()
            if msg.confidence < self.confidence_threshold:
                continue
            self.active_target = msg
            self.drop_pose = self._choose_drop_pose(msg.label)
            self.state = "approach_pick"
            self.get_logger().info(
                f"Processing target ({msg.x:.3f}, {msg.y:.3f}, {msg.z:.3f}) -> drop zone '{self._label_to_zone(msg.label)}'"
            )
            return
        self.state = "idle"

    def _choose_drop_pose(self, label):
        zone_name = self._label_to_zone(label)
        zone = DROP_ZONES[zone_name]
        x = random.uniform(zone["x_min"], zone["x_max"])
        y = random.uniform(zone["y_min"], zone["y_max"])
        z = zone["z"]
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

    def _send_set_gripper(self, value, next_state):
        req = SetGripper.Request()
        req.value = float(value)
        future = self.set_gripper_client.call_async(req)
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
        rclpy.spin_until_future_complete(self, future)
        if future.result() is None:
            raise RuntimeError("Failed to home robot during startup")
        self.get_logger().info("Home command acknowledged")

    def _reset_cycle(self):
        self.pending_action = None
        self.active_target = None
        self.drop_pose = None
        self.state = "idle"


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


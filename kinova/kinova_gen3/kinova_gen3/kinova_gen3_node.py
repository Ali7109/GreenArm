#
# This is an absolutely minimal ros2 wrapper around some demo code for the Kinova arm.
# Absolutely no apologies for what is happening here. Including the terrible hack in the
# utilities code included. This could all be made much prettier, etc.
#
from kinova_gen3_interfaces.srv import Status, SetGripper, GetGripper, SetJoints, GetJoints, GetTool, SetTool
import rclpy
from rclpy.node import Node

import sys
import os
import time
import threading

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient
from kortex_api.autogen.messages import Base_pb2, BaseCyclic_pb2, Common_pb2

from kinova_gen3.utilities import parseConnectionArguments, DeviceConnection

# Maximum allowed waiting time during actions (in seconds)
TIMEOUT_DURATION = 20

# Create closure to set an event after an END or an ABORT
def check_for_end_or_abort(e):
    """Return a closure checking for END or ABORT notifications

    Arguments:
    e -- event to signal when the action is completed
        (will be set when an END or ABORT occurs)
    """
    def check(notification, e = e):
        print("EVENT : " + \
              Base_pb2.ActionEvent.Name(notification.action_event))
        if notification.action_event == Base_pb2.ACTION_END \
        or notification.action_event == Base_pb2.ACTION_ABORT:
            e.set()
    return check


def example_move_to_home_position(base):
    # Make sure the arm is in Single Level Servoing mode
    base_servo_mode = Base_pb2.ServoingModeInformation()
    base_servo_mode.servoing_mode = Base_pb2.SINGLE_LEVEL_SERVOING
    base.SetServoingMode(base_servo_mode)

    # Move arm to ready position
    print("Moving the arm to a safe position")
    action_type = Base_pb2.RequestedActionType()
    action_type.action_type = Base_pb2.REACH_JOINT_ANGLES
    action_list = base.ReadAllActions(action_type)
    action_handle = None
    for action in action_list.action_list:
        if action.name == "Home":
            action_handle = action.handle

    if action_handle == None:
        print("Can't reach safe position. Exiting")
        return False

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    base.ExecuteActionFromReference(action_handle)
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Safe position reached")
    else:
        print("Timeout on action notification wait")
    return finished

def set_gripper(base, position):
    gripper_command = Base_pb2.GripperCommand()
    finger = gripper_command.gripper.finger.add()

    # Close the gripper with position increments
    print("Performing gripper test in position...")
    gripper_command.mode = Base_pb2.GRIPPER_POSITION
    finger.value = position
    print(f"Going to position {position}")
    base.SendGripperCommand(gripper_command)


def get_gripper(base):
    gripper_request = Base_pb2.GripperRequest()
    gripper_request.mode = Base_pb2.GRIPPER_POSITION
    gripper_measure = base.GetMeasuredGripperMovement(gripper_request)
    if len (gripper_measure.finger):
        print(f"Current position is : {gripper_measure.finger[0].value}")
        return gripper_measure.finger[0].value
    return None

def example_angular_action_movement(base, angles=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0]):

    print("Starting angular action movement ...")
    action = Base_pb2.Action()
    action.name = "Example angular action movement"
    action.application_data = ""

    actuator_count = base.GetActuatorCount()

    # Place arm straight up
    print(actuator_count.count)
    if actuator_count.count != len(angles):
        print(f"bad lengths {actuator_count.count} {len(angles)}")
    for joint_id in range(actuator_count.count):
        joint_angle = action.reach_joint_angles.joint_angles.joint_angles.add()
        joint_angle.joint_identifier = joint_id
        joint_angle.value = angles[joint_id]

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    print("Executing action")
    base.ExecuteAction(action)

    print("Waiting for movement to finish ...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    if finished:
        print("Angular movement completed")
    else:
        print("Timeout on action notification wait")
    return finished

def get_angular_state(base_cyclic):
    feedback = base_cyclic.RefreshFeedback()
    actuators = feedback.actuators
    v = []
    for j in actuators:
        v.append(j.position)
    return v

def example_cartesian_action_movement(base, x, y, z, theta_x, theta_y, theta_z):

    print("Starting Cartesian action movement ...")
    action = Base_pb2.Action()
    action.name = "Example Cartesian action movement"
    action.application_data = ""

    cartesian_pose = action.reach_pose.target_pose
    cartesian_pose.x = x
    cartesian_pose.y = y
    cartesian_pose.z = z
    cartesian_pose.theta_x = theta_x
    cartesian_pose.theta_y = theta_y
    cartesian_pose.theta_z = theta_z

    e = threading.Event()
    notification_handle = base.OnNotificationActionTopic(
        check_for_end_or_abort(e),
        Base_pb2.NotificationOptions()
    )

    print("Executing action")
    base.ExecuteAction(action)

    print("Waiting for movement to finish ...")
    finished = e.wait(TIMEOUT_DURATION)
    base.Unsubscribe(notification_handle)

    return finished

def get_tool_state(base_cyclic):
    feedback = base_cyclic.RefreshFeedback()
    base = feedback.base

    return  base.tool_pose_x, base.tool_pose_y, base.tool_pose_z, base.tool_pose_theta_x, base.tool_pose_theta_y, base.tool_pose_theta_z


class Kinova_Gen3_Interface(Node):

    def __init__(self):
        super().__init__('kinova_gen3_interface')
        self.get_logger().info(f'{self.get_name()} created')

        self.create_service(Status, "home", self._handle_home)
        self.create_service(GetGripper, "get_gripper", self._handle_get_gripper)
        self.create_service(SetGripper, "set_gripper", self._handle_set_gripper)
        self.create_service(SetJoints, "set_joints", self._handle_set_joints)
        self.create_service(GetJoints, "get_joints", self._handle_get_joints)
        self.create_service(SetTool, "set_tool", self._handle_set_tool)
        self.create_service(GetTool, "get_tool", self._handle_get_tool)

        args = parseConnectionArguments()
        with DeviceConnection.createTcpConnection(args) as router:
            self._router = router
            self._base = BaseClient(self._router)
            self._base_cyclic = BaseCyclicClient(self._router)

    def _handle_home(self, request, response):
        """Move to home"""
        self.get_logger().info(f'{self.get_name()} moving to home')

        response.status = example_move_to_home_position(self._base)
        return response

    def _handle_get_gripper(self, request, response):
        """Get gripper value"""
        self.get_logger().info(f'{self.get_name()} Getting gripper value')

        response.value = get_gripper(self._base)
        return response

    def _handle_set_gripper(self, request, response):
        """Set gripper value"""
        self.get_logger().info(f'{self.get_name()} Setting gripper value')

        set_gripper(self._base, request.value)
        response.status = True
        return response

    def _handle_set_joints(self, request, response):
        """Set joint values"""
        self.get_logger().info(f'{self.get_name()} Setting joint values')
        if len(request.joints) != 6:
            self.get_logger().info(f'{self.get_name()} Must specify exactly six joint angles')
            response.status = False
            return response

        response.status = example_angular_action_movement(self._base, angles=request.joints)
        return response

    def _handle_get_joints(self, request, response):
        """Get joint values"""
        self.get_logger().info(f'{self.get_name()} Getting joint values')
        response.joints = get_angular_state(self._base_cyclic)
        return response


    def _handle_set_tool(self, request, response):
        """Set tool values"""
        self.get_logger().info(f'{self.get_name()} Setting tool values')

        response.status = example_cartesian_action_movement(self._base, request.x, request.y, request.z, request.theta_x, request.theta_y, request.theta_z)
        return response

    def _handle_get_tool(self, request, response):
        """Get tool values"""
        self.get_logger().info(f'{self.get_name()} Getting tool values')
        x, y, z, theta_x, theta_y, theta_z = get_tool_state(self._base_cyclic)
        response.x = x
        response.y = y
        response.z = z
        response.theta_x = theta_x
        response.theta_y = theta_y
        response.theta_z = theta_z
        return response

def main(args=None):
    rclpy.init(args=args)
    try:
        node = Kinova_Gen3_Interface()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()

if __name__ == '__main__':
    main()



from kinova_gen3_interfaces.srv import Status, SetGripper, GetGripper, SetTool, GetTool
import rclpy
from rclpy.node import Node
import time
import random

#Zones
PICKUP_ZONE = {"x_min":0.2, "x_max":0.5, "y_min":0.0, "y_max":-0.3, "z":0.01}
DROP_ZONES = {
    "recycle": {"x_min":0.2, "x_max":0.5, "y_min":0.0, "y_max":0.2, "z":0.02},
     "compost": {"x_min":0.2, "x_max":0.5, "y_min":0.3, "y_max":0.5, "z":0.02},
}

def do_home(node, home):
    z = Status.Request()
    future = home.call_async(z)
    rclpy.spin_until_future_complete(node, future)
    print(f"Home returns {future.result()}")
    return future.result().status

def do_set_gripper(node, set_gripper, v):
    """Set the gripper"""
    z = SetGripper.Request()
    z.value = v
    future = set_gripper.call_async(z)
    rclpy.spin_until_future_complete(node, future)
    print(f"SetGripper returns {future.result()}")
    return future.result().status

def do_get_gripper(node, get_gripper):
    """Get the current gripper setting"""
    z = GetGripper.Request()
    future = get_gripper.call_async(z)
    rclpy.spin_until_future_complete(node, future)
    print(f"GetGripper returns {future.result()}")
    return future.result().value

def do_get_tool(node, get_tool):
    z = GetTool.Request()
    future = get_tool.call_async(z)
    rclpy.spin_until_future_complete(node, future)
    print(f"GetTool returns {future.result()}")
    q = future.result()
    return q.x, q.y, q.z, q.theta_x, q.theta_y, q.theta_z

def do_set_tool(node, set_tool, x, y, z, theta_x, theta_y, theta_z):
    t = SetTool.Request()
    t.x = float(x)
    t.y = float(y)
    t.z = float(z)
    t.theta_x = float(theta_x)
    t.theta_y = float(theta_y)
    t.theta_z = float(theta_z)
    print(f"Request built {t}")
    future = set_tool.call_async(t)
    rclpy.spin_until_future_complete(node, future)
    print(f"SetTool returns {future.result()}")
    return future.result().status

def do_pickup():
    """Right now hardcoded/fixed coordinates (within the pickup zone), Later Camera will determine this"""
    x = float(input(f"Enter pickup X ({PICKUP_ZONE['x_min']} to {PICKUP_ZONE['x_max']}): "))
    y = float(input(f"Enter pickup Y ({PICKUP_ZONE['y_min']} to {PICKUP_ZONE['y_max']}): "))
    z = PICKUP_ZONE["z"]
    return (x, y, z)

def do_drop():
    """For now taking user input for deciding drop-off zone, later classification algo will decide this"""
    while True:
        zone = input("Enter drop zone (recycle/compost): ").lower()
        if zone in DROP_ZONES:
            dz = DROP_ZONES[zone]
            # pick a random point within the drop zone rectangle
            x = random.uniform(dz["x_min"], dz["x_max"])
            y = random.uniform(dz["y_min"], dz["y_max"])
            z = dz["z"]
            return (x, y, z)
        else:
            print("Invalid zone. Please enter black, blue, or green.")

def main():
    rclpy.init(args=None)
    node = Node('pick_and_place')

    # Create service clients
    services = {
        "get_tool": node.create_client(GetTool, "/get_tool"),
        "set_tool": node.create_client(SetTool, "/set_tool"),
        "set_gripper": node.create_client(SetGripper, "/set_gripper"),
        "get_gripper": node.create_client(GetGripper, "/get_gripper"),
        "home": node.create_client(Status, "/home"),
    }

    # Always start from home
    do_home(node, services["home"])
    time.sleep(2)
   
    src = do_pickup()
    dest = do_drop()
    rotation = (180.0, 0.0, 180.0)

    node.get_logger().info(f"Moving to pickup-zonee at {src}")
    do_set_gripper(node, services["set_gripper"], 0.0)  # open gripper
    time.sleep(2)

    # Move to pickup and get low
    do_set_tool(node, services["set_tool"], *src, *rotation)
    time.sleep(2)

    # Close gripper to grab block
    do_set_gripper(node, services["set_gripper"], 1.0)
    time.sleep(2)

    # Lift slightly
    lifted = (src[0], src[1], src[2])
    do_set_tool(node, services["set_tool"], *lifted, *rotation)
    time.sleep(2)

    # Move to drop zone
    node.get_logger().info(f"Moving to drop zone at {dest}")
    do_set_tool(node, services["set_tool"], *dest, *rotation)
    time.sleep(2)

    # Open gripper to release
    do_set_gripper(node, services["set_gripper"], 0.0)
    time.sleep(2)
   
    # Finish it by going to the  home position
    do_home(node, services["home"])    
    node.get_logger().info(" Robot has returned to home.")

    rclpy.shutdown()
if __name__ == '__main__':
    main()
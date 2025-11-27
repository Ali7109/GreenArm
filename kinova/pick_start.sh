#!/bin/bash
set -e

# Source ROS2 installation (change for your distro)
source /opt/ros/humble/setup.bash

# Build
colcon build

# Source *your* workspace
source install/setup.bash

# Run the node
exec ros2 run greenarm_manipulation pick_node

#!/bin/bash
set -e

# Source ROS2 installation (change for your distro)
source /opt/ros/humble/setup.bash

# Go to your workspace
cd ~/your_ws  # change this

# Build
colcon build

# Source *your* workspace
source install/setup.bash

# Run the node
exec ros2 run kinova_gen3 kinova_gen3_node

# 📁 GreenArm Directory Structure

## Overview

This document provides a comprehensive overview of the GreenArm project directory structure, clarifying the relationship between the `kinova/` directory and other components.

## Answer to "Do you see the kinova directory and the sibling GreenArm directory?"

**Yes, the `kinova/` directory exists at the root level of the repository.**

However, there is **no sibling "GreenArm" directory**. The repository itself IS the GreenArm project. What exists instead is:
- The `kinova/` directory (contains Kinova-specific ROS2 packages)
- The `src/green_arm/` directory (contains the main GreenArm application)

Both are **subdirectories within the GreenArm repository**, not siblings.

## Complete Directory Tree

```
GreenArm/                                    # Root repository directory
│
├── kinova/                                  # Kinova robot integration packages
│   ├── greenarm_manipulation/               # ROS2 package for manipulation
│   │   ├── greenarm_manipulation/           # Python module
│   │   │   ├── __init__.py
│   │   │   └── pickplace_node.py           # Pick and place logic
│   │   ├── package.xml                      # ROS2 package manifest
│   │   ├── setup.py                         # Python package setup
│   │   ├── setup.cfg                        # Setup configuration
│   │   └── resource/
│   │       └── greenarm_manipulation
│   │
│   └── greenarm_perception/                 # ROS2 package for perception
│       ├── greenarm_perception/             # Python module
│       │   ├── __init__.py
│       │   └── source_detector.py          # Object detection logic
│       ├── msg/                             # Custom ROS2 messages
│       │   └── SourceTarget.msg            # Source/target message definition
│       ├── CMakeLists.txt                   # CMake build configuration
│       ├── package.xml                      # ROS2 package manifest
│       ├── setup.py                         # Python package setup
│       ├── setup.cfg                        # Setup configuration
│       └── resource/
│           └── greenarm_perception
│
├── src/                                     # Source code directory
│   └── green_arm/                           # Main GreenArm ROS2 package
│       ├── green_arm/                       # Python module
│       │   ├── __init__.py
│       │   ├── opencv_camera.py            # OpenCV camera interface
│       │   ├── view_camera.py              # Camera viewing utilities
│       │   ├── yolo_pose.py                # YOLO pose estimation
│       │   └── yolo_pose_object_detect.py  # YOLO object detection
│       ├── launch/                          # ROS2 launch files
│       │   └── view-camera-robot.launch.py # Camera and robot launch
│       ├── urdf/                            # Robot model descriptions
│       │   ├── colors.xacro                # Color definitions
│       │   └── scout-camera.urdf.xacro     # Robot URDF model
│       ├── test/                            # Unit tests
│       │   ├── test_copyright.py
│       │   ├── test_flake8.py
│       │   └── test_pep257.py
│       ├── package.xml                      # ROS2 package manifest
│       ├── setup.py                         # Python package setup
│       ├── setup.cfg                        # Setup configuration
│       ├── resource/
│       │   └── green_arm
│       └── LICENSE
│
├── model/                                   # Machine learning models
│   ├── prediction/                          # Inference models
│   └── training/                            # Training scripts and data
│
├── Hardware/                                # Hardware specifications
│   └── WebCam/                              # Camera hardware documentation
│
├── requirements.txt                         # Python dependencies
├── install_req.bash                         # Installation script
├── README.md                                # Project README
└── .gitignore                               # Git ignore rules

```

## Directory Descriptions

### 🤖 `kinova/` - Kinova Robot Integration

This directory contains ROS2 packages specifically designed for integration with the Kinova robotic arm:

- **`greenarm_manipulation/`**: Handles robotic manipulation tasks
  - Implements pick-and-place operations
  - Controls arm movements and gripper actions
  - Node: `pickplace_node.py`

- **`greenarm_perception/`**: Manages perception and object detection
  - Detects source objects and targets
  - Publishes detection results using custom `SourceTarget` messages
  - Node: `source_detector.py`

### 📦 `src/green_arm/` - Main Application Package

The primary ROS2 package containing the core GreenArm functionality:

- **Core Modules** (`green_arm/`):
  - `opencv_camera.py`: Camera interface using OpenCV
  - `view_camera.py`: Camera visualization utilities
  - `yolo_pose.py`: Human pose estimation using YOLO
  - `yolo_pose_object_detect.py`: Object detection using YOLO

- **Launch Files** (`launch/`):
  - Contains ROS2 launch configurations for starting the system

- **Robot Models** (`urdf/`):
  - URDF/Xacro files defining the robot's physical structure
  - Used for visualization and simulation

- **Tests** (`test/`):
  - Automated tests for code quality (flake8, pep257)
  - Copyright verification

### 🧠 `model/` - Machine Learning

Contains machine learning models and related scripts:

- `prediction/`: Trained models for inference
- `training/`: Scripts and data for model training

### 🔧 `Hardware/` - Hardware Documentation

Documentation and specifications for hardware components:

- `WebCam/`: Camera-related files and specifications

## Key Files

- **`requirements.txt`**: Lists all Python package dependencies
- **`install_req.bash`**: Automated installation script
- **`README.md`**: Main project documentation and overview
- **`.gitignore`**: Specifies files/folders to exclude from version control

## Naming Convention

Note the naming variations used throughout the project:

- **`GreenArm`**: Repository name (CamelCase)
- **`green_arm`**: Main package directory (snake_case)
- **`greenarm_manipulation`** & **`greenarm_perception`**: Kinova package names (lowercase)

This follows ROS2 conventions where package names typically use lowercase with underscores.

## Relationship Clarification

```
Repository: Ali7109/GreenArm
    │
    ├─── kinova/              (Kinova-specific integration)
    │    ├─── greenarm_manipulation/
    │    └─── greenarm_perception/
    │
    └─── src/green_arm/       (Main application - also "GreenArm" functionality)
```

Both `kinova/` and `src/green_arm/` are **subdirectories** within the GreenArm repository, working together to provide the complete system functionality.

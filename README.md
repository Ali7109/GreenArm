# 🌿 **GreenArm**

### 🧠 Course  
**EECS 4421 / EECS 5324 – Project**

---

### 👥 **Team Members**

| Name | Student ID |
|------|-------------|
| Khawaja Faiza Qaisar | 217948233 |
| Ali Hassan Amin | 217713215 |
| Omkumar Miteshbhai Patel | 222110936 |
| Thi Thanh Thuy Nguyen | 219914175 |
| Michael Murphy | 222636120 |

---

### 📁 **Directory Structure**

> **Quick Answer**: Yes, the `kinova/` directory exists at the root level of this repository!  
> For detailed structure information, see [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)

```
GreenArm/
├── kinova/                          # Kinova robot-specific ROS2 packages
│   ├── greenarm_manipulation/       # Manipulation control (pick & place)
│   └── greenarm_perception/         # Perception and object detection
├── src/
│   └── green_arm/                   # Main GreenArm ROS2 package
│       ├── green_arm/               # Core modules (camera, YOLO detection)
│       ├── launch/                  # ROS2 launch files
│       ├── urdf/                    # Robot model descriptions
│       └── test/                    # Unit tests
├── model/                           # ML models
│   ├── prediction/                  # Trained models for inference
│   └── training/                    # Training scripts and data
├── Hardware/                        # Hardware specifications
│   └── WebCam/                      # Camera-related files
├── requirements.txt                 # Python dependencies
└── install_req.bash                 # Installation script
```

**Key Directories:**
- **`kinova/`**: Contains ROS2 packages for Kinova robotic arm integration
  - `greenarm_manipulation`: Pick and place operations
  - `greenarm_perception`: Source detection and targeting
- **`src/green_arm/`**: Main application package with vision and control modules
- **`model/`**: Machine learning models for object detection and pose estimation
- **`Hardware/`**: Hardware documentation and configuration

---

### 📄 **Documentation**

You can view the full project documentation on Google Docs:  
🔗 [**Project Documentation**](https://docs.google.com/document/d/1UfCLxOMtsfqIm9XTnhB-UJ_cXhZuPkduEq30G5uH_Ag/edit?tab=t.0)


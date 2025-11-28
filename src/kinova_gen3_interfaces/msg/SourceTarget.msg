# Timestamp of the observation (we can fill header stamp with node time)
std_msgs/Header header

# Target pose in Kinova's source-zone frame (meters)
float32 x
float32 y
float32 z

# Confidence in [0,1]; 0 means "no target currently".
float32 confidence

# Optional semantic label (e.g., recycle/compost/tissue)
string label

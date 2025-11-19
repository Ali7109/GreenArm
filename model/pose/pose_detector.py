import cv2
import torch
import numpy as np
from ultralytics import YOLO

############################################
# CONFIG
############################################
IMAGE_PATH = "2.jpg"  # <-- put your image here

# Force CPU for MiDaS (more stable on Mac M-chip)
YOLO_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
MIDAS_DEVICE = "cpu"  # MiDaS works better on CPU for Mac

# Camera intrinsics (approx. for standard webcams — adjust later if needed)
fx = 800
fy = 800
cx0 = 640
cy0 = 360

# Depth calibration scale (you'll tune these later)
a = 0.45
b = 0.02

############################################
# LOAD MODELS
############################################
print("Loading YOLO model...")
detector = YOLO("yolov8s.pt")
if YOLO_DEVICE == "mps":
    print("Using MPS for YOLO")

print("Loading MiDaS model...")
# Use DPT_Hybrid on CPU
midas = torch.hub.load("intel-isl/MiDaS", "DPT_Hybrid", trust_repo=True)
midas.to(MIDAS_DEVICE)
midas.eval()

# Get the correct transform for DPT_Hybrid
midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms", trust_repo=True)
transform = midas_transforms.dpt_transform

print(f"MiDaS running on: {MIDAS_DEVICE}")

############################################
# LOAD IMAGE
############################################
img = cv2.imread(IMAGE_PATH)
if img is None:
    raise FileNotFoundError(f"Could not load image at {IMAGE_PATH}")

h, w = img.shape[:2]
print(f"Loaded image: {w}x{h}")

# Convert BGR to RGB for MiDaS
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

############################################
# RUN YOLO DETECTION
############################################
print("Running YOLO detection...")
results = detector(img, device=YOLO_DEVICE)

if len(results[0].boxes) == 0:
    raise RuntimeError("No objects detected!")

box = results[0].boxes[0]  # first detected object
u, v, bw, bh = box.xywh[0].tolist()
u = int(u)
v = int(v)
class_id = int(box.cls[0])
class_name = results[0].names[class_id]

print(f"Detected: {class_name}")
print(f"Object center at pixel = ({u}, {v})")

############################################
# RUN MiDaS DEPTH ESTIMATION
############################################
print("Running MiDaS depth estimation...")

# Transform image
input_batch = transform(img_rgb).to(MIDAS_DEVICE)

# Run depth estimation
with torch.no_grad():
    depth_predict = midas(input_batch)
    
    # Resize to original image size
    depth_predict = torch.nn.functional.interpolate(
        depth_predict.unsqueeze(1),
        size=img_rgb.shape[:2],
        mode="bicubic",
        align_corners=False,
    ).squeeze()

depth_map = depth_predict.cpu().numpy()

# Get depth at object center
Z_pseudo = depth_map[v, u]
Z = a * Z_pseudo + b  # calibrated depth estimate

print(f"Pseudo-depth at object: {Z_pseudo:.4f}")
print(f"Calibrated depth: {Z:.4f}")

############################################
# BACKPROJECT 2D PIXEL → 3D COORDINATE
############################################
X = (u - cx0) * Z / fx
Y = (v - cy0) * Z / fy

print("\n====================================")
print("3D POSITION IN CAMERA FRAME")
print("====================================")
print(f"Object: {class_name}")
print(f"X = {X:.4f} m")
print(f"Y = {Y:.4f} m")
print(f"Z = {Z:.4f} m (depth)")
print("====================================\n")

############################################
# VISUALIZATION
############################################
print("Drawing bounding box and center...")

# Get bounding box coordinates
x1 = int(box.xyxy[0][0])
y1 = int(box.xyxy[0][1])
x2 = int(box.xyxy[0][2])
y2 = int(box.xyxy[0][3])

# Draw on original image
cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
cv2.circle(img, (u, v), 5, (0, 0, 255), -1)
cv2.putText(img, f"{class_name}", (x1, y1 - 25),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
cv2.putText(img, f"Depth: {Z:.2f}m", (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

# Normalize depth map for visualization
depth_normalized = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
depth_colored = cv2.applyColorMap(depth_normalized.astype(np.uint8), cv2.COLORMAP_MAGMA)

# Show results
cv2.imshow("Detection + Depth", img)
cv2.imshow("Depth Map", depth_colored)
print("Press any key to close windows...")
cv2.waitKey(0)
cv2.destroyAllWindows()

print("\nDone!")
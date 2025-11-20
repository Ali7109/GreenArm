import cv2
import numpy as np

# --- Camera / marker configuration -----------------------------------------
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_LENGTH_M = 0.05          # physical marker edge length (meters)
MIN_RED_AREA_PX = 400           # ignore tiny blobs/noise

# Inner corner for each ID (OpenCV order: TL, TR, BR, BL)
# Coordinates are exactly what you want the Kinova frame to read (meters).
PHYSICAL_MARKERS = {
    0: {"coord": (0.2, 0.0), "inner": 3},   # top-right -> bottom-left corner
    1: {"coord": (0.50, 0.0), "inner": 0},   # bottom-right -> top-left corner
    2: {"coord": (0.2, -0.30), "inner": 2}, # top-left -> bottom-right corner
    3: {"coord": (0.5, - 0.30), "inner": 1}, # bottom-left -> top-right corner
}

camera_matrix = np.array(
    [[1.62926289e3, 0.0, 9.71234776e2],
     [0.0, 1.62748788e3, 5.30839748e2],
     [0.0, 0.0, 1.0]], dtype=np.float32)
dist_coeffs = np.array(
    [0.595836256, -7.01481761, -0.00206565224, 0.0000525532496, 24.2404007],
    dtype=np.float32)

# --- Helper functions -------------------------------------------------------
def estimate_marker_pixel_size(corner_quad):
    p = corner_quad.astype(np.float32)
    return (
        np.linalg.norm(p[1] - p[0]) +
        np.linalg.norm(p[2] - p[1]) +
        np.linalg.norm(p[3] - p[2]) +
        np.linalg.norm(p[0] - p[3])
    ) / 4.0

def build_workspace_transform(corners, ids):
    if ids is None:
        return None
    src_pts, dst_pts = [], []
    flat_ids = ids.flatten()
    for marker_id, spec in PHYSICAL_MARKERS.items():
        matches = np.where(flat_ids == marker_id)[0]
        if matches.size == 0:
            return None
        idx = matches[0]
        src_pts.append(corners[idx][0][spec["inner"]])
        dst_pts.append(spec["coord"])
    return cv2.getPerspectiveTransform(
        np.float32(src_pts),
        np.float32(dst_pts)
    )

def project_point(px, py, transform):
    pts = np.array([[[px, py]]], dtype=np.float32)
    return cv2.perspectiveTransform(pts, transform)[0][0]

# --- Video loop -------------------------------------------------------------
aruco_dict = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
parameters = cv2.aruco.DetectorParameters_create()
cap = cv2.VideoCapture("/dev/video4") #1--webcam , 0--laptop camera
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

print("Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    px_per_meter = None
    workspace_transform = None

    if ids is not None and len(ids) > 0:
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
            corners, MARKER_LENGTH_M, camera_matrix, dist_coeffs
        )
        mpx = estimate_marker_pixel_size(corners[0][0])
        px_per_meter = (MPX := mpx) and (MPX / MARKER_LENGTH_M)  # pixels per meter

        for i, marker_id in enumerate(ids.flatten()):
            pos = tvecs[i][0]
            anchor = tuple(corners[i][0][0].astype(int))
            cv2.putText(frame, f"id {marker_id}: X {pos[0]:.2f}  Y {pos[1]:.2f}",
                        anchor, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

        workspace_transform = build_workspace_transform(corners, ids)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
    mask |= cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        if cv2.contourArea(cnt) < MIN_RED_AREA_PX:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w // 2, y + h // 2

        if px_per_meter:
            block_w = w / px_per_meter
            block_h = h / px_per_meter
            cv2.putText(frame, f"Block {block_w:.2f}m x {block_h:.2f}m",
                        (x, max(15, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                        (255, 255, 0), 1)

        if workspace_transform is not None:
            wx, wy = project_point(cx, cy, workspace_transform)
            cv2.putText(frame, f"Kinova ({wx:.3f}, {wy:.3f}) m",
                        (x, y + h + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 200, 255), 2)

    cv2.imshow("Kinova workspace view", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

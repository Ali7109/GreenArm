import cv2
import numpy as np

aruco_dict_type = cv2.aruco.DICT_4X4_50
marker_length_m = 0.05   # each marker = 5 cm in real world
min_red_area_px = 500    # filter tiny red noise
# Use 0.25 for the inner work envelope or change to 0.30 to cover the outer square
workspace_side_m = 0.25
# Marker layout: ids 0-3 placed TL, TR, BL, BR on the printed board
workspace_marker_order = [0, 1, 2, 3]
marker_inner_corner = {
    0: 2,  # top-left marker -> kinova's bottom-left(0.3,0.5)
    1: 3,  # top-right marker -> bottom-left (0,0.5)
    2: 1,  # bottom-left marker -> top-right (0.3,0.2)
    3: 0,  # bottom-right marker -> top-left (0,0.2)
}

#Our Source zone for Kinova Arm:
kinova_min_x = 0.0
kinova_max_x = 0.3
kinova_min_y = 0.2
kinova_max_y = 0.5

# dictionary and detector
aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)
parameters = cv2.aruco.DetectorParameters_create()


# --- Camera setup ---
cap = cv2.VideoCapture("/dev/video4")  # change index if needed (1, 2, ...)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

# --- Calibration (replace with your actual calibration for accurate pose) ---
#camera_matrix = np.array([[800, 0, 320],
 #                         [0, 800, 240],
  #                        [0, 0, 1]], dtype=np.float32)
#dist_coeffs = np.zeros((5,1))



camera_matrix = np.array([[1.62926289e+03, 0.00000000e+00, 9.71234776e+02],[0.00000000e+00, 1.62748788e+03, 5.30839748e+02], [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]], dtype=np.float32)
dist_coeffs = np.array([0.595836256, -7.01481761, -0.00206565224, 0.0000525532496, 24.2404007], dtype=np.float32)

def estimate_marker_pixel_size(corner_quad):
    p = corner_quad.astype(np.float32)
    # side lengths in pixels
    s01 = np.linalg.norm(p[1] - p[0])
    s12 = np.linalg.norm(p[2] - p[1])
    s23 = np.linalg.norm(p[3] - p[2])
    s30 = np.linalg.norm(p[0] - p[3])
    return (s01 + s12 + s23 + s30) / 4.0

#Transforming function from image to workspace coordinates
def build_workspace_transform(marker_corners, marker_ids):
    if marker_ids is None:
        return None

    ordered_points = []
    found = 0
    for expected_id in workspace_marker_order:
        matches = np.where(marker_ids.flatten() == expected_id)[0]
        if matches.size == 0:
            break
        idx = matches[0]
        ordered_points.append(
            marker_corners[idx][0][marker_inner_corner[expected_id]]
        )
        found += 1

    if found != 4:
        return None

    image_pts = np.float32(ordered_points)
    workspace_pts = np.float32([
        [0.0, workspace_side_m],             # top-left
        [workspace_side_m, workspace_side_m],# top-right
        [0.0, 0.0],                          # bottom-left
        [workspace_side_m, 0.0],             # bottom-right
    ])
    return cv2.getPerspectiveTransform(image_pts, workspace_pts)

def workspace_to_source_zone(wx, wy):
    x = np.clip(wx / workspace_side_m, 0.0, 1.0)
    y = np.clip(wy / workspace_side_m, 0.0, 1.0)
    sx = kinova_min_x + x * (kinova_max_x - kinova_min_x)
    sy = kinova_min_y + y * (kinova_max_y - kinova_min_y)
    return sx, sy

print("Press 'q' to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=parameters)

    # Dynamic pixel->meter scale from any detected marker
    px_per_meter = None
    workspace_transform = None
    if ids is not None and len(ids) > 0:
        # Draw markers
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        # Pose (optional; keep if you want axes, else skip)
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_length_m, camera_matrix, dist_coeffs)

        # Use the first marker to compute pixel scale
        mpx = estimate_marker_pixel_size(corners[0][0])
        # meters per pixel
        m_per_px = marker_length_m / mpx
        px_per_meter = 1.0 / m_per_px

        # Overlay ID and 2D position (X,Y) in meters from pose
        for i, marker_id in enumerate(ids.flatten()):
            pos = tvecs[i][0]  # [x, y, z] meters in camera coords
            corner_text_anchor = tuple(corners[i][0][0].astype(int))
            text = f"ID:{marker_id} X:{pos[0]:.2f}, Y:{pos[1]:.2f} m"
            cv2.putText(frame, text, corner_text_anchor, cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0,255,0), 1)

            # Project center and endpoints 0.05 m along X and Y
            center, _ = cv2.projectPoints(np.array([[0,0,0]], dtype=np.float32),
                                          rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
            x_axis, _ = cv2.projectPoints(np.array([[0.05,0,0]], dtype=np.float32),
                                          rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
            y_axis, _ = cv2.projectPoints(np.array([[0,0.05,0]], dtype=np.float32),
                                          rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
            c = tuple(center[0].ravel().astype(int))
            xa = tuple(x_axis[0].ravel().astype(int))
            ya = tuple(y_axis[0].ravel().astype(int))
            cv2.line(frame, c, xa, (255,0,0), 2)  # blue X
            cv2.line(frame, c, ya, (255,0,0), 2)  # blue Y

        workspace_transform = build_workspace_transform(corners, ids)

    # --- Red block detection (physical object) ---
    # Tune HSV thresholds to your lighting
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # morphologica/structural cleanup
    kernel = np.ones((3,3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_red_area_px:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w//2, y + h//2

        # Convert pixel dimensions/centroid to meters using dynamic scale
        if px_per_meter is not None:
            m_per_px = 1.0 / px_per_meter
            block_width_m = w * m_per_px
            block_height_m = h * m_per_px
            cx_m = cx * m_per_px
            cy_m = cy * m_per_px

            # Overlay only text (no bounding box)
            cv2.putText(frame, f"Block {block_width_m:.2f}m x {block_height_m:.2f}m",
                        (x, y - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,0,0), 1)
            cv2.putText(frame, f"Center: ({cx_m:.2f}, {cy_m:.2f}) m",
                        (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,0,0), 1)

            if workspace_transform is not None:
                workspace_pt = cv2.perspectiveTransform(
                    np.array([[[cx, cy]]], dtype=np.float32),
                    workspace_transform
                )[0][0]
                wx, wy = workspace_pt
                kinova_x, kinova_y = workspace_to_source_zone(wx, wy)

                cv2.putText(frame, f"Workspace ({wx:.3f}, {wy:.3f}) m", (x, y + h + 15), cv2.FONT_HERSHEY_SIMPLEX,0.3, (0, 255, 255), 2 )
                cv2.putText(frame, f"Kinova ({kinova_x:.3f}, {kinova_y:.3f}) m",
                            (x, y + h + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 165, 255), 2)
        else:
            cv2.putText(frame, f"Block px: {w} x {h} | Center px: ({cx},{cy})",
                        (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 0), 2)

    # cv2.imshow("ArUco + Red Block (meters, live)", frame)
    cv2.namedWindow("ArUco Grid Preview", cv2.WINDOW_NORMAL)   # allow resizing
    preview_size = (600, 600)  # shrink for display
    preview_img = cv2.resize(frame, preview_size, interpolation=cv2.INTER_AREA)

    cv2.imshow("ArUco Grid Preview", preview_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
#preview_size = (1000, 1000)  # shrink for display
#preview_img = cv2.resize(frame, preview_size, interpolation=cv2.INTER_AREA)

#cv2.imshow("ArUco + Object Detection with Distances", preview_img)
#cv2.waitKey(0)
#cv2.destroyAllWindows()


# cv2.namedWindow("ArUco Grid Preview", cv2.WINDOW_NORMAL)   # allow resizing
# preview_size = (400, 400)  # shrink for display
# preview_img = cv2.resize(frame, preview_size, interpolation=cv2.INTER_AREA)

# cv2.imshow("ArUco Grid Preview", preview_img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

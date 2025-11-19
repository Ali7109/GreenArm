import cv2
import numpy as np
import glob
import json

# --- Checkerboard parameters ---
chessboard_size = (7, 9)   # inner corners per row/column (columns, rows)
square_size_m = 0.02        # 2 cm squares in meters

# --- Image folder ---
image_glob = "calibration_images/*.png"  # change to your folder path/pattern

# --- Corner detection flags ---
flags = cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK

# Prepare object points (3D points in real world space)
objp = np.zeros((chessboard_size[0]*chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size_m

objpoints = []  # 3D points
imgpoints = []  # 2D points
used_images = []

images = glob.glob(image_glob)
if len(images) == 0:
    raise RuntimeError("No images found. Check your image_glob path.")

img_size = None

for fname in images:
    img = cv2.imread(fname)
    if img is None:
        continue
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, flags)
    if ret:
        # Refine corner locations
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        corners_subpix = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        objpoints.append(objp)
        imgpoints.append(corners_subpix)
        used_images.append(fname)
        img_size = gray.shape[::-1]  # (width, height)

print(f"Detected corners in {len(used_images)} images out of {len(images)}.")

if len(used_images) < 8:
    print("⚠️ Warning: fewer than 8 valid images. Calibration may be noisy; add more varied angles.")

# --- Run calibration ---
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, img_size, None, None
)

# --- Compute reprojection error ---
total_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], camera_matrix, dist_coeffs)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    total_error += error
mean_error = total_error / len(objpoints)

print("\n=== Calibration Results ===")
print("Camera matrix:\n", camera_matrix)
print("Distortion coefficients:\n", dist_coeffs.ravel())
print(f"Mean reprojection error: {mean_error:.4f} pixels")

# --- Save results ---
results = {
    "camera_matrix": camera_matrix.tolist(),
    "dist_coeffs": dist_coeffs.ravel().tolist(),
    "image_size": {"width": img_size[0], "height": img_size[1]},
    "square_size_m": square_size_m,
    "chessboard_size": {"cols": chessboard_size[0], "rows": chessboard_size[1]},
    "mean_reprojection_error_px": float(mean_error),
    "used_images": used_images,
}
with open("calibration_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\n✅ Saved calibration_results.json")


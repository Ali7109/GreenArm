import cv2
import numpy as np


def cm_to_px(length_cm: float, dpi: int) -> int:
    """Convert centimeters to pixels for the provided printer DPI."""
    cm_per_inch = 2.54
    return int(round((length_cm / cm_per_inch) * dpi))


# --- Physical layout parameters ---
dpi = 300
marker_size_cm = 5.0  # 2.5 cm radius markers
box_detection_cm = 30.0  # ROS/OpenCV will detect a 30x30 cm square
inner_space_cm = box_detection_cm - marker_size_cm  # 25 cm workspace between inner edges
aruco_dict_type = cv2.aruco.DICT_4X4_50
marker_ids = [0, 1, 2, 3]
corner_layout_file = "aruco_corner_layout.png"

# --- Derived pixel sizes ---
marker_size_px = cm_to_px(marker_size_cm, dpi)
box_detection_px = cm_to_px(box_detection_cm, dpi)

# --- Load dictionary ---
aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)

# --- Prepare blank canvas for the corner layout ---
canvas = np.ones((box_detection_px, box_detection_px, 3), dtype=np.uint8) * 255

# Coordinates (x, y) for four corners: TL, TR, BL, BR
corner_offsets = [
    (0, 0),
    (box_detection_px - marker_size_px, 0),
    (0, box_detection_px - marker_size_px),
    (box_detection_px - marker_size_px, box_detection_px - marker_size_px),
]

# --- Generate 4 markers and position them on the canvas ---
for marker_id, (offset_x, offset_y) in zip(marker_ids, corner_offsets):
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
    marker_img_color = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)

    # Save individual marker for stand-alone printing if desired
    filename = f"aruco_marker_{marker_id}.png"
    cv2.imwrite(filename, marker_img_color)
    print(f"Saved marker ID {marker_id} to {filename}")

    canvas[offset_y:offset_y + marker_size_px, offset_x:offset_x + marker_size_px] = marker_img_color

# --- Save the final 30x30 cm corner layout ---
cv2.imwrite(corner_layout_file, canvas)
print(
    f"Corner layout saved to {corner_layout_file} "
    f"(outer square {box_detection_cm} cm, inner workspace {inner_space_cm} cm)"
)


# #old Code
# import cv2
# import numpy as np

# # --- Parameters ---
# #grid_size = 3               # 3x3 grid
# #marker_size_px = 400        # each marker size in pixels
# #padding_px = 10 # thin spacing between markers
# #aruco_dict_type = cv2.aruco.DICT_4X4_50
# #output_file = "aruco_grid_spaced.png"


# # --- Parameters ---
# marker_size_cm = 5
# dpi = 300
# cm_per_inch = 2.54
# marker_size_px = int((marker_size_cm / cm_per_inch) * dpi)  # ~591 px
# padding_px = 10
# aruco_dict_type = cv2.aruco.DICT_4X4_50


# # --- Load dictionary ---
# aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)


# # --- Generate and save each marker individually ---
# for marker_id in range(9):
#     marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
#     marker_img = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)

#     # Add thin white padding
#     padded = cv2.copyMakeBorder(marker_img, padding_px, padding_px, padding_px, padding_px,
#                                 cv2.BORDER_CONSTANT, value=(255, 255, 255))

#     # Save each marker as its own file
#     filename = f"aruco_marker_{marker_id}.png"
#     cv2.imwrite(filename, padded)
#     print(f"Saved marker ID {marker_id} to {filename}")



# # --- Generate individual markers (IDs 0–8) with padding ---
# #marker_imgs = []
# #for marker_id in range(grid_size * grid_size):
#   #  marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
#     # Convert to color so padding is visible
#     #marker_img = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
#     # Add thin white padding
#     #padded = cv2.copyMakeBorder(marker_img, padding_px, padding_px, padding_px, padding_px,
#     #                            cv2.BORDER_CONSTANT, value=(255, 255, 255))
#     #marker_imgs.append(padded)

# # --- Arrange markers in a grid ---
# #rows = [np.hstack(marker_imgs[i*grid_size:(i+1)*grid_size]) for i in range(grid_size)]
# #grid_img = np.vstack(rows)

# # --- Save the full grid ---
# #cv2.imwrite(output_file, grid_img)
# #print(f"Generated spaced grid image: {output_file}")



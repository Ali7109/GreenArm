import cv2
import numpy as np

# --- Parameters ---
#grid_size = 3               # 3x3 grid
#marker_size_px = 400        # each marker size in pixels
#padding_px = 10 # thin spacing between markers
#aruco_dict_type = cv2.aruco.DICT_4X4_50
#output_file = "aruco_grid_spaced.png"



# --- Parameters ---
marker_size_cm = 5
dpi = 300
cm_per_inch = 2.54
marker_size_px = int((marker_size_cm / cm_per_inch) * dpi)  # ~591 px
padding_px = 10
aruco_dict_type = cv2.aruco.DICT_4X4_50


# --- Load dictionary ---
aruco_dict = cv2.aruco.getPredefinedDictionary(aruco_dict_type)















# --- Generate and save each marker individually ---
for marker_id in range(9):
    marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
    marker_img = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)

    # Add thin white padding
    padded = cv2.copyMakeBorder(marker_img, padding_px, padding_px, padding_px, padding_px,
                                cv2.BORDER_CONSTANT, value=(255, 255, 255))

    # Save each marker as its own file
    filename = f"aruco_marker_{marker_id}.png"
    cv2.imwrite(filename, padded)
    print(f"Saved marker ID {marker_id} to {filename}")
















# --- Generate individual markers (IDs 0–8) with padding ---
#marker_imgs = []
#for marker_id in range(grid_size * grid_size):
  #  marker_img = cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size_px)
    # Convert to color so padding is visible
    #marker_img = cv2.cvtColor(marker_img, cv2.COLOR_GRAY2BGR)
    # Add thin white padding
    #padded = cv2.copyMakeBorder(marker_img, padding_px, padding_px, padding_px, padding_px,
    #                            cv2.BORDER_CONSTANT, value=(255, 255, 255))
    #marker_imgs.append(padded)

# --- Arrange markers in a grid ---
#rows = [np.hstack(marker_imgs[i*grid_size:(i+1)*grid_size]) for i in range(grid_size)]
#grid_img = np.vstack(rows)

# --- Save the full grid ---
#cv2.imwrite(output_file, grid_img)
#print(f"Generated spaced grid image: {output_file}")



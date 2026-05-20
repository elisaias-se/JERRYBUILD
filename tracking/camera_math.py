import math

CAMERA_HORIZONTAL_FOV = 70.42
CAMERA_VERTICAL_FOV = 43.3

FRAME_WIDTH = 640
FRAME_HEIGHT = 360

REAL_HEIGHT_CM = 12.0
DISTANCE_CALIBRATION_FACTOR = 0.8036


def calculate_focal_length_pixels(frame_size_pixels, fov_degrees):
    return frame_size_pixels / (2 * math.tan(math.radians(fov_degrees / 2)))


def calculate_distance_cm(pixel_height):
    if pixel_height <= 0:
        return None

    focal_length_y = calculate_focal_length_pixels(
        FRAME_HEIGHT,
        CAMERA_VERTICAL_FOV
    )

    raw_distance = (REAL_HEIGHT_CM * focal_length_y) / pixel_height
    return raw_distance * DISTANCE_CALIBRATION_FACTOR


def calculate_horizontal_angle(cx, frame_width):
    normalized_x = (cx - frame_width / 2) / (frame_width / 2)
    return normalized_x * (CAMERA_HORIZONTAL_FOV / 2)


def calculate_xy(distance_cm, angle_deg):
    angle_rad = math.radians(angle_deg)

    x_cm = distance_cm * math.sin(angle_rad)
    y_cm = distance_cm * math.cos(angle_rad)

    return x_cm, y_cm
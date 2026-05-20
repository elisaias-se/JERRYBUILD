print("🚀 Starting program...")

from ultralytics import YOLO
import cv2
import time
import math
import platform


# =========================
# Configuration
# =========================

MODEL_PATH = "best.engine"

VALID_CLASSES = ["trash"]

# Logitech C920e camera specs
CAMERA_HORIZONTAL_FOV = 70.42  # degrees
CAMERA_VERTICAL_FOV = 43.3     # degrees

# Keep 16:9 aspect ratio for better camera geometry
FRAME_WIDTH = 640
FRAME_HEIGHT = 360

# Approximate real-world object height
# This only works well if the trash object is close to this height.
REAL_HEIGHT_CM = 12.0

CONFIDENCE_THRESHOLD = 0.5

# Real-world calibration scale factor
DISTANCE_CALIBRATION_FACTOR = 0.8036


# =========================
# Camera / Geometry Helpers
# =========================

def calculate_focal_length_pixels(frame_size_pixels, fov_degrees):
    """
    Calculates focal length in pixels using camera FOV.
    """
    return frame_size_pixels / (2 * math.tan(math.radians(fov_degrees / 2)))


def calculate_horizontal_angle(cx, frame_width, horizontal_fov=CAMERA_HORIZONTAL_FOV):
    """
    Calculates horizontal angle of detected object from camera center.

    Negative angle = object is left of center
    Positive angle = object is right of center
    """
    normalized_x = (cx - frame_width / 2) / (frame_width / 2)
    angle = normalized_x * (horizontal_fov / 2)

    return angle

def calculate_distance_cm(real_height_cm, pixel_height, focal_length_y):
    if pixel_height <= 0:
        return None

    raw_distance = (real_height_cm * focal_length_y) / pixel_height
    calibrated_distance = raw_distance * DISTANCE_CALIBRATION_FACTOR

    return calibrated_distance


def open_camera(camera_index=0):
    """
    Opens camera using the best backend for the current OS.
    """

    current_os = platform.system()

    print(f"Detected OS: {current_os}")

    if current_os == "Windows":
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

    elif current_os == "Linux":
        cap = cv2.VideoCapture(camera_index, cv2.CAP_V4L2)

    else:
        cap = cv2.VideoCapture(camera_index)

    return cap


# =========================
# Main Program
# =========================

print("Loading custom YOLO model...")

model = YOLO(MODEL_PATH, task="detect")

print("Model loaded!")
print("Model classes:", model.names)

focal_length_x = calculate_focal_length_pixels(
    FRAME_WIDTH,
    CAMERA_HORIZONTAL_FOV
)

focal_length_y = calculate_focal_length_pixels(
    FRAME_HEIGHT,
    CAMERA_VERTICAL_FOV
)

print(f"Focal Length X: {focal_length_x:.2f} px")
print(f"Focal Length Y: {focal_length_y:.2f} px")

print("📷 Opening camera...")

cap = open_camera(0)

if not cap.isOpened():
    print("ERROR: Camera failed to open")
    exit()

print("Camera opened successfully")

frame_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to grab frame")
        break

    frame_count += 1

    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    frame_height, frame_width = frame.shape[:2]

    start_time = time.time()

    results = model(
        frame,
        conf=CONFIDENCE_THRESHOLD,
        verbose=False,
        device=0
    )

    end_time = time.time()

    inference_ms = (end_time - start_time) * 1000
    fps = 1000 / inference_ms if inference_ms > 0 else 0

    if frame_count % 30 == 0:
        print(f"Processing frame {frame_count}")
        print(f"Inference: {inference_ms:.2f} ms | FPS: {fps:.2f}")

    detected_any = False

    for box in results[0].boxes:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]
        conf = float(box.conf[0])

        if label not in VALID_CLASSES:
            continue

        detected_any = True

        x1, y1, x2, y2 = box.xyxy[0]

        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)

        pixel_height = float(y2 - y1)

        distance_cm = calculate_distance_cm(
            REAL_HEIGHT_CM,
            pixel_height,
            focal_length_y
        )

        angle_deg = calculate_horizontal_angle(
            cx,
            frame_width
        )

        if distance_cm is None:
            print("Skipping invalid bounding box")
            continue

        print(
            f"{label} at ({cx}, {cy}) | "
            f"Distance: {distance_cm:.2f} cm | "
            f"Angle: {angle_deg:.2f}°"
        )

        cv2.rectangle(
            frame,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            (0, 255, 0),
            2
        )

        cv2.circle(
            frame,
            (cx, cy),
            5,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            f"{label} {conf:.2f} | {distance_cm:.1f} cm | {angle_deg:.1f} deg",
            (int(x1), int(y1) - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

    if not detected_any and frame_count % 30 == 0:
        print("No valid trash detected")

    cv2.imshow("Custom Trash Detection", frame)

    if cv2.waitKey(1) == 27:
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()

print("Program ended cleanly")